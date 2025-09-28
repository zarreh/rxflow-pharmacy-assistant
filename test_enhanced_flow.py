#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from rxflow.workflow.conversation_manager import ConversationManager

async def test_enhanced_flow():
    """Test the enhanced conversation flow with better confirmation handling"""
    
    print("🧪 Testing Enhanced Conversation Flow")
    print("=" * 60)
    
    # Initialize conversation manager
    manager = ConversationManager()
    session_id = None
    
    # Test conversation flow that reproduces the issue
    test_messages = [
        "hi, i need refill for a drug for my acid reflux that I take every morning but I don't remember.",
        "which one/ones are for acid reflux?",
        "I got it. it is Omeprazole (20mg capsules). can I have refill for this?",
        "yes"  # This should properly proceed with the refill
    ]
    
    print("Test Scenario: Acid reflux medication refill with confirmation")
    print("-" * 60)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 Step {i}: User says: '{message}'")
        print("-" * 40)
        
        try:
            response = await manager.handle_message(message, session_id)
            session_id = response.session_id
            
            print(f"🤖 AI Response:")
            print(f"   State: {response.current_state.value}")
            print(f"   Message: {response.message}")
            
            if response.next_steps:
                print(f"   Next Steps: {response.next_steps}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            break
    
    print("\n" + "=" * 60)
    print("✅ Enhanced Flow Test Complete")

if __name__ == "__main__":
    asyncio.run(test_enhanced_flow())