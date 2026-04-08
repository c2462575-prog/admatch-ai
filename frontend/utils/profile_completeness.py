"""Profile completeness calculator — drives user engagement via Zeigarnik effect."""
import streamlit as st


def advertiser_completeness(profile: dict) -> tuple[float, list[str]]:
    """Calculate advertiser profile completeness. Returns (0-1 score, list of missing items)."""
    checks = [
        (bool(profile.get("industry")), "選擇行業"),
        (len(profile.get("description", "")) > 20, "撰寫品牌描述（至少 20 字）"),
        (profile.get("budget_value", 0) > 0, "設定推廣預算"),
        (bool(profile.get("target_audience")), "選擇目標受眾"),
        (len(profile.get("values", [])) >= 2, "選擇至少 2 個品牌價值觀"),
        (bool(profile.get("campaign_goal")), "選擇推廣目標"),
    ]
    done = sum(1 for ok, _ in checks if ok)
    missing = [label for ok, label in checks if not ok]
    return done / len(checks), missing


def creator_completeness(profile: dict) -> tuple[float, list[str]]:
    """Calculate creator profile completeness."""
    checks = [
        (bool(profile.get("niche")), "選擇內容領域"),
        (len(profile.get("description", "")) > 20, "撰寫頻道描述（至少 20 字）"),
        (profile.get("follower_count", 0) > 0, "填寫粉絲數量"),
        (profile.get("engagement_rate", 0) > 0, "設定互動率"),
        (profile.get("min_fee", 0) > 0, "設定最低報價"),
        (len(profile.get("values", [])) >= 2, "選擇至少 2 個核心價值觀"),
        (len(profile.get("content_style", [])) >= 1, "選擇內容風格標籤"),
        (len(profile.get("audience_description", "")) > 10, "描述粉絲群體"),
    ]
    done = sum(1 for ok, _ in checks if ok)
    missing = [label for ok, label in checks if not ok]
    return done / len(checks), missing


def show_completeness_bar(score: float, missing: list[str], role: str):
    """Display a visual completeness bar with missing items."""
    label = "品牌資料" if role == "advertiser" else "頻道資料"

    if score >= 1.0:
        st.success(f"✅ {label}完整度：100% — 已準備好進行 AI 匹配！")
    else:
        pct = int(score * 100)
        color = "🟢" if pct >= 80 else "🟡" if pct >= 50 else "🔴"
        st.progress(score, text=f"{color} {label}完整度：{pct}%")
        if missing:
            with st.expander(f"還有 {len(missing)} 項未完成"):
                for item in missing:
                    st.markdown(f"- {item}")
