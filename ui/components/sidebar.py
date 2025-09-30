"""
Sidebar components for RxFlow Pharmacy Assistant

This module contains sidebar-related UI components including patient selection,
quick links, and session management controls.
"""

import streamlit as st
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Callable


def render_sidebar(
    demo_data: Dict[str, Any], 
    patient_id: str, 
    session_start_time: datetime,
    session_id: str,
    current_state,
    show_debug_info: bool,
    reset_callback: Callable,
    export_callback: Callable
) -> tuple:
    """
    Render sidebar with application configuration and session management.
    
    Args:
        demo_data: Demo data dictionary
        patient_id: Current patient ID
        session_start_time: When the session started
        session_id: Current session ID
        current_state: Current workflow state
        show_debug_info: Whether to show debug information
        reset_callback: Function to call when resetting conversation
        export_callback: Function to call when exporting session data
        
    Returns:
        tuple: (selected_patient_id, show_debug_info_updated)
    """
    # Clean, focused sidebar
    st.sidebar.markdown(
        """
        <div class="sidebar-section">
            <div class="sidebar-title">👤 Current Patient</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Render patient context card at top of sidebar (always John Smith)
    render_patient_context_sidebar(demo_data, "patient_001")
    
    selected_patient = "patient_001"  # Always default to John Smith

    # Quick Links
    render_quick_links(demo_data, "patient_001")
    
    # Recent Activity
    render_recent_activity_sidebar()
    
    # Help & Support
    render_help_support(reset_callback)
    
    # Advanced options
    updated_debug_info = render_advanced_options(
        show_debug_info, 
        export_callback, 
        session_start_time, 
        session_id, 
        current_state
    )
    
    return selected_patient, updated_debug_info


def render_patient_context_sidebar(demo_data: Dict[str, Any], patient_id: str) -> None:
    """
    Render patient context card in sidebar with current patient information.
    
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
        
        st.sidebar.markdown(
            f"""
            <div class="sidebar-card">
                <div class="patient-info">
                    <div class="patient-avatar">{patient['name'][0]}</div>
                    <div>
                        <h4>{patient['name']}</h4>
                        <div class="patient-id">Patient ID: {patient_id}</div>
                    </div>
                </div>
                <div class="patient-details">
                    <div class="detail-item">
                        <div class="detail-label">INSURANCE</div>
                        <div class="detail-value">{patient.get('insurance_id', 'N/A')}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">MEDICATIONS</div>
                        <div class="detail-value">{total_meds} Active</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">LAST REFILL</div>
                        <div class="detail-value">2 weeks ago</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_recent_activity_sidebar() -> None:
    """
    Render recent activity in sidebar using real data from submitted_orders.json.
    """
    st.sidebar.markdown(
        """
        <div class="sidebar-section">
            <div class="sidebar-title">🕐 Recent Activity</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    try:
        # Load submitted orders data
        orders_file = Path("data/submitted_orders.json")
        if orders_file.exists():
            with open(orders_file, 'r') as f:
                orders = json.load(f)
            
            # Filter orders for patient_001 and get recent ones
            recent_orders = []
            for order in orders:
                if order.get("patient_id") == "patient_001":
                    recent_orders.append(order)
                # Also include orders with old patient_id "12345" as they're for John Smith
                elif order.get("patient_id") == "12345":
                    recent_orders.append(order)
            
            # Sort by order_time (most recent first) and take top 3
            recent_orders.sort(key=lambda x: x.get("order_time", ""), reverse=True)
            recent_orders = recent_orders[:3]
            
            # Display recent activities
            for order in recent_orders:
                medication = order.get("medication", "Unknown").title()
                dosage = order.get("dosage", "")
                status = order.get("status", "unknown")
                order_time = order.get("order_time", "")
                
                # Calculate time ago
                from datetime import datetime, timezone
                try:
                    if order_time:
                        order_dt = datetime.fromisoformat(order_time.replace('Z', '+00:00'))
                        now = datetime.now(timezone.utc)
                        diff = now - order_dt
                        
                        if diff.days > 0:
                            time_ago = f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
                        elif diff.seconds > 3600:
                            hours = diff.seconds // 3600
                            time_ago = f"{hours} hour{'s' if hours > 1 else ''} ago"
                        else:
                            minutes = diff.seconds // 60
                            time_ago = f"{minutes} minute{'s' if minutes > 1 else ''} ago"
                    else:
                        time_ago = "Recently"
                except:
                    time_ago = "Recently"
                
                # Choose appropriate icon and format
                if status == "received":
                    icon = "💊"
                    activity_text = f"{medication} {dosage} refilled"
                else:
                    icon = "📋"
                    activity_text = f"{medication} ordered"
                
                st.sidebar.markdown(
                    f"""
                    <div class="activity-item">
                        <div class="activity-icon">{icon}</div>
                        <div class="activity-content">
                            <div class="activity-title">{activity_text}</div>
                            <div class="activity-time">{time_ago}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            # Fallback if no orders file
            st.sidebar.info("No recent activity found.")
            
    except Exception as e:
        st.sidebar.error(f"Error loading recent activity: {str(e)}")


def render_quick_links(demo_data: Dict[str, Any], patient_id: str) -> None:
    """Render quick links section in sidebar with real data."""
    st.sidebar.markdown(
        """
        <div class="sidebar-section">
            <div class="sidebar-title">⚡ Quick Links</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if st.sidebar.button("📋 View Medical History", use_container_width=True, type="secondary"):
        show_medical_history(demo_data, patient_id)
        
    if st.sidebar.button("💳 Insurance Info", use_container_width=True, type="secondary"):
        show_insurance_info(demo_data, patient_id)
        
    if st.sidebar.button("📞 Contact Pharmacy", use_container_width=True, type="secondary"):
        show_pharmacy_contacts(demo_data)


def render_help_support(reset_callback: Callable) -> None:
    """Render help and support section in sidebar."""
    st.sidebar.markdown(
        """
        <div class="sidebar-section">
            <div class="sidebar-title">❓ Help & Support</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if st.sidebar.button("📚 User Guide", use_container_width=True, type="secondary"):
        show_user_guide()
        
    if st.sidebar.button("🔄 Reset Conversation", use_container_width=True, type="secondary"):
        reset_callback()
        st.sidebar.success("✅ Conversation reset successfully!")


def show_user_guide() -> None:
    """Display user guide information."""
    with st.sidebar.expander("📚 User Guide", expanded=True):
        st.markdown("### How to Use RxFlow")
        st.markdown("""
        **Getting Started:**
        1. Select your patient profile from the dropdown
        2. Use Quick Actions for common tasks
        3. Type messages in the chat to interact with the AI assistant
        
        **Available Features:**
        - � **Prescription Refills**: Request refills for your medications
        - 🏥 **Find Pharmacies**: Locate nearby pharmacies and compare prices
        - 💰 **Price Comparison**: Check medication costs across different sources
        - 📋 **Medical History**: View your current medications and history
        - 💳 **Insurance Info**: Check coverage and copay information
        
        **Quick Actions:**
        - Use the buttons in the right panel for common requests
        - View your medical history and insurance info in the sidebar
        - Contact pharmacies directly using the provided contact information
        
        **Tips:**
        - Be specific about which medication you need
        - Mention your preferred pharmacy if you have one
        - Ask about generic alternatives to save money
        - Check your insurance coverage before requesting refills
        """)
        
        st.markdown("### Need Help?")
        st.info("💡 If you have questions, try asking the AI assistant or use the Quick Actions for guided workflows.")
        
        st.markdown("### Privacy & Security")
        st.markdown("🔒 This is a demo application using mock data. No real patient information is processed or stored.")


def render_advanced_options(
    show_debug_info: bool,
    export_callback: Callable,
    session_start_time: datetime,
    session_id: str,
    current_state
) -> bool:
    """Render advanced options expandable section."""
    with st.sidebar.expander("⚙️ Advanced Options"):
        updated_debug_info = st.checkbox(
            "Show Debug Info", value=show_debug_info
        )
        
        if st.button("📊 Export Session Data", use_container_width=True):
            export_callback()
            st.success("📥 Session data prepared for download!")
        
        # Only show technical details if debug mode is on
        if updated_debug_info:
            st.markdown("### 🔧 Technical Details")
            session_duration = datetime.now() - session_start_time
            st.text(f"Session: {session_id[:8]}...")
            st.text(f"Duration: {str(session_duration).split('.')[0]}")
            st.text(f"State: {current_state.value}")
    
    return updated_debug_info


def show_medical_history(demo_data: Dict[str, Any], patient_id: str) -> None:
    """Display patient's medical history and current medications."""
    if not demo_data.get("patients") or patient_id not in demo_data["patients"]:
        st.sidebar.error("Patient data not found!")
        return
    
    patient = demo_data["patients"][patient_id]
    
    with st.sidebar.expander("📋 Medical History", expanded=True):
        st.markdown(f"**Patient:** {patient['name']}")
        st.markdown(f"**DOB:** {patient['date_of_birth']}")
        st.markdown(f"**Phone:** {patient.get('phone', 'N/A')}")
        
        st.markdown("### Current Medications")
        if patient.get("current_medications"):
            for med in patient["current_medications"]:
                st.markdown(f"• **{med['name']}** {med['strength']}")
                st.markdown(f"  - Prescribed by: {med['prescriber']}")
                st.markdown(f"  - Start date: {med['start_date']}")
                st.markdown("---")
        else:
            st.info("No current medications on file")
            
        # Show medication history if available
        if patient.get("medication_history"):
            st.markdown("### Recent Refills")
            for refill in patient["medication_history"][-3:]:  # Show last 3 refills
                st.markdown(f"• **{refill.get('medication', 'Unknown')}** - {refill.get('date', 'Unknown date')}")


def show_insurance_info(demo_data: Dict[str, Any], patient_id: str) -> None:
    """Display patient's insurance information and coverage details."""
    if not demo_data.get("patients") or patient_id not in demo_data["patients"]:
        st.sidebar.error("Patient data not found!")
        return
    
    patient = demo_data["patients"][patient_id]
    insurance_id = patient.get("insurance_id")
    
    if not insurance_id or not demo_data.get("insurance") or insurance_id not in demo_data["insurance"]:
        st.sidebar.error("Insurance information not found!")
        return
    
    insurance = demo_data["insurance"][insurance_id]
    
    with st.sidebar.expander("💳 Insurance Information", expanded=True):
        st.markdown(f"**Plan:** {insurance['name']}")
        st.markdown(f"**Type:** {insurance['type'].title()}")
        st.markdown(f"**Member ID:** {insurance_id}")
        
        st.markdown("### Coverage Tiers")
        tier_structure = insurance.get("tier_structure", {})
        for tier_name, tier_info in tier_structure.items():
            tier_num = tier_name.replace("tier_", "Tier ")
            st.markdown(f"**{tier_num}:** ${tier_info['copay']} - {tier_info['description']}")
        
        # Show coverage for current medications
        if patient.get("current_medications"):
            st.markdown("### Your Medication Coverage")
            covered_drugs = insurance.get("covered_drugs", {})
            for med in patient["current_medications"]:
                med_name = med["name"].lower()
                if med_name in covered_drugs:
                    coverage = covered_drugs[med_name]
                    st.markdown(f"• **{med['name']}**: Tier {coverage['tier']}, ${coverage['copay']} copay")
                else:
                    st.markdown(f"• **{med['name']}**: Coverage unknown")


def show_pharmacy_contacts(demo_data: Dict[str, Any]) -> None:
    """Display nearby pharmacy contact information."""
    if not demo_data.get("pharmacies"):
        st.sidebar.error("Pharmacy data not found!")
        return
    
    with st.sidebar.expander("📞 Pharmacy Contacts", expanded=True):
        st.markdown("### Nearby Pharmacies")
        
        # Show first 3 pharmacies
        pharmacy_items = list(demo_data["pharmacies"].items())[:3]
        
        for pharmacy_id, pharmacy in pharmacy_items:
            st.markdown(f"**{pharmacy['name']}**")
            st.markdown(f"📞 {pharmacy['phone']}")
            
            # Show address
            address = pharmacy.get("address", {})
            if address:
                st.markdown(f"📍 {address.get('street', '')}, {address.get('city', '')}, {address.get('state', '')} {address.get('zip', '')}")
            
            # Show hours
            if pharmacy.get("hours"):
                st.markdown(f"🕒 {pharmacy['hours']}")
            
            # Show services
            if pharmacy.get("services"):
                services = ", ".join(pharmacy["services"]).replace("_", " ").title()
                st.markdown(f"🔧 Services: {services}")
            
            st.markdown("---")
        
        st.info("💡 Click 'Find Pharmacy' in Quick Actions to see more options and compare prices!")