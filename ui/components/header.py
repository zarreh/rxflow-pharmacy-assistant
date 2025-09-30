"""
Header components for RxFlow Pharmacy Assistant

This module contains header-related UI components.
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any


def render_main_header() -> None:
    """
    Render the main application header.
    
    Displays the application title and subtitle with consistent styling.
    """
    st.markdown(
        """
        <div class="main-header">
            <h1>💊 RxFlow Pharmacy Assistant</h1>
            <div class="subtitle">Your trusted partner for prescription management</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_patient_context(demo_data: Dict[str, Any], patient_id: str) -> None:
    """
    Render patient context card with current patient information.
    
    Args:
        demo_data (Dict[str, Any]): Demo data containing patient information
        patient_id (str): Current patient ID
    """
    if demo_data.get("patients") and patient_id in demo_data["patients"]:
        patient = demo_data["patients"][patient_id]
        
        # Get medication count
        current_meds = len(patient.get('current_medications', []))
        medication_history = len(patient.get('medication_history', []))
        total_meds = max(current_meds, medication_history)
        
        st.markdown(
            f"""
            <div class="patient-card">
                <div class="patient-card-header">
                    <div class="patient-avatar">{patient['name'][0]}</div>
                    <div class="patient-info">
                        <h3>{patient['name']}</h3>
                        <p>Patient ID: {patient_id}</p>
                    </div>
                </div>
                <div class="patient-details">
                    <div class="detail-item">
                        <div class="detail-label">Insurance</div>
                        <div class="detail-value">{patient.get('insurance_id', 'N/A')}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Medications</div>
                        <div class="detail-value">{total_meds} Active</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Last Refill</div>
                        <div class="detail-value">2 weeks ago</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


