"""
Message processing utilities for RxFlow Pharmacy Assistant

This module handles the processing of user messages through the AI system.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any

import streamlit as st
from rxflow.utils.logger import get_logger

logger = get_logger(__name__)


async def process_user_input_async(user_input: str) -> Dict[str, Any]:
    """Process user input through advanced conversation manager"""
    try:
        # Get conversation manager and session info
        conversation_manager = st.session_state.conversation_manager
        session_id = st.session_state.session_id
        patient_id = st.session_state.patient_id

        # Process message through conversation manager
        result = await conversation_manager.process_message(
            session_id=session_id, message=user_input
        )

        # Update session state with conversation info
        st.session_state.current_state = result.current_state

        # Get the conversation context from the session
        conversation_context = conversation_manager.get_session(session_id)
        if conversation_context:
            st.session_state.conversation_context = conversation_context
        else:
            logger.warning(f"No conversation context found for session {session_id}")
            st.session_state.conversation_context = {}

        # Add tool logs from this interaction
        if hasattr(result, "tool_calls") and result.tool_calls:
            for tool_call in result.tool_calls:
                st.session_state.tool_logs.append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "tool": tool_call.get("tool", "unknown"),
                        "input": tool_call.get("input", ""),
                        "success": tool_call.get("success", False),
                        "execution_time": tool_call.get("execution_time", 0),
                    }
                )

        # Update cost savings if available
        if hasattr(result, "cost_analysis") and result.cost_analysis:
            cost_data = result.cost_analysis
            if "savings_amount" in cost_data:
                st.session_state.cost_savings["total_saved"] += cost_data[
                    "savings_amount"
                ]
                st.session_state.cost_savings["comparisons"].append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "medication": cost_data.get("medication", ""),
                        "original_price": cost_data.get("original_price", 0),
                        "best_price": cost_data.get("best_price", 0),
                        "savings": cost_data.get("savings_amount", 0),
                        "source": cost_data.get("best_source", ""),
                    }
                )

        return {
            "response": result.message,
            "state": result.current_state.value,
            "tools_used": len(result.tool_calls)
            if hasattr(result, "tool_calls")
            else 0,
            "success": True,
        }

    except Exception as e:
        logger.error(f"Error in conversation manager: {e}")
        return {
            "response": "I apologize, but I'm having trouble processing your request right now. Could you please try rephrasing your question?",
            "state": "error",
            "tools_used": 0,
            "success": False,
            "error": str(e),
        }


def process_user_input(user_input: str) -> Dict[str, Any]:
    """Synchronous wrapper for async conversation processing"""
    try:
        # Run async function in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(process_user_input_async(user_input))
        finally:
            loop.close()
        return result
    except Exception as e:
        logger.error(f"Error in process_user_input: {e}")
        return {
            "response": "I apologize, but I encountered an error processing your request. Please try again.",
            "state": "error",
            "tools_used": 0,
            "success": False,
            "error": str(e),
        }