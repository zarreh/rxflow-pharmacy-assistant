"""
Styling utilities for RxFlow Pharmacy Assistant

This module handles CSS loading and styling utilities for the Streamlit interface.
"""

from pathlib import Path
import streamlit as st


def load_css() -> str:
    """
    Load CSS from external file.
    
    Returns:
        str: CSS content as string
    """
    css_file = Path(__file__).parent.parent.parent / "static" / "css" / "styles.css"
    
    try:
        with open(css_file, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"CSS file not found: {css_file}")
        return ""
    except Exception as e:
        st.error(f"Error loading CSS: {e}")
        return ""


def apply_custom_css() -> None:
    """
    Apply custom CSS styles to the Streamlit app.
    
    This function loads the external CSS file and injects it into the Streamlit app.
    """
    css_content = load_css()
    if css_content:
        # Add cache-busting comment
        import time
        cache_buster = f"/* Cache buster: {int(time.time())} */"
        st.markdown(f"<style>{cache_buster}\n{css_content}</style>", unsafe_allow_html=True)


def get_page_config() -> dict:
    """
    Get page configuration for Streamlit.
    
    Returns:
        dict: Page configuration parameters
    """
    return {
        "page_title": "RxFlow Pharmacy Assistant",
        "page_icon": "💊",
        "layout": "wide",
        "initial_sidebar_state": "expanded",
    }