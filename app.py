"""
RxFlow Pharmacy Assistant - Streamlit Frontend
Main application interface for the pharmacy refill AI assistant
"""

import streamlit as st
import asyncio
from typing import Dict, Any
import json
import os
from datetime import datetime

# Import configuration and utilities
from rxflow.config.settings import get_settings
from rxflow.utils.logger import setup_logging, get_logger

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
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
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
""", unsafe_allow_html=True)


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
            index=0
        )
        
        st.session_state.patient_id = selected_patient
        
        # Display patient info
        if selected_patient in demo_data["patients"]:
            patient = demo_data["patients"][selected_patient]
            st.sidebar.markdown("**Patient Info:**")
            st.sidebar.text(f"Name: {patient['name']}")
            st.sidebar.text(f"Insurance: {patient['insurance_id']}")
            st.sidebar.text(f"Location: {patient['address']['city']}, {patient['address']['state']}")
    
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
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>👤 You</strong> <small>{timestamp}</small><br>
            {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>🤖 RxFlow Assistant</strong> <small>{timestamp}</small><br>
            {content}
        </div>
        """, unsafe_allow_html=True)


def process_user_input(user_input: str) -> str:
    """Process user input through the workflow (placeholder for now)"""
    
    # TODO: Replace with actual workflow processing
    # This is a placeholder response system
    
    responses = {
        "help": "I can help you refill your prescriptions! Just tell me which medication you need refilled, like 'I need to refill my lisinopril' or 'refill metformin'.",
        "refill": "I'd be happy to help you refill your prescription! Could you please tell me which medication you need refilled and the strength (e.g., 'lisinopril 10mg')?",
        "lisinopril": "I found your Lisinopril 10mg prescription. You have 2 refills remaining. Would you like me to check which pharmacy has the best price and shortest wait time?",
        "metformin": "I see your Metformin 500mg prescription. You have 3 refills remaining. Let me check availability and pricing at nearby pharmacies.",
        "eliquis": "I found your Eliquis 5mg prescription, but it requires prior authorization. Would you like me to request a new authorization from Dr. Johnson?",
        "default": "I understand you're looking to refill a prescription. Could you please specify which medication you need? For example, you can say 'I need to refill my lisinopril 10mg' or just 'refill metformin'."
    }
    
    user_lower = user_input.lower()
    
    if "help" in user_lower:
        return responses["help"]
    elif any(med in user_lower for med in ["lisinopril", "prinivil", "zestril"]):
        return responses["lisinopril"]
    elif any(med in user_lower for med in ["metformin", "glucophage"]):
        return responses["metformin"]
    elif any(med in user_lower for med in ["eliquis", "apixaban"]):
        return responses["eliquis"]
    elif "refill" in user_lower:
        return responses["refill"]
    else:
        return responses["default"]


def main():
    """Main application function"""
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>💊 RxFlow Pharmacy Assistant</h1>
        <p>AI-powered prescription refill assistance</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Render sidebar
    render_sidebar()
    
    # Main chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Welcome message
        if not st.session_state.messages:
            st.markdown("""
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
            """, unsafe_allow_html=True)
        
        # Display chat history
        for message in st.session_state.messages:
            render_chat_message(message)
        
        # Chat input
        user_input = st.chat_input("Type your refill request here... (e.g., 'I need to refill my lisinopril')")
        
        if user_input:
            # Add user message
            timestamp = datetime.now().strftime("%H:%M")
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": timestamp
            })
            
            # Process and get response
            try:
                with st.spinner("Processing your request..."):
                    response = process_user_input(user_input)
                
                # Add assistant response
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response,
                    "timestamp": timestamp
                })
                
                st.rerun()
                
            except Exception as e:
                logger.error(f"Error processing user input: {e}")
                st.error("Sorry, I encountered an error processing your request. Please try again.")
    
    with col2:
        # Workflow status (placeholder)
        st.markdown("### 📊 Workflow Status")
        
        if st.session_state.workflow_state:
            st.text("Current Step: Input Processing")
            st.text("Patient: John Smith")
            st.text("Insurance: Verified")
            st.text("Pharmacy: Searching...")
        else:
            st.text("Status: Ready")
            st.text("Waiting for refill request...")
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        
        demo_data = load_demo_data()
        if demo_data.get("drugs"):
            st.text("Common medications:")
            if st.button("Refill Lisinopril"):
                st.session_state.messages.append({
                    "role": "user",
                    "content": "I need to refill my lisinopril",
                    "timestamp": datetime.now().strftime("%H:%M")
                })
                st.rerun()
            
            if st.button("Refill Metformin"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": "I need to refill my metformin",
                    "timestamp": datetime.now().strftime("%H:%M")
                })
                st.rerun()


if __name__ == "__main__":
    main()