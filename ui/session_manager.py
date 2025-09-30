"""
Session management utilities for RxFlow Pharmacy Assistant

This module handles session state initialization, management, and persistence.
"""

import uuid
import streamlit as st
from datetime import datetime
from rxflow.workflow.conversation_manager import ConversationManager
from rxflow.workflow.workflow_types import WorkflowState


def initialize_session_state() -> None:
    """
    Initialize Streamlit session state variables for pharmacy assistant application.
    
    This function sets up the core session state variables required for the RxFlow
    application, including conversation management, user identification, workflow
    state tracking, and UI component states.
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "conversation_manager" not in st.session_state:
        st.session_state.conversation_manager = ConversationManager()

    if "patient_id" not in st.session_state:
        st.session_state.patient_id = "patient_001"  # Default to John Smith

    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if "current_state" not in st.session_state:
        st.session_state.current_state = WorkflowState.GREETING

    if "conversation_context" not in st.session_state:
        st.session_state.conversation_context = {}

    if "tool_logs" not in st.session_state:
        st.session_state.tool_logs = []

    if "cost_savings" not in st.session_state:
        st.session_state.cost_savings = {"total_saved": 0, "comparisons": []}

    if "session_start_time" not in st.session_state:
        st.session_state.session_start_time = datetime.now()

    if "show_debug_info" not in st.session_state:
        st.session_state.show_debug_info = False


def reset_conversation() -> None:
    """
    Reset conversation state and clear all session data.
    
    Clears the conversation history, resets workflow state, and reinitializes
    the conversation manager for a fresh start.
    """
    st.session_state.messages = []
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.current_state = WorkflowState.GREETING
    st.session_state.conversation_context = {}
    st.session_state.tool_logs = []
    st.session_state.cost_savings = {"total_saved": 0, "comparisons": []}
    st.session_state.session_start_time = datetime.now()
    # Create new conversation manager instance
    st.session_state.conversation_manager = ConversationManager()
    st.rerun()


def add_quick_message(content: str) -> None:
    """
    Add predefined message to conversation and process response.
    
    Handles quick action button clicks by adding the predefined message
    to the conversation and processing it through the AI system.
    
    Args:
        content (str): Predefined message content to add
    """
    from ui.message_processor import process_user_input
    
    timestamp = datetime.now().strftime("%I:%M %p")
    
    # Add user message
    user_message = {
        "role": "user",
        "content": content,
        "timestamp": timestamp,
    }
    st.session_state.messages.append(user_message)
    
    # Process and get AI response
    try:
        result = process_user_input(content)
        
        # Add assistant response with metadata
        assistant_message = {
            "role": "assistant",
            "content": result["response"],
            "timestamp": timestamp,
            "tools_used": result.get("tools_used", 0),
            "state": result.get("state", ""),
        }
        st.session_state.messages.append(assistant_message)
        
        # Update session state
        if "state" in result:
            st.session_state.current_state = result["state"]
        if "tools_used" in result:
            st.session_state.tool_logs.extend(result.get("tool_logs", []))
            
    except Exception as e:
        # Handle errors gracefully
        error_message = {
            "role": "assistant", 
            "content": f"I apologize, but I encountered an error processing your request: {str(e)}",
            "timestamp": timestamp
        }
        st.session_state.messages.append(error_message)
    
    st.rerun()