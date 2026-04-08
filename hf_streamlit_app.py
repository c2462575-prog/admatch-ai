"""HuggingFace Spaces Streamlit entry point.
Starts API server in background, then runs Streamlit app.
"""
import hf_app  # This initializes DB + starts API in background thread

# Now import and run the actual Streamlit app
import streamlit as st

st.set_page_config(
    page_title="AdMatch AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "token" not in st.session_state:
    st.session_state["token"] = None
if "user" not in st.session_state:
    st.session_state["user"] = None

home = st.Page("frontend/pages/00_home.py", title="Home", icon="🏠", default=True)
login_page = st.Page("frontend/pages/01_login.py", title="Login", icon="🔑")
register_page = st.Page("frontend/pages/02_register.py", title="Register", icon="📝")
adv_dashboard = st.Page("frontend/pages/10_advertiser_dashboard.py", title="Advertiser Dashboard", icon="📊")
adv_profile = st.Page("frontend/pages/11_advertiser_profile.py", title="Advertiser Profile", icon="🏢")
creator_dashboard = st.Page("frontend/pages/20_creator_dashboard.py", title="Creator Dashboard", icon="🎬")
creator_profile = st.Page("frontend/pages/21_creator_profile.py", title="Creator Profile", icon="👤")
matches = st.Page("frontend/pages/30_matches.py", title="Matches", icon="🤝")
negotiation = st.Page("frontend/pages/31_negotiation.py", title="Negotiation", icon="💬")
history = st.Page("frontend/pages/32_history.py", title="History", icon="📋")
pricing_page = st.Page("frontend/pages/40_pricing.py", title="Pricing Calculator", icon="💰")
plans_page = st.Page("frontend/pages/41_plans.py", title="Plans", icon="💎")
admin_page = st.Page("frontend/pages/50_admin.py", title="Admin", icon="📈")
terms_page = st.Page("frontend/pages/60_terms.py", title="Terms & Privacy", icon="📜")

user = st.session_state.get("user")

if user and user.get("role") == "advertiser":
    pages = {
        "": [home],
        "Dashboard": [adv_dashboard, adv_profile],
        "Matching": [matches, negotiation, history],
        "Tools": [pricing_page, plans_page, admin_page, terms_page],
    }
elif user and user.get("role") == "creator":
    pages = {
        "": [home],
        "Dashboard": [creator_dashboard, creator_profile],
        "Matching": [matches, negotiation, history],
        "Tools": [pricing_page, plans_page, admin_page, terms_page],
    }
else:
    pages = {
        "": [home],
        "Account": [login_page, register_page],
        "Tools": [pricing_page, plans_page, admin_page, terms_page],
    }

pg = st.navigation(pages)
pg.run()
