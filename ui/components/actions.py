"""
Action components for RxFlow Pharmacy Assistant

This module contains action-related UI components including quick actions,
recent activity, and interactive elements.
"""

import streamlit as st
from datetime import datetime
from typing import Callable, List, Tuple


def render_quick_actions(add_message_callback: Callable) -> None:
    """
    Render quick action buttons for common pharmacy requests.
    
    Displays predefined action buttons that allow users to quickly
    initiate common pharmacy workflows without typing.
    
    Args:
        add_message_callback: Function to call when a quick action is selected
    """
    st.markdown(
        """
        <div class="quick-actions-card">
            <div class="quick-actions-header">
                ⚡ Quick Actions
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Common pharmacy actions
    actions = [
        ("💊", "Refill Medications", "I need to refill my medications"),
        ("🏥", "Find Pharmacy", "Where is the nearest pharmacy?"),
        ("💰", "Check Prices", "What are the prices for my medications?"),
        ("📋", "View Prescriptions", "Show me my active prescriptions"),
    ]
    
    for icon, label, message in actions:
        if st.button(f"{icon} {label}", use_container_width=True, type="secondary"):
            add_message_callback(message)


def render_recent_activity() -> None:
    """Render recent activity card with mock activity data."""
    st.markdown(
        """
        <div class="activity-card">
            <div class="activity-header">🕐 Recent Activity</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Mock recent activities
    activities = [
        ("💊", "Lisinopril refilled", "2 days ago"),
        ("🔔", "Prior auth approved", "5 days ago"),
        ("📋", "New prescription added", "1 week ago"),
    ]
    
    for icon, title, time in activities:
        st.markdown(
            f"""
            <div class="activity-item">
                <div class="activity-icon">{icon}</div>
                <div class="activity-content">
                    <div class="activity-title">{title}</div>
                    <div class="activity-time">{time}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )