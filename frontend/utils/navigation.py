"""Navigation helpers for role-based redirects."""
import streamlit as st
from frontend.utils.api_client import current_user


def redirect_to_dashboard():
    """Redirect logged-in user to their role-specific dashboard."""
    user = current_user()
    if not user:
        return
    if user.get("role") == "advertiser":
        st.switch_page("pages/10_advertiser_dashboard.py")
    else:
        st.switch_page("pages/20_creator_dashboard.py")
