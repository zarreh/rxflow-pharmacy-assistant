"""
Chat components for RxFlow Pharmacy Assistant

This module contains chat-related UI components including message rendering
and chat interface elements.
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Any


def render_chat_interface(messages: List[Dict[str, str]]) -> None:
    """
    Render the main chat interface container.
    
    Args:
        messages (List[Dict[str, str]]): List of conversation messages
    """
    # No need for wrapper HTML structure anymore
    pass
    
    # Display messages or empty state
    if not messages:
        render_empty_chat_state()
    else:
        for message in messages:
            render_chat_message(message)
    
    # No closing tags needed


def render_empty_chat_state() -> None:
    """Render empty chat state with welcome message."""
    st.markdown(
        """
        <div style="text-align: center; padding: 3rem; color: #9ca3af;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">💬</div>
            <p>Hi! I'm your pharmacy assistant. How can I help you today?</p>
            <p style="font-size: 0.875rem;">You can type a message or use the quick actions on the right.</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_chat_message(message: Dict[str, str]) -> None:
    """
    Render a single chat message with appropriate styling.
    
    Displays user or assistant messages with distinct visual styling,
    icons, and formatting for optimal readability.
    
    Args:
        message (Dict[str, str]): Message dictionary containing:
            - role (str): "user" or "assistant"
            - content (str): Message text content
            - timestamp (str, optional): ISO format timestamp
    """
    role = message["role"]
    content = message["content"]
    timestamp = message.get("timestamp", "")

    if role == "user":
        st.markdown(
            f"""
            <div class="chat-message user-message">
                <div class="message-avatar user-avatar">👤</div>
                <div class="message-content">
                    {content}
                    <div class="message-time">{timestamp}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="chat-message assistant-message">
                <div class="message-avatar assistant-avatar">💊</div>
                <div class="message-content">
                    {content}
                    <div class="message-time">{timestamp}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )