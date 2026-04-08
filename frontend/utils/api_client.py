"""HTTP client for Streamlit frontend to call FastAPI backend."""
import os
import httpx
import streamlit as st

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000/api")


def _headers() -> dict:
    token = st.session_state.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def post(path: str, data: dict = None) -> dict:
    r = httpx.post(f"{API_BASE}{path}", json=data, headers=_headers(), timeout=60)
    if r.status_code >= 400:
        detail = r.json().get("detail", r.text) if r.headers.get("content-type", "").startswith("application/json") else r.text
        raise Exception(detail)
    return r.json()


def get(path: str, params: dict = None) -> dict | list:
    r = httpx.get(f"{API_BASE}{path}", params=params, headers=_headers(), timeout=60)
    if r.status_code >= 400:
        detail = r.json().get("detail", r.text) if r.headers.get("content-type", "").startswith("application/json") else r.text
        raise Exception(detail)
    return r.json()


def put(path: str, data: dict = None) -> dict:
    r = httpx.put(f"{API_BASE}{path}", json=data, headers=_headers(), timeout=60)
    if r.status_code >= 400:
        detail = r.json().get("detail", r.text) if r.headers.get("content-type", "").startswith("application/json") else r.text
        raise Exception(detail)
    return r.json()


def register(email: str, password: str, role: str, display_name: str) -> dict:
    result = post("/auth/register", {"email": email, "password": password, "role": role, "display_name": display_name})
    st.session_state["token"] = result["access_token"]
    st.session_state["user"] = result["user"]
    return result


def login(email: str, password: str) -> dict:
    result = post("/auth/login", {"email": email, "password": password})
    st.session_state["token"] = result["access_token"]
    st.session_state["user"] = result["user"]
    return result


def logout():
    st.session_state.pop("token", None)
    st.session_state.pop("user", None)


def is_logged_in() -> bool:
    return "token" in st.session_state and st.session_state["token"]


def current_user() -> dict | None:
    return st.session_state.get("user")


def require_login():
    if not is_logged_in():
        st.warning("Please login first")
        st.switch_page("pages/01_login.py")
        st.stop()
