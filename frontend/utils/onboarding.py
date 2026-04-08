"""Onboarding checklist for new users."""
import streamlit as st
from frontend.utils.api_client import get


def show_advertiser_onboarding():
    """Show onboarding checklist for advertisers. Returns True if profile exists."""
    has_profile = False
    has_matches = False
    try:
        profile = get("/advertisers/profile")
        has_profile = bool(profile.get("industry"))
    except Exception:
        pass
    try:
        matches = get("/matching/results")
        has_matches = len(matches) > 0
    except Exception:
        pass

    if has_profile and has_matches:
        return True

    st.markdown("### 🚀 快速開始")
    with st.container(border=True):
        step1 = "~~1. 填寫品牌資料~~  ✅" if has_profile else "**1. 填寫品牌資料** ← 從這裡開始"
        step2 = "~~2. 執行 AI 匹配~~  ✅" if has_matches else "**2. 執行 AI 匹配**"
        step3 = "**3. 查看匹配結果並開始談判**"

        st.markdown(step1)
        st.markdown(step2)
        st.markdown(step3)

        if not has_profile:
            st.warning("請先完成品牌資料，才能開始匹配！")
            if st.button("📝 立即填寫品牌資料", type="primary", use_container_width=True, key="onboard_profile"):
                st.switch_page("pages/11_advertiser_profile.py")
        elif not has_matches:
            st.info("品牌資料已完成！現在可以開始 AI 匹配了。")
            if st.button("🔍 開始 AI 匹配", type="primary", use_container_width=True, key="onboard_match"):
                st.switch_page("pages/30_matches.py")

    return has_profile


def show_creator_onboarding():
    """Show onboarding checklist for creators. Returns True if profile exists."""
    has_profile = False
    has_matches = False
    try:
        profile = get("/creators/profile")
        has_profile = bool(profile.get("niche"))
    except Exception:
        pass
    try:
        matches = get("/matching/results")
        has_matches = len(matches) > 0
    except Exception:
        pass

    if has_profile and has_matches:
        return True

    st.markdown("### 🚀 快速開始")
    with st.container(border=True):
        step1 = "~~1. 填寫頻道資料~~  ✅" if has_profile else "**1. 填寫頻道資料** ← 從這裡開始"
        step2 = "~~2. 執行 AI 匹配~~  ✅" if has_matches else "**2. 執行 AI 匹配**"
        step3 = "**3. 查看品牌配對並開始談判**"

        st.markdown(step1)
        st.markdown(step2)
        st.markdown(step3)

        if not has_profile:
            st.warning("請先完成頻道資料，才能開始匹配！")
            if st.button("📝 立即填寫頻道資料", type="primary", use_container_width=True, key="onboard_profile"):
                st.switch_page("pages/21_creator_profile.py")
        elif not has_matches:
            st.info("頻道資料已完成！現在可以開始 AI 匹配了。")
            if st.button("🔍 開始 AI 匹配", type="primary", use_container_width=True, key="onboard_match"):
                st.switch_page("pages/30_matches.py")

    return has_profile
