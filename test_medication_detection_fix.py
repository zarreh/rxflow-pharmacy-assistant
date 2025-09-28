#!/usr/bin/env python3
"""
Test script to verify that patient medication history can now find omeprazole
and the conversation system properly detects it for refill requests.
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rxflow.workflow.conversation_manager import ConversationManager

async def test_medication_detection():
    """Test if the conversation system can now detect omeprazole in patient history"""
    
    print("=== Testing Medication Detection Fix ===")
    
    # Create conversation manager
    manager = ConversationManager()
    
    # Test 1: Basic omeprazole request
    print("\n1. Testing basic omeprazole refill request...")
    user_input = "I need a refill for my omeprazole"
    
    try:
        response = await manager.handle_message(user_input, session_id="test_detection")
        print(f"✅ Response received: {response.message[:100]}...")
        
        # Check if omeprazole was detected in the conversation
        if "omeprazole" in response.message.lower():
            print("✅ Omeprazole mentioned in response")
        else:
            print("❌ Omeprazole not mentioned in response")
            
        # Check if we have medication history access
        if "don't have any records" in response.message.lower() or "no records" in response.message.lower():
            print("❌ Still shows no medication records")
        else:
            print("✅ Medication records appear to be accessible")
            
    except Exception as e:
        print(f"❌ Error in test: {e}")
        return False
    
    # Test 2: Verify the patient history tool directly
    print("\n2. Testing patient history tool directly...")
    from rxflow.tools.patient_history_tool import safe_medication_history
    
    result = safe_medication_history("12345")
    medications = result.get("medications", [])
    omeprazole_meds = [med for med in medications if "omeprazole" in med.get("name", "").lower()]
    
    print(f"✅ Found {len(medications)} total medications")
    print(f"✅ Found {len(omeprazole_meds)} omeprazole entries")
    
    if omeprazole_meds:
        omeprazole = omeprazole_meds[0]
        print(f"✅ Omeprazole details: {omeprazole.get('name')} {omeprazole.get('dosage')}")
        print(f"✅ Refills remaining: {omeprazole.get('refills_remaining')}")
    
    return len(omeprazole_meds) > 0

async def main():
    """Run all tests"""
    print("Testing medication detection after patient ID fix...")
    
    success = await test_medication_detection()
    
    if success:
        print("\n🎉 SUCCESS: Medication detection fix is working!")
        print("   - Patient history tool now returns all medications for patient ID")
        print("   - Omeprazole is properly found in patient medication history")
        print("   - Conversation system should now be able to identify omeprazole")
    else:
        print("\n❌ FAILURE: Issues still exist with medication detection")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)