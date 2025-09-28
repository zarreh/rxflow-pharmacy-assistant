#!/usr/bin/env python3
"""
Test script to verify the omeprazole confirmation loop fix
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rxflow.workflow.conversation_manager import ConversationManager
from rxflow.llm import get_llm

async def test_omeprazole_conversation():
    """Test the full omeprazole refill conversation flow"""
    print("🧪 Testing Omeprazole Confirmation Loop Fix")
    print("=" * 50)
    
    # Initialize conversation manager
    manager = ConversationManager()
    
    # Start a new session
    session_id = None
    patient_id = "12345"
    
    # Step 1: Initial omeprazole refill request
    print("\n💬 Step 1: User requests omeprazole refill")
    response = await manager.handle_message(
        user_input="I need to refill my omeprazole",
        session_id=session_id,
        patient_id=patient_id
    )
    session_id = response.session_id
    print(f"🤖 AI: {response.message}")
    print(f"📊 State: {response.current_state}")
    
    # Step 2: Select first option (20mg)
    print("\n💬 Step 2: User selects first option")
    response = await manager.handle_message(
        user_input="it is the first option",
        session_id=session_id,
        patient_id=patient_id
    )
    print(f"🤖 AI: {response.message}")
    print(f"📊 State: {response.current_state}")
    
    # Step 3: Confirm medication
    print("\n💬 Step 3: User confirms medication")
    response = await manager.handle_message(
        user_input="yes, i confirm that",
        session_id=session_id,
        patient_id=patient_id
    )
    print(f"🤖 AI: {response.message}")
    print(f"📊 State: {response.current_state}")
    
    # Step 4: Choose closest pharmacy
    print("\n💬 Step 4: User chooses closest pharmacy")
    response = await manager.handle_message(
        user_input="I go with the closest",
        session_id=session_id,
        patient_id=patient_id
    )
    print(f"🤖 AI: {response.message}")
    print(f"📊 State: {response.current_state}")
    
    # Step 5: Final confirmation - this is where it was getting stuck
    print("\n💬 Step 5: User gives final confirmation (this was the problematic step)")
    response = await manager.handle_message(
        user_input="yes please",
        session_id=session_id,
        patient_id=patient_id
    )
    print(f"🤖 AI: {response.message}")
    print(f"📊 State: {response.current_state}")
    
    # Check if we got stuck in a loop
    if "confirm" in response.message.lower() and response.current_state == "identify_medication":
        print("\n❌ ISSUE: Still stuck in confirmation loop!")
        
        # Try one more time with stronger confirmation
        print("\n💬 Step 6: Trying stronger confirmation")
        response = await manager.handle_message(
            user_input="pelase please move forward",  # This was in the logs
            session_id=session_id,
            patient_id=patient_id
        )
        print(f"🤖 AI: {response.message}")
        print(f"📊 State: {response.current_state}")
        
    # Look for success indicators
    if any(keyword in response.message.lower() for keyword in ["order", "submitted", "confirmation", "refill has been"]):
        print("\n✅ SUCCESS: Order appears to have been submitted!")
    elif response.current_state != "identify_medication":
        print(f"\n✅ PROGRESS: Moved out of identify_medication state to {response.current_state}")
    else:
        print("\n❌ ISSUE: Still stuck in identify_medication state")
    
    print("\n" + "=" * 50)
    print("🎯 Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_omeprazole_conversation())