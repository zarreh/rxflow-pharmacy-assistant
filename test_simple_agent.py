#!/usr/bin/env python3
"""
Simple test for LangChain agent setup
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rxflow.llm import get_conversational_llm
from rxflow.tools.patient_history_tool import patient_history_tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

def test_simple_agent():
    print("🧪 Testing LangChain Agent Setup...")
    
    try:
        # Get LLM
        llm = get_conversational_llm()
        print(f"✅ LLM obtained: {type(llm).__name__}")
        
        # Simple tools
        tools = [patient_history_tool]
        print(f"✅ Tools: {len(tools)} tools")
        
        # Simple prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant."),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        print("✅ Prompt template created")
        
        # Create agent
        agent = create_tool_calling_agent(
            llm=llm,
            tools=tools,
            prompt=prompt
        )
        print("✅ Agent created successfully")
        
        # Create executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True
        )
        print("✅ Agent executor created")
        
        # Test simple query
        print("\n🧪 Testing simple query...")
        response = agent_executor.invoke({"input": "Hello, can you help me?"})
        print(f"✅ Response: {response.get('output', 'No output')[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_agent()
    print(f"\n{'✅ Success' if success else '❌ Failed'}")