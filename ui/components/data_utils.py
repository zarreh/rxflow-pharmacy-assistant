"""
Data utilities for RxFlow Pharmacy Assistant

This module contains utilities for loading demo data and managing
session state information.
"""

import json
import streamlit as st
from typing import Dict, Any


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


def export_session_data(
    session_id: str,
    patient_id: str,
    session_start_time,
    current_state,
    messages: list,
    conversation_context: dict,
    tool_logs: list,
    cost_savings: dict
) -> str:
    """
    Export session data for analysis.
    
    Args:
        session_id: Current session ID
        patient_id: Current patient ID
        session_start_time: Session start time
        current_state: Current workflow state
        messages: Conversation messages
        conversation_context: Conversation context
        tool_logs: Tool execution logs
        cost_savings: Cost savings data
        
    Returns:
        str: JSON string of exported data
    """
    from datetime import datetime
    
    export_data = {
        "session_id": session_id,
        "patient_id": patient_id,
        "session_duration": str(datetime.now() - session_start_time),
        "current_state": current_state.value,
        "messages": messages,
        "conversation_context": conversation_context,
        "tool_logs": tool_logs,
        "cost_savings": cost_savings,
        "export_timestamp": datetime.now().isoformat(),
    }

    return json.dumps(export_data, indent=2, default=str)