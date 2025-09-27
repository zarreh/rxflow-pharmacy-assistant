#!/usr/bin/env python3
"""
Test the new intelligent conversation system
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rxflow.workflow.refill_conversation import start_refill_conversation, continue_refill_conversation


async def test_intelligent_conversation():
    """Test the intelligent conversation flow"""
    print("🧪 Testing Intelligent Conversation System\n")
    
    # Start conversation
    print("👤 User: I need to refill my lisinopril 10mg")
    result1 = await start_refill_conversation(
        patient_id="patient_001",
        message="I need to refill my lisinopril 10mg"
    )
    
    session_id = result1["session_id"]
    print(f"🤖 RxFlow: {result1['response']}")
    print(f"📋 Intent: {result1['intent']}")
    print(f"📦 Entities: {result1['entities']}")
    print()
    
    # Continue conversation  
    print("👤 User: Yes, show me pharmacy options")
    result2 = await continue_refill_conversation(
        session_id=session_id,
        message="Yes, show me pharmacy options"
    )
    
    print(f"🤖 RxFlow: {result2['response']}")
    print(f"📋 Intent: {result2['intent']}")
    print(f"📦 Entities: {result2['entities']}")
    print()
    
    # Continue with cost question
    print("👤 User: What about generic options?")
    result3 = await continue_refill_conversation(
        session_id=session_id,
        message="What about generic options?"
    )
    
    print(f"🤖 RxFlow: {result3['response']}")
    print(f"📋 Intent: {result3['intent']}")
    print(f"📦 Entities: {result3['entities']}")
    
    print("\n✅ Intelligent conversation test completed!")


if __name__ == "__main__":
    asyncio.run(test_intelligent_conversation())