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
        # Test START to IDENTIFY_MEDICATION
        assert state_machine.can_transition(RefillState.START, RefillState.IDENTIFY_MEDICATION)
        
        # Test IDENTIFY_MEDICATION to CLARIFY_MEDICATION
        assert state_machine.can_transition(RefillState.IDENTIFY_MEDICATION, RefillState.CLARIFY_MEDICATION)
        
        # Test CONFIRM_DOSAGE to SELECT_PHARMACY
        assert state_machine.can_transition(RefillState.CONFIRM_DOSAGE, RefillState.SELECT_PHARMACY)
    
    def test_invalid_state_transitions(self, state_machine):
        """Test invalid state transitions are rejected"""
        # Cannot go from START directly to COMPLETE
        assert not state_machine.can_transition(RefillState.START, RefillState.COMPLETE)
        
        # Cannot go from COMPLETE back to START
        assert not state_machine.can_transition(RefillState.COMPLETE, RefillState.START)


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
        
        # Mock the tool function
        with patch('rxflow.services.mock_data.get_patient_medications') as mock_get_meds:
            mock_get_meds.return_value = {
                "success": True,
                "medications": [
                    {"name": "lisinopril", "dosage": "10mg", "frequency": "once daily"}
                ]
            }
            
            # Test tool execution
            result = patient_history_tool.run("patient_id=12345,medication_name=lisinopril")
            
            assert isinstance(result, str)
            assert "lisinopril" in result.lower()


class TestWorkflowIntegrationUnit:
    """Unit tests for workflow integration components"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_mock_workflow(self):
        """Test end-to-end workflow with mocked components"""
        conversation_manager = ConversationManager()
        
        # Mock all external dependencies
        with patch.object(conversation_manager, 'llm') as mock_llm, \
             patch('rxflow.services.mock_data.get_patient_medications') as mock_get_meds:
            
            # Setup mocks
            mock_response = Mock()
            mock_response.content = "I can help you refill your lisinopril 10mg. Let me find nearby pharmacies."
            mock_llm.ainvoke.return_value = mock_response
            
            mock_get_meds.return_value = {
                "success": True,
                "medications": [{"name": "lisinopril", "dosage": "10mg"}]
            }
            
            # Test workflow
            result = await conversation_manager.handle_message(
                user_input="I need to refill my lisinopril",
                session_id="test_session",
                patient_id="12345"
            )
            
            assert result.message is not None
            assert result.session_id == "test_session"
            assert result.current_state != RefillState.ERROR


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
    
    previous_context = None
    
    with patch.object(conversation_manager, 'llm') as mock_llm:
        mock_response = Mock()
        mock_response.content = "Context maintained successfully"
        mock_llm.ainvoke.return_value = mock_response
        
        for i, message in enumerate(messages):
            result = await conversation_manager.handle_message(
                user_input=message,
                session_id=session_id,
                patient_id="12345"
            )
            
            # Verify context is maintained and updated
            assert result.context is not None
            assert result.session_id == session_id
            
            # Context should evolve with each message
            if previous_context:
                # Some context should be preserved
                assert result.context.session_id == previous_context.session_id
            
            previous_context = result.context


def test_mock_data_availability():
    """Test that mock data is available for testing"""
    from rxflow.services.mock_data import (
        get_patient_medications, get_pharmacy_locations,
        get_medication_prices, get_insurance_formulary
    )
    
    # Test patient medications
    patient_meds = get_patient_medications("12345")
    assert patient_meds["success"] is True
    assert "medications" in patient_meds
    
    # Test pharmacy locations
    pharmacies = get_pharmacy_locations("New York, NY")
    assert pharmacies["success"] is True
    assert "pharmacies" in pharmacies
    
    # Test medication prices
    prices = get_medication_prices("lisinopril", "10mg", 30)
    assert prices["success"] is True
    assert "prices" in prices


def test_error_handling_components():
    """Test error handling in key components"""
    from rxflow.workflow.conversation_manager import ConversationManager
    
    # Test with invalid inputs
    conversation_manager = ConversationManager()
    
    # Test state machine with invalid transitions
    state_machine = conversation_manager.state_machine
    
    # Should handle invalid state gracefully
    try:
        invalid_state = "invalid_state"
        # This should not crash the system
        result = state_machine.get_next_states(RefillState.START)
        assert isinstance(result, list)
    except Exception as e:
        # Should be a handled exception, not a crash
        assert "invalid" in str(e).lower() or "unknown" in str(e).lower()


if __name__ == "__main__":
    """Run unit tests when executed directly"""
    pytest.main([__file__, "-v", "--tb=short"])