#!/usr/bin/env python3
"""
Simple test of the LLM system to debug issues
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rxflow.llm import get_conversational_llm, get_analytical_llm


async def test_basic_llm():
    """Test basic LLM functionality"""
    print("🧪 Testing Basic LLM System\n")
    
    try:
        # Test conversational LLM
        print("1️⃣ Testing conversational LLM...")
        conv_llm = get_conversational_llm()
        
        response = await conv_llm.ainvoke("Hello, how are you today?")
        print(f"✅ Conversational LLM response: {response.content[:100]}...")
        
        # Test analytical LLM
        print("\n2️⃣ Testing analytical LLM...")
        ana_llm = get_analytical_llm()
        
        response = await ana_llm.ainvoke("What is 2+2?")
        print(f"✅ Analytical LLM response: {response.content[:100]}...")
        
        print("\n🎉 Basic LLM tests passed!")
        
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        raise


async def test_simple_conversation():
    """Test a simple conversation without complex intent classification"""
    print("\n🧪 Testing Simple Conversation\n")
    
    try:
        llm = get_conversational_llm()
        
        prompt = """You are RxFlow, a pharmacy assistant. Help the user with their prescription refill.
        
User: I need to refill my lisinopril 10mg
Assistant: """

        response = await llm.ainvoke(prompt)
        print(f"🤖 Simple response: {response.content}")
        
        print("\n✅ Simple conversation test passed!")
        
    except Exception as e:
        print(f"❌ Simple conversation test failed: {e}")
        raise


async def main():
    """Run all tests in single event loop"""
    await test_basic_llm()
    await test_simple_conversation()

if __name__ == "__main__":
    asyncio.run(main())