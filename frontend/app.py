"""AdMatch AI - Streamlit multipage app entry point."""
import streamlit as st

st.set_page_config(
    page_title="AdMatch AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "token" not in st.session_state:
    st.session_state["token"] = None
if "user" not in st.session_state:
    st.session_state["user"] = None

home = st.Page("pages/00_home.py", title="Home", icon="🏠", default=True)
login_page = st.Page("pages/01_login.py", title="Login", icon="🔑")
register_page = st.Page("pages/02_register.py", title="Register", icon="📝")
adv_dashboard = st.Page("pages/10_advertiser_dashboard.py", title="Advertiser Dashboard", icon="📊")
adv_profile = st.Page("pages/11_advertiser_profile.py", title="Advertiser Profile", icon="🏢")
creator_dashboard = st.Page("pages/20_creator_dashboard.py", title="Creator Dashboard", icon="🎬")
creator_profile = st.Page("pages/21_creator_profile.py", title="Creator Profile", icon="👤")
matches = st.Page("pages/30_matches.py", title="Matches", icon="🤝")
negotiation = st.Page("pages/31_negotiation.py", title="Negotiation", icon="💬")
history = st.Page("pages/32_history.py", title="History", icon="📋")
pricing_page = st.Page("pages/40_pricing.py", title="Pricing Calculator", icon="💰")
plans_page = st.Page("pages/41_plans.py", title="Plans", icon="💎")
admin_page = st.Page("pages/50_admin.py", title="Admin", icon="📈")
terms_page = st.Page("pages/60_terms.py", title="Terms & Privacy", icon="📜")

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
