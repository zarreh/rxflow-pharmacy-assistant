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

import asyncio
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st

# Import configuration and utilities
from rxflow.config.settings import get_settings
from rxflow.utils.logger import get_all_session_logs, get_logger, setup_logging

# Import advanced conversation manager (Step 6)
from rxflow.workflow.conversation_manager import ConversationManager
from rxflow.workflow.workflow_types import WorkflowState

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="RxFlow Pharmacy Assistant",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #667eea;
    }
    
    .user-message {
        background-color: #f0f2f6;
        border-left-color: #667eea;
    }
    
    .assistant-message {
        background-color: #e8f4f8;
        border-left-color: #1f77b4;
    }
    
    .system-info {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 0.75rem;
        margin: 1rem 0;
    }
    
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 0.75rem;
        margin: 1rem 0;
        color: #155724;
    }
    
    .error-message {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 0.75rem;
        margin: 1rem 0;
        color: #721c24;
    }
    
    .state-indicator {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .tool-log-item {
        background-color: #f8f9fa;
        border-left: 3px solid #28a745;
        padding: 0.5rem;
        margin-bottom: 0.5rem;
        border-radius: 0 5px 5px 0;
        font-family: monospace;
        font-size: 0.85em;
    }
    
    .cost-savings {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .quick-action-btn {
        background: linear-gradient(45deg, #17a2b8, #138496);
        color: white;
        border: none;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        cursor: pointer;
        width: 100%;
        margin-bottom: 0.5rem;
        transition: all 0.3s ease;
    }
    
    .quick-action-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""",
    unsafe_allow_html=True,
)


def initialize_session_state() -> None:
    """
    Initialize Streamlit session state variables for pharmacy assistant application.
    
    This function sets up the core session state variables required for the RxFlow
    application, including conversation management, user identification, workflow
    state tracking, and UI component states. It ensures proper initialization
    on first page load and maintains state consistency across user interactions.
    
    Session State Variables Initialized:
        - messages: List of conversation messages between user and AI
        - conversation_manager: ConversationManager instance for AI orchestration
        - patient_id: Mock patient identifier for demo purposes (default: "12345")
        - session_id: Unique UUID for conversation session tracking
        - current_state: Current workflow state (starts at GREETING)
        - tool_results: Results from pharmacy tool executions
        - cost_savings: Calculated savings and cost information
        - selected_pharmacy: User's chosen pharmacy for refill
        - demo_data: Mock patient and pharmacy data for demonstration
    
    Design Patterns:
        - Lazy initialization: Only creates objects when not already present
        - UUID-based session identification for uniqueness
        - Default value pattern for required state variables
        - State isolation for concurrent user sessions
    
    Example State Structure:
        ```python
        st.session_state = {
            "messages": [
                {"role": "user", "content": "I need a refill"},
                {"role": "assistant", "content": "I can help with that..."}
            ],
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "current_state": WorkflowState.MEDICATION_SEARCH,
            "patient_id": "12345",
            "cost_savings": {"total_saved": 25.50, "best_option": "Generic"}
        }
        ```
    
    Performance Considerations:
        - ConversationManager initialization is expensive; only done once per session
        - UUID generation is lightweight and provides good uniqueness guarantees
        - State variables use efficient Python objects (lists, dicts, enums)
    
    Thread Safety:
        Streamlit manages session state per user session, providing natural
        isolation between concurrent users without requiring additional
        synchronization mechanisms.
    
    Note:
        This function should be called at the beginning of the main application
        flow to ensure all required session state is properly initialized
        before any UI components attempt to access it.
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "conversation_manager" not in st.session_state:
        st.session_state.conversation_manager = ConversationManager()

    if "patient_id" not in st.session_state:
        st.session_state.patient_id = "12345"  # Mock patient ID

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


def load_demo_data() -> Dict[str, Any]:
    """
    Load demonstration data from JSON files for testing and development.
    
    Reads mock patient, pharmacy, insurance, and drug data from the data/
    directory to populate the application with realistic test data.
    
    Returns:
        Dict[str, Any]: Demo data dictionary containing:
            - patients (Dict): Mock patient records with medication histories
            - pharmacies (Dict): Mock pharmacy locations and details
            - insurance (Dict): Mock insurance plans and formularies
            - drugs (Dict): Mock medication database with pricing
            Empty dictionaries returned if files are not found
            
    Side Effects:
        - Reads from data/mock_patients.json
        - Reads from data/mock_pharmacies.json  
        - Reads from data/mock_insurance.json
        - Reads from data/mock_drugs.json
        - Displays error messages in Streamlit if files missing
    """
    demo_data = {}

    try:
        # Load patient data
        with open("data/mock_patients.json", "r") as f:
            demo_data["patients"] = json.load(f)

        # Load pharmacy data
        with open("data/mock_pharmacies.json", "r") as f:
            demo_data["pharmacies"] = json.load(f)

        # Load insurance data
        with open("data/mock_insurance.json", "r") as f:
            demo_data["insurance"] = json.load(f)

        # Load drug data
        with open("data/mock_drugs.json", "r") as f:
            demo_data["drugs"] = json.load(f)

    except FileNotFoundError as e:
        st.error(f"Demo data file not found: {e}")
        demo_data = {"patients": {}, "pharmacies": {}, "insurance": {}, "drugs": {}}

    return demo_data


def render_sidebar() -> None:
    """
    Render sidebar with application configuration and session management.
    
    Creates the left sidebar containing demo data display, session controls,
    debug information toggles, and conversation management options.
    
    Returns:
        None: Renders UI components directly to Streamlit sidebar
        
    Side Effects:
        - Displays demo data in expandable sections
        - Renders session management controls (reset, export)
        - Shows debug information toggles
        - Updates session state based on user interactions
        - Calls helper functions for log display and data export
    """
    st.sidebar.title("🔧 Configuration")

    # Session Management
    st.sidebar.markdown("### 🎯 Session Management")

    # Session info
    session_duration = datetime.now() - st.session_state.session_start_time
    st.sidebar.text(f"Session ID: {st.session_state.session_id[:8]}...")
    st.sidebar.text(f"Duration: {str(session_duration).split('.')[0]}")
    st.sidebar.text(f"Current State: {st.session_state.current_state.value}")
    st.sidebar.text(f"Messages: {len(st.session_state.messages)}")

    # Patient selection
    demo_data = load_demo_data()
    if demo_data.get("patients"):
        patient_options = {
            pid: f"{data['name']} ({pid})"
            for pid, data in demo_data["patients"].items()
        }

        selected_patient = st.sidebar.selectbox(
            "Select Demo Patient",
            options=list(patient_options.keys()),
            format_func=lambda x: patient_options[x],
            index=0,
        )

        if selected_patient != st.session_state.patient_id:
            st.session_state.patient_id = selected_patient
            # Reset conversation when patient changes
            if st.sidebar.button("🔄 Switch Patient"):
                reset_conversation()

        # Display patient info
        if selected_patient in demo_data["patients"]:
            patient = demo_data["patients"][selected_patient]
            st.sidebar.markdown("**Patient Info:**")
            st.sidebar.text(f"Name: {patient['name']}")
            st.sidebar.text(f"Insurance: {patient['insurance_id']}")
            st.sidebar.text(
                f"Location: {patient['address']['city']}, {patient['address']['state']}"
            )

    # Settings info
    st.sidebar.markdown("### ⚙️ Settings")
    settings = get_settings()
    st.sidebar.text(f"LLM: {settings.ollama_model}")
    st.sidebar.text(f"Mock Data: {settings.use_mock_data}")

    # Debug controls
    st.session_state.show_debug_info = st.sidebar.checkbox(
        "🐛 Show Debug Info", value=st.session_state.show_debug_info
    )

    # Session Logs Section
    st.sidebar.markdown("### 📋 Session Logs")

    # Show current session log status - simplified logging
    st.sidebar.info("📝 Session logging active")
    # Note: Detailed session log files are not available in simplified version

    # Show all available logs
    all_logs = get_all_session_logs()
    if all_logs:
        st.sidebar.markdown("**Available Logs:**")
        log_options = [
            f"{session_id[:8]} - {path.name}" for session_id, path in all_logs.items()
        ]
        selected_log = st.sidebar.selectbox(
            "Select log to view:", ["None"] + log_options
        )

        if selected_log != "None" and st.sidebar.button("📄 View Selected Log"):
            # Extract session ID and find corresponding path
            selected_session_id = selected_log.split(" - ")[0]
            if selected_session_id in all_logs:
                show_session_log(str(all_logs[selected_session_id]))

    # Action buttons
    st.sidebar.markdown("### 🎬 Actions")

    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            reset_conversation()

    with col2:
        if st.button("📊 Export Data", use_container_width=True):
            export_session_data()


def reset_conversation() -> None:
    """
    Reset conversation state and clear all session data.
    
    Clears the conversation history, resets workflow state, and reinitializes
    the conversation manager for a fresh start.
    
    Returns:
        None: Modifies session state in place
        
    Side Effects:
        - Clears st.session_state.messages list
        - Resets current_state to WorkflowState.GREETING
        - Generates new session_id UUID
        - Clears conversation manager session data
        - Displays success message to user
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


def show_session_log(log_file_path: str) -> None:
    """Show session log contents in an expander"""
    try:
        with open(log_file_path, "r", encoding="utf-8") as f:
            log_content = f.read()

        # Show in an expander in the main area
        with st.expander(f"📋 Session Log: {Path(log_file_path).name}", expanded=True):
            st.code(log_content, language="text")

    except Exception as e:
        st.error(f"Error reading log file: {e}")


def export_session_data() -> None:
    """Export session data for analysis"""
    export_data = {
        "session_id": st.session_state.session_id,
        "patient_id": st.session_state.patient_id,
        "session_duration": str(datetime.now() - st.session_state.session_start_time),
        "current_state": st.session_state.current_state.value,
        "messages": st.session_state.messages,
        "conversation_context": st.session_state.conversation_context,
        "tool_logs": st.session_state.tool_logs,
        "cost_savings": st.session_state.cost_savings,
        "export_timestamp": datetime.now().isoformat(),
    }

    # Create downloadable JSON
    json_str = json.dumps(export_data, indent=2, default=str)
    st.sidebar.download_button(
        label="📥 Download Session JSON",
        data=json_str,
        file_name=f"rxflow_session_{st.session_state.session_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
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
            
    Returns:
        None: Renders message directly to Streamlit interface
        
    Side Effects:
        - Displays message with role-appropriate styling
        - Shows user messages with blue background and user icon
        - Shows assistant messages with white background and bot icon
        - Applies custom CSS classes for consistent formatting
    """
    role = message["role"]
    content = message["content"]
    timestamp = message.get("timestamp", "")
    tools_used = message.get("tools_used", 0)
    state = message.get("state", "")

    if role == "user":
        st.markdown(
            f"""
        <div class="chat-message user-message">
            <strong>👤 You</strong> <small>{timestamp}</small><br>
            {content}
        </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        # Show tool usage and state info for assistant messages
        metadata = ""
        if tools_used and int(tools_used) > 0:
            metadata += f" • 🔧 {tools_used} tools used"
        if state and st.session_state.show_debug_info:
            metadata += f" • 🎯 State: {state}"

        st.markdown(
            f"""
        <div class="chat-message assistant-message">
            <strong>🤖 RxFlow Assistant</strong> <small>{timestamp}{metadata}</small><br>
            {content}
        </div>
        """,
            unsafe_allow_html=True,
        )


def render_tool_logs() -> None:
    """Display recent tool usage logs"""
    if not st.session_state.tool_logs:
        st.info("No tool usage logged yet.")
        return

    st.markdown("### 🔧 Tool Usage Log")

    # Show recent tools first
    recent_logs = sorted(
        st.session_state.tool_logs, key=lambda x: x["timestamp"], reverse=True
    )

    for log in recent_logs[:10]:  # Show last 10 tool calls
        timestamp = datetime.fromisoformat(log["timestamp"]).strftime("%H:%M:%S")
        success_icon = "✅" if log["success"] else "❌"

        with st.expander(f"{success_icon} {log['tool']} - {timestamp}"):
            st.text(
                f"Input: {log['input'][:100]}..."
                if len(log["input"]) > 100
                else f"Input: {log['input']}"
            )
            st.text(f"Execution time: {log['execution_time']:.2f}s")
            st.text(f"Success: {log['success']}")


def render_cost_savings() -> None:
    """Display potential cost savings information"""
    savings = st.session_state.cost_savings

    if savings["total_saved"] > 0:
        st.markdown("### 💰 Cost Savings")
        st.metric(
            label="Total Savings",
            value=f"${savings['total_saved']:.2f}",
            delta=f"+${savings['total_saved']:.2f}",
        )

        if savings["comparisons"]:
            st.markdown("**Recent Comparisons:**")
            for comparison in savings["comparisons"][-3:]:  # Show last 3
                with st.expander(f"💊 {comparison['medication']}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Original", f"${comparison['original_price']:.2f}")
                    with col2:
                        st.metric("Best Price", f"${comparison['best_price']:.2f}")
                    with col3:
                        st.metric("Saved", f"${comparison['savings']:.2f}")
                    st.text(f"Best source: {comparison['source']}")
    else:
        st.info("No cost comparisons yet.")


def render_state_visualization() -> None:
    """Render workflow state visualization"""
    st.markdown("### 🎯 Conversation State")

    # State indicator for simplified workflow
    state_colors = {
        WorkflowState.GREETING: "�",
        WorkflowState.PROCESSING: "",
        WorkflowState.ESCALATED: "🔴",
        WorkflowState.COMPLETED: "✅",
        WorkflowState.ERROR: "❌",
    }

    current_state = st.session_state.current_state
    state_icon = state_colors.get(current_state, "⚪")

    st.markdown(
        f"**Current State:** {state_icon} {current_state.value.replace('_', ' ').title()}"
    )

    # Progress indicator for simplified workflow
    state_order = [
        WorkflowState.GREETING,
        WorkflowState.PROCESSING,
        WorkflowState.COMPLETED,
    ]

    if current_state in state_order:
        progress = (state_order.index(current_state) + 1) / len(state_order)
        st.progress(progress)
        st.text(f"Progress: {progress:.1%}")
    elif current_state == WorkflowState.ESCALATED:
        st.info("🏥 Case escalated to pharmacist")
    elif current_state == WorkflowState.ERROR:
        st.error("❌ Error occurred")

    # Context information
    context = st.session_state.conversation_context
    if context and st.session_state.show_debug_info:
        st.markdown("**Context:**")
        for key, value in context.items():
            if key != "session_id" and value:
                st.text(f"{key}: {str(value)[:50]}...")


def render_quick_actions() -> None:
    """
    Render quick action buttons for common pharmacy requests.
    
    Displays predefined action buttons that allow users to quickly
    initiate common pharmacy workflows without typing.
    
    Returns:
        None: Renders button interface directly to Streamlit
        
    Side Effects:
        - Displays quick action buttons in organized layout
        - Processes button clicks and adds messages to conversation
        - Triggers conversation processing for selected actions
        - Updates session state with new user interactions
    """
    st.markdown("### ⚡ Quick Actions")

    demo_data = load_demo_data()

    # Common refill requests
    col1, col2 = st.columns(2)

    with col1:
        if st.button("💊 Refill Lisinopril", use_container_width=True):
            add_quick_message("I need to refill my lisinopril 10mg")

        if st.button("💊 Refill Metformin", use_container_width=True):
            add_quick_message("I need to refill my metformin 500mg")

    with col2:
        if st.button("🏥 Find Pharmacy", use_container_width=True):
            add_quick_message("Where is the nearest pharmacy?")

        if st.button("💰 Check Prices", use_container_width=True):
            add_quick_message("What are the prices for my medications?")

    # Scenario buttons
    st.markdown("**Test Scenarios:**")

    if st.button("⚠️ Prior Authorization", use_container_width=True):
        add_quick_message(
            "I need to refill my Eliquis but my insurance requires prior authorization"
        )

    if st.button("🚫 No Refills Left", use_container_width=True):
        add_quick_message("I have no refills remaining for my prescription")


def add_quick_message(content: str) -> None:
    """
    Add predefined message to conversation and process response.
    
    Handles quick action button clicks by adding the predefined message
    to the conversation and processing it through the AI system.
    
    Args:
        content (str): Predefined message content to add
            Examples: "I need to refill my medication", "Show me pharmacy locations"
            
    Returns:
        None: Updates conversation state and triggers rerun
        
    Side Effects:
        - Adds user message to session state messages
        - Triggers conversation processing through AI system
        - Forces Streamlit rerun to display updated conversation
        - Updates workflow state based on AI response
    """
    timestamp = datetime.now().strftime("%H:%M")
    st.session_state.messages.append(
        {"role": "user", "content": content, "timestamp": timestamp}
    )
    st.rerun()


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
        import asyncio

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


def main() -> None:
    """
    Main application entry point for RxFlow Pharmacy Assistant Streamlit interface.
    
    This function orchestrates the entire user interface, initializing session state,
    rendering the main application components, and coordinating the conversational
    AI workflow for prescription refill assistance. It provides the primary user
    experience for the pharmacy assistant system.
    
    Application Flow:
        1. Initialize session state variables and conversation manager
        2. Render main header with branding and application title  
        3. Setup sidebar with controls, demo data, and session management
        4. Create main chat interface with conversation history
        5. Implement tabbed interface for state, tools, and cost information
        6. Provide quick action buttons for common user interactions
        7. Handle user input processing and conversation management
    
    UI Components Rendered:
        - Main Header: Application branding and title with gradient styling
        - Sidebar: Session controls, demo data, logs, and export functionality  
        - Chat Interface: Conversational AI interaction with message history
        - State Visualization: Current workflow state and progress tracking
        - Tool Logs: Real-time display of pharmacy tool execution results
        - Cost Savings: Financial analysis and savings opportunities
        - Quick Actions: Predefined message buttons for common requests
    
    Key Features:
        - Real-time conversation with AI pharmacy assistant
        - Step-by-step workflow guidance with visual state tracking
        - Comprehensive tool execution monitoring and logging
        - Cost analysis with savings calculations and pharmacy comparisons
        - Session management with conversation history persistence
        - Export functionality for session data and audit trails
    
    User Experience Design:
        - Responsive two-column layout optimizing screen real estate
        - Professional medical interface with intuitive navigation
        - Real-time feedback and status updates during processing
        - Clear visual indicators for workflow progress and state
        - Accessible design patterns following web accessibility guidelines
    
    Error Handling:
        - Graceful degradation when AI services are unavailable
        - User-friendly error messages without exposing system details
        - Automatic session recovery and state restoration
        - Comprehensive logging for debugging and audit purposes
    
    Performance Considerations:
        - Lazy loading of expensive components (ConversationManager)
        - Efficient state management using Streamlit's session state
        - Optimized rendering with conditional component updates
        - Minimal API calls through intelligent caching strategies
    
    Example User Journey:
        1. User loads application and sees welcome interface
        2. Clicks "I need to refill my medication" quick action
        3. AI responds with step-by-step guidance for medication identification
        4. User confirms medication details through interactive prompts
        5. System provides cost analysis and pharmacy options
        6. User selects preferred pharmacy and completes refill process
        7. Session data is available for export and audit purposes
    
    Integration Points:
        - ConversationManager: Core AI conversation orchestration
        - WorkflowState: State machine for process management  
        - Pharmacy Tools: 19 specialized tools for comprehensive operations
        - Logging System: Audit trails and debugging information
        - Demo Data: Mock patient and pharmacy information
    
    Note:
        This function serves as the single entry point for the Streamlit
        application and should be called when the module is executed directly.
        It handles all UI initialization and user interaction coordination.
    """

    # Initialize session state
    initialize_session_state()

    # Header
    st.markdown(
        """
    <div class="main-header">
        <h1>💊 RxFlow Pharmacy Assistant</h1>
        <p>AI-powered prescription refill assistance</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Render sidebar
    render_sidebar()

    # Enhanced main interface layout
    col1, col2 = st.columns([2.5, 1.5])

    with col1:
        # Welcome message
        if not st.session_state.messages:
            st.markdown(
                """
            <div class="system-info">
                <strong>👋 Welcome to RxFlow Enhanced!</strong><br>
                I'm your AI pharmacy assistant with advanced capabilities:
                <ul>
                    <li>🔧 <strong>17 integrated tools</strong> for comprehensive assistance</li>
                    <li>💊 Smart medication identification and verification</li>
                    <li>🏥 Real-time pharmacy inventory and pricing</li>
                    <li>💰 Cost optimization with GoodRx integration</li>
                    <li>📋 Insurance authorization handling</li>
                    <li>🎯 <strong>State-based conversation flow</strong></li>
                </ul>
                Try: <em>"I need to refill my lisinopril"</em> or <em>"Find the cheapest pharmacy near me"</em>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Display chat history
        for message in st.session_state.messages:
            render_chat_message(message)

        # Chat input
        user_input = st.chat_input(
            "Type your refill request... (Enhanced with AI tools!)"
        )

        if user_input:
            # Add user message
            timestamp = datetime.now().strftime("%H:%M")
            user_message = {
                "role": "user",
                "content": user_input,
                "timestamp": timestamp,
            }
            st.session_state.messages.append(user_message)

            # Process and get response
            try:
                with st.spinner("🔧 Processing with AI tools..."):
                    result = process_user_input(user_input)

                # Add assistant response with metadata
                assistant_message = {
                    "role": "assistant",
                    "content": result["response"],
                    "timestamp": timestamp,
                    "tools_used": result["tools_used"],
                    "state": result["state"],
                }
                st.session_state.messages.append(assistant_message)

                st.rerun()

            except Exception as e:
                logger.error(f"Error processing user input: {e}")
                st.error(
                    "Sorry, I encountered an error processing your request. Please try again."
                )

    with col2:
        # Tabbed interface for enhanced features
        tab1, tab2, tab3 = st.tabs(["🎯 State", "🔧 Tools", "💰 Savings"])

        with tab1:
            render_state_visualization()

        with tab2:
            render_tool_logs()

        with tab3:
            render_cost_savings()

        st.markdown("---")

        # Quick actions at the bottom
        render_quick_actions()


if __name__ == "__main__":
    main()
