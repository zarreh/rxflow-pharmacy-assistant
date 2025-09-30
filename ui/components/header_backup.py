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


def render_progress_indicator(current_state) -> None:
    """
    Render comprehensive progress indicator for refill process.
    
    Args:
        current_state: Current workflow state
    """
    from rxflow.workflow.workflow_types import WorkflowState, RefillState
    
    # Define comprehensive workflow steps
    steps = [
        ("🚀", "Start", "greeting"),
        ("🔍", "Identify", "processing"),
        ("📋", "Verify", "processing"),
        ("💰", "Review", "processing"),
        ("🎯", "Complete", "completed")
    ]
    
    # Determine current step based on state with comprehensive logic
    current_step = 0
    
    # Check if current_state has a 'value' attribute (enum) or is a string
    state_value = current_state.value if hasattr(current_state, 'value') else str(current_state).lower()
    
    # Map all possible states to progress steps with more gradual progression
    if state_value in ['greeting', 'start']:
        current_step = 0  # Start - 0%
    elif state_value in ['processing', 'identify_medication', 'clarify_medication']:
        current_step = 1  # Identify - 25%
    elif state_value in ['medication_verified', 'confirm_dosage', 'check_authorization', 'dosage_verification']:
        current_step = 2  # Verify - 50%
    elif state_value in ['escalated', 'escalate_pa', 'select_pharmacy', 'cost_analysis', 'pharmacy_selection']:
        current_step = 3  # Review - 75%
    elif state_value in ['completed', 'complete', 'order_submitted', 'confirmed']:
        current_step = 4  # Complete - 100%
    elif state_value in ['error']:
        current_step = max(1, current_step)  # At least identify stage
    else:
        # Default progression - when processing starts, show at least 25%
        current_step = 1 if state_value != 'greeting' else 0
    
    # Calculate progress percentage
    progress_percentage = (current_step / (len(steps) - 1)) * 100 if len(steps) > 1 else 0
    
    st.markdown(
        f"""
        <div class="progress-card" style="border: 2px solid #2563eb !important; background: white !important; border-radius: 12px !important; padding: 1rem !important; margin-bottom: 1rem !important;">
            <div class="progress-header" style="display: flex !important; justify-content: space-between !important; align-items: center !important; margin-bottom: 0.75rem !important;">
                <div class="progress-title" style="font-size: 0.875rem !important; font-weight: 600 !important; color: #1e40af !important;">Refill Progress (UPDATED)</div>
                <div class="progress-percentage" style="font-size: 0.75rem !important; font-weight: 600 !important; color: #059669 !important; background: #ecfdf5 !important; padding: 0.25rem 0.5rem !important; border-radius: 12px !important; border: 1px solid #bbf7d0 !important;">{progress_percentage:.0f}%</div>
            </div>
                        <div class=\"progress-bar\" style=\"width: 100% !important; height: 6px !important; background: #e2e8f0 !important; border-radius: 3px !important; overflow: hidden !important; margin-bottom: 1rem !important;\">\n                <div class=\"progress-bar-filled\" style=\"height: 100% !important; background: linear-gradient(90deg, #2563eb, #059669) !important; transition: width 0.3s ease !important; border-radius: 3px !important; width: {progress_percentage}% !important;\"></div>\n            </div>\n            <div class=\"horizontal-steps-container\" style=\"display: grid !important; grid-template-columns: repeat(5, 1fr) !important; gap: 0.5rem !important; align-items: start !important; position: relative !important; margin-bottom: 1rem !important; width: 100% !important;\">\n                <div class=\"connecting-line\" style=\"position: absolute; top: 14px; left: 10%; right: 10%; height: 2px; background: #e2e8f0; z-index: 0;\"></div>\n                <div class=\"progress-line-filled\" style=\"position: absolute !important; top: 14px !important; left: 10% !important; height: 2px !important; background: linear-gradient(90deg, #2563eb, #059669) !important; z-index: 0 !important; width: {progress_percentage * 0.8}% !important; transition: width 0.3s ease !important;\"></div>
        """,
        unsafe_allow_html=True
    )
    
    for i, (icon, label, _) in enumerate(steps):
        status = ""
        circle_class = ""
        
        if i < current_step:
            status = "step-completed"
            circle_class = "circle-completed"
            display_icon = "✓"
        elif i == current_step:
            status = "step-active"
            circle_class = "circle-active"
            display_icon = icon
        else:
            status = "step-pending"
            circle_class = "circle-pending"
            display_icon = icon
            
        st.markdown(
            f"""
                <div class="progress-step {status}" style="display: inline-flex !important; flex-direction: column !important; align-items: center !important; justify-content: flex-start !important; width: 19% !important; max-width: 60px !important; flex: 0 0 auto !important; z-index: 2 !important; position: relative !important; text-align: center !important;">
                    <div class="step-circle {circle_class}" style="width: 28px !important; height: 28px !important; border-radius: 50% !important; display: flex !important; align-items: center !important; justify-content: center !important; font-size: 0.625rem !important; font-weight: 600 !important; border: 2px solid !important; z-index: 2 !important; margin-bottom: 0.25rem !important; background: white !important;">{display_icon}</div>
                    <div class="step-label" style="font-size: 0.6rem !important; text-align: center !important; font-weight: 500 !important; white-space: nowrap !important; margin-top: 0.125rem !important; line-height: 1.2 !important; max-width: 50px !important;">{label}</div>
                </div>
            """,
            unsafe_allow_html=True
        )
    
    # Add current state indicator
    # Add current state indicator with debugging info\n    state_text = current_state.value if hasattr(current_state, 'value') else str(current_state)\n    state_text_clean = state_text.replace(\"_\", \" \").title()\n    \n    st.markdown(\n        f\"\"\"\n            </div>\n            <div class=\"current-state\" style=\"display: flex !important; justify-content: space-between !important; align-items: center !important; padding: 0.5rem !important; background: #f8fafc !important; border-radius: 8px !important; border: 1px solid #e2e8f0 !important; margin-top: 1rem !important;\">\n                <div class=\"state-label\" style=\"font-size: 0.75rem !important; color: #64748b !important; font-weight: 500 !important;\">Status:</div>\n                <div class=\"state-value\" style=\"font-size: 0.75rem !important; font-weight: 600 !important; color: #1e40af !important; text-transform: capitalize !important;\">{state_text_clean}</div>\n            </div>\n            <div class=\"progress-debug\" style=\"font-size: 0.6rem !important; color: #94a3b8 !important; margin-top: 0.25rem !important; text-align: center !important; background: #f0f9ff !important; padding: 0.25rem !important; border-radius: 4px !important; border: 1px dashed #bfdbfe !important;\">\n                🔄 GRID LAYOUT V2 • Step {current_step + 1}/5 • State: {state_value} • Progress: {progress_percentage:.0f}%\n            </div>\n        </div>\n        \"\"\",\n        unsafe_allow_html=True\n    )