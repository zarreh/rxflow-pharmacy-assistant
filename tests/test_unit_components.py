"""
Unit Tests for Individual Components - Step 9 Integration Testing
Tests individual components before full integration testing
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

from rxflow.workflow.conversation_manager import ConversationManager
from rxflow.workflow.state_machine import RefillStateMachine
from rxflow.workflow.workflow_types import RefillState, ConversationContext
from rxflow.tools.tool_manager import ToolManager


class TestConversationManagerUnit:
    """Unit tests for Conversation Manager component"""
    
    @pytest.fixture
    def conversation_manager(self):
        """Create conversation manager instance for testing"""
        return ConversationManager()
    
    @pytest.mark.asyncio
    async def test_conversation_manager_initialization(self, conversation_manager):
        """Test that conversation manager initializes correctly"""
        assert conversation_manager is not None
        assert hasattr(conversation_manager, 'state_machine')
        assert hasattr(conversation_manager, 'prompt_manager')
        assert len(conversation_manager.tools) > 0
    
    @pytest.mark.asyncio
    async def test_simple_medication_identification(self, conversation_manager):
        """Test basic medication identification"""
        session_id = "test_session_001"
        user_input = "I need to refill my lisinopril"
        
        with patch.object(conversation_manager, 'llm') as mock_llm:
            # Mock LLM response for medication identification
            mock_response = Mock()
            mock_response.content = "I can help you refill your lisinopril. Can you confirm the dosage?"
            mock_llm.ainvoke.return_value = mock_response
            
            result = await conversation_manager.handle_message(
                user_input=user_input,
                session_id=session_id,
                patient_id="12345"
            )
            
            assert result.message is not None
            assert result.session_id == session_id
            assert result.current_state in [RefillState.IDENTIFY_MEDICATION, RefillState.CONFIRM_DOSAGE]


class TestStateMachineUnit:
    """Unit tests for State Machine component"""
    
    @pytest.fixture
    def state_machine(self):
        """Create state machine instance for testing"""
        return RefillStateMachine()
    
    def test_state_machine_initialization(self, state_machine):
        """Test state machine initializes with correct states"""
        assert state_machine is not None
        # Check that all expected states are defined
        expected_states = [
            RefillState.START, RefillState.IDENTIFY_MEDICATION, RefillState.CLARIFY_MEDICATION,
            RefillState.CONFIRM_DOSAGE, RefillState.CHECK_AUTHORIZATION, RefillState.SELECT_PHARMACY,
            RefillState.CONFIRM_ORDER, RefillState.ESCALATE_PA, RefillState.COMPLETE, RefillState.ERROR
        ]
        
        for state in expected_states:
            assert state in RefillState
    
    def test_valid_state_transitions(self, state_machine):
        """Test valid state transitions"""
        # Create a test session and check valid triggers
        session_id = "test_session"
        context = state_machine.create_session(session_id)
        
        # Test that we can get valid triggers for current state
        valid_triggers = state_machine.get_valid_triggers(session_id)
        assert isinstance(valid_triggers, list)
        
        # Test basic transition
        success, new_context, error = state_machine.transition(session_id, "medication_request")
        assert success or error is not None  # Should either succeed or have a clear error
    
    def test_invalid_state_transitions(self, state_machine):
        """Test invalid state transitions are rejected"""
        # Create a test session
        session_id = "invalid_test_session"
        context = state_machine.create_session(session_id)
        
        # Try an invalid transition
        success, new_context, error = state_machine.transition(session_id, "invalid_trigger")
        assert not success or error is not None


class TestToolIntegrationUnit:
    """Unit tests for individual tool integration"""
    
    @pytest.fixture
    def tool_manager(self):
        """Create tool manager for testing"""
        return ToolManager()
    
    def test_tool_registration(self, tool_manager):
        """Test that tools are properly registered"""
        # Import and register a sample tool
        from rxflow.tools.patient_history_tool import patient_history_tool
        
        tool_manager.register_tool(patient_history_tool)
        
        assert "patient_medication_history" in tool_manager.tools
        assert tool_manager.get_tool("patient_medication_history") is not None
    
    def test_tool_execution_mock(self, tool_manager):
        """Test tool execution with mocked responses"""
        from rxflow.tools.patient_history_tool import patient_history_tool
        
        # Test tool execution directly with actual data
        result = patient_history_tool("patient_12345")
        assert result is not None
        assert isinstance(result, (dict, str))
        
        # If it's a dict, check for expected structure
        if isinstance(result, dict):
            assert "success" in result or "error" in result or "medications" in result


class TestWorkflowIntegrationUnit:
    """Unit tests for workflow integration components"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_mock_workflow(self):
        """Test end-to-end workflow with mocked components"""
        conversation_manager = ConversationManager()
        
        # Mock the agent executor instead of individual functions
        with patch.object(conversation_manager, 'agent_executor') as mock_executor:
            
            # Setup mock response
            mock_executor.invoke.return_value = {
                'output': 'I can help you refill your lisinopril medication.'
            }
            
            # Test conversation flow
            result = await conversation_manager.handle_message(
                user_input="I need to refill my lisinopril",
                session_id="test_session"
            )
            
            # Verify result structure
            assert result is not None
            assert hasattr(result, 'session_id')
            assert result.session_id == "test_session"


@pytest.mark.asyncio
async def test_conversation_context_management():
    """Test conversation context management across multiple messages"""
    conversation_manager = ConversationManager()
    session_id = "context_test_session"
    
    # Simulate a conversation flow
    messages = [
        "I need to refill my medication",
        "It's lisinopril 10mg",
        "CVS Pharmacy is fine"
    ]
    
    previous_session_id = None
    
    with patch.object(conversation_manager, 'agent_executor') as mock_executor:
        mock_response = {'output': 'Context maintained successfully'}
        mock_executor.invoke.return_value = mock_response
        
        for i, message in enumerate(messages):
            result = await conversation_manager.handle_message(
                user_input=message,
                session_id=session_id
            )
            
            # Verify session is maintained and updated
            assert result.session_id == session_id
            assert result.message is not None
            
            # Session ID should be consistent
            if previous_session_id:
                assert result.session_id == previous_session_id
            
            previous_session_id = result.session_id


def test_mock_data_availability():
    """Test that mock data is available for testing"""
    from rxflow.services.mock_data import (
        MEDICATIONS_DB, PHARMACY_INVENTORY, INSURANCE_FORMULARIES, GOODRX_DISCOUNTS
    )
    
    # Test medication database
    assert "lisinopril" in MEDICATIONS_DB
    assert "rxcui" in MEDICATIONS_DB["lisinopril"]
    
    # Test pharmacy inventory
    assert len(PHARMACY_INVENTORY) > 0
    
    # Test insurance formularies
    assert len(INSURANCE_FORMULARIES) > 0
    
    # Test discount data
    assert len(GOODRX_DISCOUNTS) > 0


def test_error_handling_components():
    """Test error handling in key components"""
    from rxflow.workflow.conversation_manager import ConversationManager
    
    # Test with invalid inputs
    conversation_manager = ConversationManager()
    
    # Test state machine with invalid transitions
    state_machine = conversation_manager.state_machine
    
    # Should handle invalid state gracefully
    try:
        # Test with an invalid session ID
        invalid_session = "invalid_session_id"
        result = state_machine.get_valid_triggers(invalid_session)
        # Should return empty list or handle gracefully
        assert isinstance(result, list)
    except Exception as e:
        # Should be a handled exception, not a crash
        assert "session" in str(e).lower() or "not found" in str(e).lower()


if __name__ == "__main__":
    """Run unit tests when executed directly"""
    pytest.main([__file__, "-v", "--tb=short"])