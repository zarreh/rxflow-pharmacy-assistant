"""
Debug and monitoring components for RxFlow Pharmacy Assistant

This module contains debug information, tool logs, cost analysis,
and state visualization components.
"""

import streamlit as st
from datetime import datetime
from typing import Dict, List, Any


def render_debug_tabs(
    current_state,
    tool_logs: List[Dict],
    cost_savings: Dict[str, Any]
) -> None:
    """
    Render debug information in tabbed interface.
    
    Args:
        current_state: Current workflow state
        tool_logs: List of tool execution logs
        cost_savings: Cost savings data
    """
    tab1, tab2, tab3 = st.tabs(["State", "Tools", "Savings"])
    
    with tab1:
        render_state_visualization(current_state)
    
    with tab2:
        render_tool_logs(tool_logs)
    
    with tab3:
        render_cost_savings(cost_savings)


def render_state_visualization(current_state) -> None:
    """
    Render workflow state visualization.
    
    Args:
        current_state: Current workflow state
    """
    from rxflow.workflow.workflow_types import WorkflowState
    
    # State indicator with modern design
    state_colors = {
        WorkflowState.GREETING: "👋",
        WorkflowState.PROCESSING: "⚡",
        WorkflowState.ESCALATED: "🚨",
        WorkflowState.COMPLETED: "✅",
        WorkflowState.ERROR: "❌",
    }

    state_icon = state_colors.get(current_state, "⚪")
    
    is_active = current_state in [WorkflowState.GREETING, WorkflowState.PROCESSING]
    
    st.markdown(
        f"""
        <div class="state-indicator {'active' if is_active else ''}">
            {state_icon} {current_state.value.replace('_', ' ').title()}
        </div>
        """,
        unsafe_allow_html=True
    )

    # Progress indicator with enhanced styling
    state_order = [
        WorkflowState.GREETING,
        WorkflowState.PROCESSING,
        WorkflowState.COMPLETED,
    ]

    if current_state in state_order:
        progress = (state_order.index(current_state) + 1) / len(state_order)
        st.progress(progress)
        st.markdown(f"**Progress:** {progress:.0%}")
    elif current_state == WorkflowState.ESCALATED:
        st.warning("🏥 Your case has been escalated to a pharmacist for review")
    elif current_state == WorkflowState.ERROR:
        st.error("❌ An error occurred. Please try again or contact support.")


def render_tool_logs(tool_logs: List[Dict]) -> None:
    """
    Display recent tool usage logs.
    
    Args:
        tool_logs: List of tool execution logs
    """
    if not tool_logs:
        st.markdown(
            """
            <div class="info-card">
                <h3>🔧 Tool Usage Log</h3>
                <p style="color: #6b7280;">No tools have been used yet. Start a conversation to see tool activity.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    st.markdown(
        """
        <div class="info-card">
            <h3>🔧 Recent Tool Activity</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Show recent tools first
    recent_logs = sorted(
        tool_logs, key=lambda x: x["timestamp"], reverse=True
    )

    for log in recent_logs[:5]:  # Show last 5 tool calls
        timestamp = datetime.fromisoformat(log["timestamp"]).strftime("%H:%M:%S")
        success_icon = "✅" if log["success"] else "❌"

        with st.expander(f"{success_icon} {log['tool']} - {timestamp}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Execution Time", f"{log['execution_time']:.2f}s")
            with col2:
                st.metric("Status", "Success" if log["success"] else "Failed")
            with col3:
                st.metric("Input Length", f"{len(log['input'])} chars")
            
            st.text_area("Input Details", log['input'][:200] + "..." if len(log['input']) > 200 else log['input'], height=100)


def render_cost_savings(cost_savings: Dict[str, Any]) -> None:
    """
    Display potential cost savings information.
    
    Args:
        cost_savings: Cost savings data dictionary
    """
    if cost_savings["total_saved"] > 0:
        st.markdown(
            f"""
            <div class="cost-savings">
                <h3>💰 Total Savings</h3>
                <p>${cost_savings['total_saved']:.2f}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if cost_savings["comparisons"]:
            st.markdown("### Recent Price Comparisons")
            
            for comparison in cost_savings["comparisons"][-3:]:  # Show last 3
                with st.container():
                    st.markdown(f"**💊 {comparison['medication']}**")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(
                            f"""
                            <div class="metric-card">
                                <div class="metric-label">Original Price</div>
                                <div class="metric-value">${comparison['original_price']:.2f}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    with col2:
                        st.markdown(
                            f"""
                            <div class="metric-card">
                                <div class="metric-label">Best Price</div>
                                <div class="metric-value">${comparison['best_price']:.2f}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    with col3:
                        st.markdown(
                            f"""
                            <div class="metric-card">
                                <div class="metric-label">You Save</div>
                                <div class="metric-value">${comparison['savings']:.2f}</div>
                                <div class="metric-delta">↓ {(comparison['savings'] / comparison['original_price'] * 100):.0f}%</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    
                    st.info(f"💡 Best source: **{comparison['source']}**")
                    st.markdown("---")
    else:
        st.markdown(
            """
            <div class="info-card">
                <h3>💰 Cost Analysis</h3>
                <p style="color: #6b7280;">No cost comparisons available yet. Ask about medication prices to see potential savings!</p>
            </div>
            """,
            unsafe_allow_html=True
        )