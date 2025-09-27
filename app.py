"""
RxFlow Pharmacy Assistant - Streamlit Frontend
Enhanced UI with conversation history, state display, tool logs, and cost tracking
Step 8: Update Streamlit UI
"""

import asyncio
import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import streamlit as st

# Import configuration and utilities
from rxflow.config.settings import get_settings
from rxflow.utils.logger import get_logger, setup_logging

# Import advanced conversation manager (Step 6)
from rxflow.workflow.conversation_manager import ConversationManager
from rxflow.workflow.workflow_types import RefillState

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


def initialize_session_state():
    """Initialize enhanced session state variables for Step 8"""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "conversation_manager" not in st.session_state:
        st.session_state.conversation_manager = ConversationManager()

    if "patient_id" not in st.session_state:
        st.session_state.patient_id = "12345"  # Mock patient ID

    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if "current_state" not in st.session_state:
        st.session_state.current_state = RefillState.START

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
    """Load demo data for testing"""
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


def render_sidebar():
    """Render enhanced sidebar with session management and debug controls"""
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
        "🐛 Show Debug Info", 
        value=st.session_state.show_debug_info
    )

    # Action buttons
    st.sidebar.markdown("### 🎬 Actions")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            reset_conversation()
    
    with col2:
        if st.button("📊 Export Data", use_container_width=True):
            export_session_data()


def reset_conversation():
    """Reset conversation state"""
    st.session_state.messages = []
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.current_state = RefillState.START
    st.session_state.conversation_context = {}
    st.session_state.tool_logs = []
    st.session_state.cost_savings = {"total_saved": 0, "comparisons": []}
    st.session_state.session_start_time = datetime.now()
    # Create new conversation manager instance
    st.session_state.conversation_manager = ConversationManager()
    st.rerun()


def export_session_data():
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
        "export_timestamp": datetime.now().isoformat()
    }
    
    # Create downloadable JSON
    json_str = json.dumps(export_data, indent=2, default=str)
    st.sidebar.download_button(
        label="📥 Download Session JSON",
        data=json_str,
        file_name=f"rxflow_session_{st.session_state.session_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )


def render_chat_message(message: Dict[str, str]):
    """Render a chat message with enhanced metadata"""
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


def render_tool_logs():
    """Render tool usage logs"""
    if not st.session_state.tool_logs:
        st.info("No tool usage logged yet.")
        return
    
    st.markdown("### 🔧 Tool Usage Log")
    
    # Show recent tools first
    recent_logs = sorted(st.session_state.tool_logs, key=lambda x: x["timestamp"], reverse=True)
    
    for log in recent_logs[:10]:  # Show last 10 tool calls
        timestamp = datetime.fromisoformat(log["timestamp"]).strftime("%H:%M:%S")
        success_icon = "✅" if log["success"] else "❌"
        
        with st.expander(f"{success_icon} {log['tool']} - {timestamp}"):
            st.text(f"Input: {log['input'][:100]}..." if len(log['input']) > 100 else f"Input: {log['input']}")
            st.text(f"Execution time: {log['execution_time']:.2f}s")
            st.text(f"Success: {log['success']}")


def render_cost_savings():
    """Render cost savings information"""
    savings = st.session_state.cost_savings
    
    if savings["total_saved"] > 0:
        st.markdown("### 💰 Cost Savings")
        st.metric(
            label="Total Savings",
            value=f"${savings['total_saved']:.2f}",
            delta=f"+${savings['total_saved']:.2f}"
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


def render_state_visualization():
    """Render current conversation state"""
    st.markdown("### 🎯 Conversation State")
    
    # State indicator
    state_colors = {
        RefillState.START: "🟢",
        RefillState.IDENTIFY_MEDICATION: "🔵", 
        RefillState.CLARIFY_MEDICATION: "🟡",
        RefillState.CONFIRM_DOSAGE: "🟠",
        RefillState.CHECK_AUTHORIZATION: "🟣",
        RefillState.SELECT_PHARMACY: "🔵",
        RefillState.CONFIRM_ORDER: "🟢",
        RefillState.ESCALATE_PA: "🔴",
        RefillState.COMPLETE: "✅",
        RefillState.ERROR: "❌"
    }
    
    current_state = st.session_state.current_state
    state_icon = state_colors.get(current_state, "⚪")
    
    st.markdown(f"**Current State:** {state_icon} {current_state.value.replace('_', ' ').title()}")
    
    # Progress indicator
    state_order = [
        RefillState.START, RefillState.IDENTIFY_MEDICATION, RefillState.CLARIFY_MEDICATION,
        RefillState.CONFIRM_DOSAGE, RefillState.CHECK_AUTHORIZATION, RefillState.SELECT_PHARMACY,
        RefillState.CONFIRM_ORDER, RefillState.COMPLETE
    ]
    
    if current_state in state_order:
        progress = (state_order.index(current_state) + 1) / len(state_order)
        st.progress(progress)
        st.text(f"Progress: {progress:.1%}")
    
    # Context information
    context = st.session_state.conversation_context
    if context and st.session_state.show_debug_info:
        st.markdown("**Context:**")
        for key, value in context.items():
            if key != "session_id" and value:
                st.text(f"{key}: {str(value)[:50]}...")


def render_quick_actions():
    """Render quick action buttons"""
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
        add_quick_message("I need to refill my Eliquis but my insurance requires prior authorization")
    
    if st.button("🚫 No Refills Left", use_container_width=True):
        add_quick_message("I have no refills remaining for my prescription")


def add_quick_message(content: str):
    """Add a quick message to the conversation"""
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
        result = await conversation_manager.handle_message(
            user_input=user_input,
            session_id=session_id,
            patient_id=patient_id
        )
        
        # Update session state with conversation info
        st.session_state.current_state = result.current_state
        st.session_state.conversation_context = result.context.to_dict()
        
        # Add tool logs from this interaction
        if hasattr(result, 'tool_calls') and result.tool_calls:
            for tool_call in result.tool_calls:
                st.session_state.tool_logs.append({
                    "timestamp": datetime.now().isoformat(),
                    "tool": tool_call.get("tool", "unknown"),
                    "input": tool_call.get("input", ""),
                    "success": tool_call.get("success", False),
                    "execution_time": tool_call.get("execution_time", 0)
                })
        
        # Update cost savings if available
        if hasattr(result, 'cost_analysis') and result.cost_analysis:
            cost_data = result.cost_analysis
            if "savings_amount" in cost_data:
                st.session_state.cost_savings["total_saved"] += cost_data["savings_amount"]
                st.session_state.cost_savings["comparisons"].append({
                    "timestamp": datetime.now().isoformat(),
                    "medication": cost_data.get("medication", ""),
                    "original_price": cost_data.get("original_price", 0),
                    "best_price": cost_data.get("best_price", 0),
                    "savings": cost_data.get("savings_amount", 0),
                    "source": cost_data.get("best_source", "")
                })
        
        return {
            "response": result.message,
            "state": result.current_state.value,
            "tools_used": len(result.tool_calls) if hasattr(result, 'tool_calls') else 0,
            "success": True
        }
            
    except Exception as e:
        logger.error(f"Error in conversation manager: {e}")
        return {
            "response": "I apologize, but I'm having trouble processing your request right now. Could you please try rephrasing your question?",
            "state": "error",
            "tools_used": 0,
            "success": False,
            "error": str(e)
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
            "error": str(e)
        }


def main():
    """Main application function"""

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
            user_message = {"role": "user", "content": user_input, "timestamp": timestamp}
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
                    "state": result["state"]
                }
                st.session_state.messages.append(assistant_message)

                st.rerun()

            except Exception as e:
                logger.error(f"Error processing user input: {e}")
                st.error("Sorry, I encountered an error processing your request. Please try again.")

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
