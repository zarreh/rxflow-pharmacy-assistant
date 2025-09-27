"""
RxFlow Pharmacy Assistant - Streamlit Frontend
Main application interface for the pharmacy refill AI assistant
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Any, Dict

import streamlit as st

# Import configuration and utilities
from rxflow.config.settings import get_settings
from rxflow.utils.logger import get_logger, setup_logging
# Import simple conversation system
from rxflow.workflow.simple_conversation import (
    get_simple_response,
    clear_simple_conversation,
    get_simple_conversation_summary
)

# Import workflow components (will be created later)
# from rxflow.workflow.graph import create_workflow
# from rxflow.workflow.state import create_initial_state

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
</style>
""",
    unsafe_allow_html=True,
)


def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "workflow_state" not in st.session_state:
        st.session_state.workflow_state = None

    if "patient_id" not in st.session_state:
        st.session_state.patient_id = "patient_001"

    if "workflow_initialized" not in st.session_state:
        st.session_state.workflow_initialized = False

    if "conversation_context" not in st.session_state:
        st.session_state.conversation_context = {}

    if "current_step" not in st.session_state:
        st.session_state.current_step = "initial"

    if "conversation_session_id" not in st.session_state:
        # Initialize conversation session
        st.session_state.conversation_session_id = None
        
    if "conversation_summary" not in st.session_state:
        st.session_state.conversation_summary = {}


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
    """Render the sidebar with configuration and demo data"""
    st.sidebar.title("🔧 Configuration")

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

        st.session_state.patient_id = selected_patient

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
    settings = get_settings()
    st.sidebar.markdown("**Current Settings:**")
    st.sidebar.text(f"LLM: {settings.ollama_model}")
    st.sidebar.text(f"Mock Data: {settings.use_mock_data}")

    # Clear conversation button
    if st.sidebar.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.session_state.workflow_state = None
        st.session_state.workflow_initialized = False
        st.rerun()


def render_chat_message(message: Dict[str, str]):
    """Render a chat message"""
    role = message["role"]
    content = message["content"]
    timestamp = message.get("timestamp", "")

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
        st.markdown(
            f"""
        <div class="chat-message assistant-message">
            <strong>🤖 RxFlow Assistant</strong> <small>{timestamp}</small><br>
            {content}
        </div>
        """,
            unsafe_allow_html=True,
        )


async def process_user_input_async(user_input: str) -> str:
    """Process user input through simple conversation system"""
    try:
        patient_id = st.session_state.patient_id
        session_id = st.session_state.conversation_session_id
        
        # Generate session ID if needed
        if session_id is None:
            import uuid
            session_id = str(uuid.uuid4())
            st.session_state.conversation_session_id = session_id
        
        # Prepare context
        context = {
            "patient_id": patient_id,
            "extracted_entities": st.session_state.conversation_summary.get("entities", {})
        }
        
        # Get response from simple conversation system
        result = await get_simple_response(session_id, user_input, context)
        
        # Update session state
        st.session_state.conversation_summary = result
        
        return result["response"]
            
    except Exception as e:
        logger.error(f"Error in simple conversation: {e}")
        return "I apologize, but I'm having trouble processing your request right now. Could you please try rephrasing your question?"





def process_user_input(user_input: str) -> str:
    """Synchronous wrapper for async chain processing"""
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
        return "I apologize, but I encountered an error processing your request. Please try again."


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

    # Main chat interface
    col1, col2 = st.columns([3, 1])

    with col1:
        # Welcome message
        if not st.session_state.messages:
            st.markdown(
                """
            <div class="system-info">
                <strong>👋 Welcome to RxFlow!</strong><br>
                I'm your AI pharmacy assistant. I can help you:
                <ul>
                    <li>Refill your prescriptions</li>
                    <li>Find the best pharmacy prices</li>
                    <li>Check for drug interactions</li>
                    <li>Handle insurance authorizations</li>
                    <li>Optimize your medication costs</li>
                </ul>
                Try saying something like: <em>"I need to refill my lisinopril"</em>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Display chat history
        for message in st.session_state.messages:
            render_chat_message(message)

        # Chat input
        user_input = st.chat_input(
            "Type your refill request here... (e.g., 'I need to refill my lisinopril')"
        )

        if user_input:
            # Add user message
            timestamp = datetime.now().strftime("%H:%M")
            st.session_state.messages.append(
                {"role": "user", "content": user_input, "timestamp": timestamp}
            )

            # Process and get response
            try:
                with st.spinner("Processing your request..."):
                    response = process_user_input(user_input)

                # Add assistant response
                st.session_state.messages.append(
                    {"role": "assistant", "content": response, "timestamp": timestamp}
                )

                st.rerun()

            except Exception as e:
                logger.error(f"Error processing user input: {e}")
                st.error(
                    "Sorry, I encountered an error processing your request. Please try again."
                )

    with col2:
        # Intelligent conversation status
        st.markdown("### � Smart Conversation")

        session_id = st.session_state.get("conversation_session_id")
        summary = st.session_state.get("conversation_summary", {})
        
        if session_id:
            st.text(f"Session: {session_id[:8]}...")
            
            # Show current intent if available
            if summary.get("intent"):
                intent_display = {
                    "refill_request": "💊 Processing refill",
                    "pharmacy_inquiry": "🏪 Finding pharmacies", 
                    "cost_inquiry": "💰 Checking costs",
                    "general_question": "❓ Answering question",
                    "escalation_needed": "⚠️ Needs pharmacist"
                }
                intent = summary["intent"]
                st.text(f"Intent: {intent_display.get(intent, intent)}")
            
            # Show extracted entities
            entities = summary.get("entities", {})
            if entities.get("medication"):
                st.text(f"Medication: {entities['medication']}")
            if entities.get("pharmacy"):
                st.text(f"Pharmacy: {entities['pharmacy']}")
        else:
            st.text("Status: Ready for new conversation")

        # Quick actions
        st.markdown("### ⚡ Quick Actions")

        # Reset conversation button
        if st.button("🔄 New Conversation", type="secondary"):
            # Clear conversation in backend
            if st.session_state.get("conversation_session_id"):
                clear_simple_conversation(st.session_state.conversation_session_id)
            
            # Reset session state
            st.session_state.conversation_session_id = None
            st.session_state.conversation_summary = {}
            st.session_state.messages = []
            st.rerun()

        st.markdown("---")

        demo_data = load_demo_data()
        if demo_data.get("drugs"):
            st.text("Try these examples:")

            if st.button("💊 Refill Lisinopril 10mg"):
                st.session_state.messages.append(
                    {
                        "role": "user",
                        "content": "I need to refill my lisinopril 10mg",
                        "timestamp": datetime.now().strftime("%H:%M"),
                    }
                )
                st.rerun()

            if st.button("💊 Refill Metformin 500mg"):
                st.session_state.messages.append(
                    {
                        "role": "user",
                        "content": "I need to refill my metformin 500mg",
                        "timestamp": datetime.now().strftime("%H:%M"),
                    }
                )
                st.rerun()

            if st.button("⚠️ No refills remaining"):
                st.session_state.messages.append(
                    {
                        "role": "user",
                        "content": "I have no refills remaining for my prescription",
                        "timestamp": datetime.now().strftime("%H:%M"),
                    }
                )
                st.rerun()


if __name__ == "__main__":
    main()
