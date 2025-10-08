"""
RxFlow Pharmacy Assistant - Streamlit Frontend Application

This is the main user interface for the RxFlow Pharmacy Assistant, providing an
intuitive web-based interface for prescription refill management. The application
implements a comprehensive conversational AI system that guides patients through
safe and efficient prescription refill processes.

Key Features:
    - Interactive conversational AI interface for prescription refills
    - Real-time conversation history and state management
    - Comprehensive tool execution logging and monitoring
    - Cost tracking and pharmacy comparison capabilities
    - Patient safety validation with escalation management
    - Insurance verification and prior authorization support
    - Multi-pharmacy integration with location services

User Experience Design:
    - Clean, medical-professional interface design
    - Step-by-step workflow guidance with clear instructions
    - Real-time feedback and status updates
    - Comprehensive error handling with user-friendly messages
    - Responsive design for desktop and mobile access
    - Accessibility features for inclusive user experience

Safety Features:
    - Mandatory safety checks at each workflow step
    - Automatic escalation for controlled substances
    - Interactive confirmations for critical decisions
    - Comprehensive audit logging for regulatory compliance
    - Patient data privacy protection and secure handling

Architecture:
    - Streamlit-based responsive web interface
    - LangChain conversation management with OpenAI GPT-4
    - 19 specialized pharmacy tools for comprehensive operations
    - Session-based state management with persistence
    - Real-time logging and monitoring capabilities

Workflow States:
    The application manages users through defined workflow states:
    - INITIAL: Starting conversation and patient identification
    - MEDICATION_SEARCH: Finding and verifying medications
    - ESCALATED: Professional consultation required
    - COST_ANALYSIS: Price comparison and insurance verification
    - PHARMACY_SELECTION: Location and service comparison
    - ORDER_PROCESSING: Prescription submission and tracking
    - COMPLETED: Successful refill completion
    - ERROR: Error handling and recovery

Example Usage:
    ```bash
    # Run the Streamlit application
    streamlit run app.py
    
    # Navigate to http://localhost:8501
    # Start conversation: "I need to refill my blood pressure medication"
    # Follow step-by-step guidance through the refill process
    ```

Technical Components:
    - ConversationManager: Core AI conversation orchestration
    - WorkflowState: State machine for process management
    - Session Management: User session persistence and security
    - Tool Integration: 19 specialized pharmacy operation tools
    - Logging System: Comprehensive audit and debugging capabilities

Security Considerations:
    - Session-based user identification without storing PII
    - Secure API key management for external services
    - Input validation and sanitization
    - Audit logging for regulatory compliance
    - Error handling that doesn't expose system internals

Deployment:
    - Docker containerization support
    - Environment-based configuration management
    - Health check endpoints for monitoring
    - Scalable architecture for multi-user deployment

Note:
    This application uses mock data for demonstration purposes.
    Production deployment requires integration with certified pharmacy
    systems and compliance with healthcare regulations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import streamlit as st

# Import configuration and utilities
from rxflow.config.settings import get_settings
from rxflow.utils.logger import get_all_session_logs, get_logger, setup_logging

# Import workflow types
from rxflow.workflow.workflow_types import WorkflowState
from ui.components.chat import render_chat_interface
from ui.components.data_utils import export_session_data, load_demo_data
from ui.components.debug import render_debug_tabs
from ui.components.header import render_main_header, render_patient_context
from ui.components.sidebar import render_sidebar

# Import UI components
from ui.components.styles import apply_custom_css, get_page_config
from ui.message_processor import process_user_input
from ui.session_manager import initialize_session_state, reset_conversation

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Page configuration
st.set_page_config(**get_page_config())

# Apply custom CSS
apply_custom_css()


# Session state initialization is now handled by session_manager module


def main() -> None:
    """
    Main application entry point for RxFlow Pharmacy Assistant Streamlit interface.

    This function orchestrates the entire user interface, initializing session state,
    rendering the main application components, and coordinating the conversational
    AI workflow for prescription refill assistance.
    """

    # Initialize session state
    initialize_session_state()

    # Load demo data
    demo_data = load_demo_data()

    # Render header
    render_main_header()

    # Create export callback function
    def export_callback():
        json_str = export_session_data(
            st.session_state.session_id,
            st.session_state.patient_id,
            st.session_state.session_start_time,
            st.session_state.current_state,
            st.session_state.messages,
            st.session_state.conversation_context,
            st.session_state.tool_logs,
            st.session_state.cost_savings,
        )
        st.sidebar.download_button(
            label="📥 Download Session JSON",
            data=json_str,
            file_name=f"rxflow_session_{st.session_state.session_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
        )

    # Render sidebar and get updates
    selected_patient, updated_debug_info = render_sidebar(
        demo_data=demo_data,
        patient_id=st.session_state.patient_id,
        session_start_time=st.session_state.session_start_time,
        session_id=st.session_state.session_id,
        current_state=st.session_state.current_state,
        show_debug_info=st.session_state.show_debug_info,
        reset_callback=reset_conversation,
        export_callback=export_callback,
    )

    # Update session state from sidebar
    if selected_patient != st.session_state.patient_id:
        st.session_state.patient_id = selected_patient

    if updated_debug_info != st.session_state.show_debug_info:
        st.session_state.show_debug_info = updated_debug_info

    # Chat interface - now takes full width
    render_chat_interface(st.session_state.messages)

    # Chat input
    user_input = st.chat_input("Type your message here...", key="chat_input")

    if user_input:
        # Add user message
        timestamp = datetime.now().strftime("%I:%M %p")
        user_message = {
            "role": "user",
            "content": user_input,
            "timestamp": timestamp,
        }
        st.session_state.messages.append(user_message)

        # Process and get response
        try:
            with st.spinner("Processing..."):
                result = process_user_input(user_input)

            # Add assistant response with metadata
            assistant_message = {
                "role": "assistant",
                "content": result["response"],
                "timestamp": timestamp,
                "tools_used": result.get("tools_used", 0),
                "state": result.get("state", ""),
            }
            st.session_state.messages.append(assistant_message)

            st.rerun()

        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            st.error("I'm having trouble processing your request. Please try again.")

    # Only show technical details if debug mode is on
    if st.session_state.show_debug_info:
        with st.expander("🔧 Debug Info"):
            render_debug_tabs(
                st.session_state.current_state,
                st.session_state.tool_logs,
                st.session_state.cost_savings,
            )


if __name__ == "__main__":
    main()
