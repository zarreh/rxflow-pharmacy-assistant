#!/usr/bin/env python3
"""
Test the simple conversation system
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rxflow.workflow.simple_conversation import get_simple_response


async def test_simple_conversation():
    """Test the simple conversation flow"""
    print("🧪 Testing Simple Conversation System\n")
    
    session_id = "test_session_123"
    
    # Test 1: Initial refill request
    print("👤 User: I need to refill my lisinopril 10mg")
    result1 = await get_simple_response(
        session_id=session_id,
        message="I need to refill my lisinopril 10mg",
        context={"patient_id": "patient_001"}
    )
    
    print(f"🤖 RxFlow: {result1['response']}")
    print(f"📦 Entities: {result1['entities']}")
    print(f"📊 Status: {result1['status']}")
    print(f"💬 Messages: {result1['message_count']}")
    print()
    
    # Test 2: Continue conversation  
    print("👤 User: Yes, I need a 30-day supply")
    result2 = await get_simple_response(
        session_id=session_id,
        message="Yes, I need a 30-day supply"
    )
    
    print(f"🤖 RxFlow: {result2['response']}")
    print(f"📦 Entities: {result2['entities']}")
    print(f"📊 Status: {result2['status']}")
    print()
    
    # Test 3: Ask about pharmacy
    print("👤 User: What pharmacies do you recommend?")
    result3 = await get_simple_response(
        session_id=session_id,
        message="What pharmacies do you recommend?"
    )
    
    print(f"🤖 RxFlow: {result3['response']}")
    print(f"📦 Entities: {result3['entities']}")
    print(f"📊 Status: {result3['status']}")
    print()
    
    # Test 4: Cost question
    print("👤 User: How much will this cost?")
    result4 = await get_simple_response(
        session_id=session_id,
        message="How much will this cost?"
    )
    
    print(f"🤖 RxFlow: {result4['response']}")
    print(f"📦 Entities: {result4['entities']}")
    print(f"📊 Status: {result4['status']}")
    
    print("\n✅ Simple conversation test completed!")


if __name__ == "__main__":
    asyncio.run(test_simple_conversation())