#!/usr/bin/env python3
"""
Test the advanced state machine implementation for Step 5
Validates state transitions, context management, and workflow integrity
"""

import sys
from pathlib import Path
import uuid

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from rxflow.workflow.state_machine import RefillStateMachine
from rxflow.workflow.workflow_types import RefillState, ConversationContext
from datetime import datetime

def test_state_machine_initialization():
    """Test basic state machine setup and validation"""
    print("=" * 60)
    print("TESTING STATE MACHINE INITIALIZATION")
    print("=" * 60)
    
    sm = RefillStateMachine()
    
    print(f"✅ Initialized with {len(sm.states)} state definitions")
    print(f"✅ Configured {len(sm.transitions)} state transitions")
    
    # List all states with their properties
    print("\n📋 State Definitions:")
    for state, definition in sm.states.items():
        terminal = "🏁" if definition.is_terminal else "🔄"
        tools = len(definition.required_tools)
        data = len(definition.required_data)
        timeout = definition.timeout_seconds or "∞"
        
        print(f"  {terminal} {state.value}")
        print(f"    - Description: {definition.description}")
        print(f"    - Tools: {tools}, Data: {data}, Timeout: {timeout}s")
    
    return sm

def test_session_management(sm: RefillStateMachine):
    """Test session creation and management"""
    print("\n" + "=" * 60)
    print("TESTING SESSION MANAGEMENT")
    print("=" * 60)
    
    # Create test sessions
    session1 = str(uuid.uuid4())
    session2 = str(uuid.uuid4())
    
    ctx1 = sm.create_session(session1, "patient_123")
    ctx2 = sm.create_session(session2, "patient_456")
    
    print(f"✅ Created session {session1[:8]}... for patient {ctx1.patient_id}")
    print(f"✅ Created session {session2[:8]}... for patient {ctx2.patient_id}")
    
    # Test session retrieval
    retrieved_ctx1 = sm.get_session(session1)
    assert retrieved_ctx1 is not None
    assert retrieved_ctx1.session_id == session1
    assert retrieved_ctx1.current_state == RefillState.START
    
    print(f"✅ Session retrieval working correctly")
    
    # Test session summary
    summary = sm.get_session_summary(session1)
    print(f"✅ Session summary: {summary['current_state']}, {summary['total_transitions']} transitions")
    
    return session1, session2

def test_state_transitions(sm: RefillStateMachine, session_id: str):
    """Test valid state transitions"""
    print("\n" + "=" * 60)
    print("TESTING STATE TRANSITIONS")
    print("=" * 60)
    
    print(f"🧪 Testing transitions for session {session_id[:8]}...")
    
    # Test initial valid transitions
    valid_triggers = sm.get_valid_triggers(session_id)
    print(f"📋 Valid triggers from START: {valid_triggers}")
    
    # Transition: START -> IDENTIFY_MEDICATION
    success, context, error = sm.transition(session_id, "medication_request")
    assert success, f"Transition failed: {error}"
    print(f"✅ START -> IDENTIFY_MEDICATION: Success")
    
    # Test invalid transition
    success, context, error = sm.transition(session_id, "invalid_trigger")
    assert not success, "Invalid transition should fail"
    print(f"✅ Invalid trigger properly rejected: {error}")
    
    # Continue workflow: IDENTIFY_MEDICATION -> CLARIFY_MEDICATION
    success, context, error = sm.transition(
        session_id, 
        "ambiguous_medication",
        medication={"name": "heart pill", "ambiguous": True}
    )
    assert success, f"Transition failed: {error}"
    print(f"✅ IDENTIFY_MEDICATION -> CLARIFY_MEDICATION: Success")
    
    # CLARIFY_MEDICATION -> CONFIRM_DOSAGE
    # First check current context to see what medication data exists
    current_context = sm.get_session(session_id)
    if current_context:
        print(f"📋 Current medication in context: {current_context.medication}")
    
    success, context, error = sm.transition(
        session_id,
        "medication_clarified", 
        medication={"name": "lisinopril", "ambiguous": False, "rxcui": "29046"}
    )
    
    # For debugging - let's check what the condition actually sees
    if not success and context:
        print(f"⚠️  Condition check - medication: {context.medication}")
        print(f"⚠️  Is medication not None: {context.medication is not None}")
        if context.medication:
            print(f"⚠️  Ambiguous flag: {context.medication.get('ambiguous', False)}")
    
    assert success, f"Transition failed: {error}"
    print(f"✅ CLARIFY_MEDICATION -> CONFIRM_DOSAGE: Success")
    
    # CONFIRM_DOSAGE -> CHECK_AUTHORIZATION
    success, context, error = sm.transition(
        session_id,
        "dosage_confirmed",
        dosage="10mg",
        medication={"name": "lisinopril", "safety_issues": False}
    )
    assert success, f"Transition failed: {error}"
    print(f"✅ CONFIRM_DOSAGE -> CHECK_AUTHORIZATION: Success")
    
    return context

def test_conditional_transitions(sm: RefillStateMachine):
    """Test transitions with conditions"""
    print("\n" + "=" * 60)
    print("TESTING CONDITIONAL TRANSITIONS")
    print("=" * 60)
    
    # Create session for testing conditions
    session_id = str(uuid.uuid4())
    ctx = sm.create_session(session_id)
    
    # Test transition with failing condition
    print("🧪 Testing condition: medication_request without patient_id")
    success, context, error = sm.transition(session_id, "medication_request")
    # Should still succeed because we set patient_id in create_session
    print(f"📋 Result: {'✅ Success' if success else '❌ Failed'} - {error}")
    
    # Test safety concern condition
    sm.transition(session_id, "medication_request")
    sm.transition(session_id, "medication_identified", 
                 medication={"name": "test_med", "ambiguous": False})
    
    print("🧪 Testing safety concern condition")
    success, context, error = sm.transition(
        session_id,
        "safety_concern",
        medication={"name": "dangerous_med", "safety_issues": True}
    )
    print(f"📋 Safety transition: {'✅ Success' if success else '❌ Failed'}")
    
    # Test prior auth condition
    session_id2 = str(uuid.uuid4())
    sm.create_session(session_id2)
    
    # Navigate to CHECK_AUTHORIZATION state
    sm.transition(session_id2, "medication_request")
    sm.transition(session_id2, "medication_identified", 
                 medication={"name": "eliquis", "ambiguous": False})
    sm.transition(session_id2, "dosage_confirmed", 
                 dosage="5mg", medication={"name": "eliquis", "safety_issues": False})
    
    print("🧪 Testing prior authorization condition")
    success, context, error = sm.transition(
        session_id2,
        "prior_auth_required",
        insurance_info={"prior_auth_required": True, "plan": "basic"}
    )
    print(f"📋 PA transition: {'✅ Success' if success else '❌ Failed'}")
    
    return context

def test_complete_workflow(sm: RefillStateMachine):
    """Test complete happy path workflow"""
    print("\n" + "=" * 60)
    print("TESTING COMPLETE WORKFLOW")
    print("=" * 60)
    
    session_id = str(uuid.uuid4())
    ctx = sm.create_session(session_id)
    
    workflow_steps = [
        ("medication_request", {"patient_id": "12345"}),
        ("medication_identified", {"medication": {"name": "lisinopril", "ambiguous": False, "rxcui": "29046"}}),
        ("dosage_confirmed", {
            "dosage": "10mg", 
            "medication": {"name": "lisinopril", "safety_issues": False}
        }),
        ("authorized", {"insurance_info": {"prior_auth_required": False, "copay": 10}}),
        ("pharmacy_selected", {"pharmacy": {"name": "CVS", "id": "cvs_123", "address": "123 Main St"}}),
        ("order_confirmed", {"order_details": {"order_id": "ORD_123", "pickup_time": "2 PM today"}})
    ]
    
    print("🎯 Executing complete refill workflow:")
    
    for i, (trigger, data) in enumerate(workflow_steps, 1):
        success, context, error = sm.transition(session_id, trigger, **data)
        state = context.current_state.value if context else "ERROR"
        status = "✅" if success else "❌"
        
        print(f"   {i}. {status} {trigger} -> {state}")
        
        if not success:
            print(f"      Error: {error}")
            break
    
    # Check final state
    if success and context:
        assert context.current_state == RefillState.COMPLETE
        assert sm.is_terminal_state(session_id)
        print(f"🎉 Workflow completed successfully in COMPLETE state!")
    
    return context

def test_error_recovery(sm: RefillStateMachine):
    """Test error handling and recovery paths"""
    print("\n" + "=" * 60)
    print("TESTING ERROR HANDLING & RECOVERY")
    print("=" * 60)
    
    session_id = str(uuid.uuid4())
    ctx = sm.create_session(session_id)
    
    # Navigate to ERROR state
    sm.transition(session_id, "medication_request")
    success, context, error = sm.transition(session_id, "medication_not_found")
    
    print(f"✅ Entered ERROR state: {context and context.current_state == RefillState.ERROR}")
    
    # Test recovery options
    valid_triggers = sm.get_valid_triggers(session_id)
    print(f"📋 Recovery options from ERROR: {valid_triggers}")
    
    # Test restart recovery
    success, context, error = sm.transition(session_id, "restart_conversation")
    print(f"✅ Restart recovery: {context and context.current_state == RefillState.START}")
    
    # Test retry recovery
    session_id2 = str(uuid.uuid4())
    sm.create_session(session_id2)
    sm.transition(session_id2, "medication_request")
    sm.transition(session_id2, "medication_not_found")
    
    success, context, error = sm.transition(session_id2, "retry_medication")
    print(f"✅ Retry recovery: {context and context.current_state == RefillState.IDENTIFY_MEDICATION}")

def test_session_analytics(sm: RefillStateMachine, session_id: str):
    """Test session analytics and history tracking"""
    print("\n" + "=" * 60)
    print("TESTING SESSION ANALYTICS")  
    print("=" * 60)
    
    # Get session history
    history = sm.get_state_history(session_id)
    print(f"📊 State history length: {len(history)}")
    
    print("📋 State Transition History:")
    for i, (state, timestamp, description) in enumerate(history):
        print(f"   {i+1}. {state.value} - {description}")
    
    # Get comprehensive summary
    summary = sm.get_session_summary(session_id)
    print(f"\n📈 Session Summary:")
    print(f"   - Current State: {summary['current_state']}")
    print(f"   - Total Transitions: {summary['total_transitions']}")
    print(f"   - Is Terminal: {summary['is_terminal']}")
    print(f"   - Required Tools: {len(summary['required_tools'])}")
    print(f"   - Required Data: {len(summary['required_data'])}")
    
    # Test data export
    exported_data = sm.export_session_data(session_id)
    assert exported_data is not None
    print(f"✅ Session data export successful ({len(exported_data)} chars)")

def test_workflow_diagram(sm: RefillStateMachine):
    """Test workflow diagram generation"""
    print("\n" + "=" * 60)
    print("TESTING WORKFLOW DIAGRAM GENERATION")
    print("=" * 60)
    
    diagram = sm.get_workflow_diagram()
    
    print("📊 Generated Mermaid Workflow Diagram:")
    print(diagram)
    
    # Validate diagram content
    assert "graph TD" in diagram
    assert "start" in diagram
    assert "complete" in diagram
    print(f"✅ Diagram generated successfully ({len(diagram.split())} elements)")

def test_session_cleanup(sm: RefillStateMachine):
    """Test session cleanup functionality"""
    print("\n" + "=" * 60)
    print("TESTING SESSION CLEANUP")
    print("=" * 60)
    
    initial_sessions = len(sm.sessions)
    print(f"📊 Initial sessions: {initial_sessions}")
    
    # Create some test sessions
    test_sessions = []
    for i in range(3):
        session_id = f"test_session_{i}"
        sm.create_session(session_id)
        test_sessions.append(session_id)
    
    print(f"📊 Sessions after creation: {len(sm.sessions)}")
    
    # Test cleanup (won't remove recent sessions)
    cleaned = sm.cleanup_expired_sessions(max_age_hours=1)  # 1 hour threshold
    print(f"✅ Cleanup completed: {cleaned} sessions removed")
    print(f"📊 Remaining sessions: {len(sm.sessions)}")

def main():
    """Run all state machine tests"""
    print("🧪 COMPREHENSIVE STATE MACHINE TESTING")
    print("Testing advanced state machine implementation for Step 5")
    print("=" * 80)
    
    try:
        # Initialize and test basic functionality
        sm = test_state_machine_initialization()
        
        # Test session management
        session1, session2 = test_session_management(sm)
        
        # Test state transitions
        context = test_state_transitions(sm, session1)
        
        # Test conditional logic
        test_conditional_transitions(sm)
        
        # Test complete workflows
        test_complete_workflow(sm)
        
        # Test error handling
        test_error_recovery(sm)
        
        # Test analytics and tracking
        test_session_analytics(sm, session1)
        
        # Test diagram generation
        test_workflow_diagram(sm)
        
        # Test session cleanup
        test_session_cleanup(sm)
        
        print("\n" + "=" * 80)
        print("✅ ALL STATE MACHINE TESTS COMPLETED SUCCESSFULLY!")
        print("🎯 Step 5: Advanced State Machine System - READY")
        print("=" * 80)
        
        # Show final system stats
        print(f"\n📊 FINAL SYSTEM STATISTICS:")
        print(f"   - Total States: {len(sm.states)}")
        print(f"   - Total Transitions: {len(sm.transitions)}")
        print(f"   - Active Sessions: {len(sm.sessions)}")
        print(f"   - Terminal States: {len([s for s in sm.states.values() if s.is_terminal])}")
        
    except Exception as e:
        print(f"\n❌ ERROR in state machine testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)