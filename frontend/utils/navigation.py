"""Navigation helpers for role-based redirects.

Handles dual context: local dev uses frontend/app.py as main script
(paths like pages/X.py) while HF Space uses hf_streamlit_app.py
(paths like frontend/pages/X.py).
"""
import os
import sys
import streamlit as st
from frontend.utils.api_client import current_user


def _is_hf_context() -> bool:
    """Detect if running under hf_streamlit_app.py (HF Space).

    Streamlit exposes the main script via runtime API. HF Space runs
    hf_streamlit_app.py at project root, local dev runs frontend/app.py.
    Cache the result since it doesn't change within a session.
    """
    if hasattr(_is_hf_context, "_cached"):
        return _is_hf_context._cached
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        ctx = get_script_run_ctx()
        if ctx and ctx.main_script_path:
            result = "hf_streamlit_app" in ctx.main_script_path
            _is_hf_context._cached = result
            return result
    except Exception:
        pass
    # Fallback: check if we're running from the HF folder structure
    cwd = os.getcwd()
    result = os.path.basename(cwd) == "app" or os.path.exists("hf_streamlit_app.py")
    _is_hf_context._cached = result
    return result


def page(filename: str) -> str:
    """Return the correct page path for the current execution context.

    Args:
        filename: Page filename like '00_home.py' or '10_advertiser_dashboard.py'
    Returns:
        Path usable with st.switch_page() in current context.
    """
    if _is_hf_context():
        return f"frontend/pages/{filename}"
    return f"pages/{filename}"


def switch(filename: str):
    """Context-aware st.switch_page wrapper."""
    st.switch_page(page(filename))


def redirect_to_dashboard():
    """Redirect logged-in user to their role-specific dashboard."""
    user = current_user()
    if not user:
        return
    if user.get("role") == "advertiser":
        switch("10_advertiser_dashboard.py")
    else:
        switch("20_creator_dashboard.py")
