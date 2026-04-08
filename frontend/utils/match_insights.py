"""Generate human-readable match insights from scores."""


def generate_match_insight(scores: dict) -> str:
    """Generate a one-line Chinese explanation of why this match scored the way it did."""
    emb = scores.get("embedding_score", 0)
    aud = scores.get("audience_score", 0)
    bud = scores.get("budget_score", 0)
    val = scores.get("values_score", 0)

    strengths = []
    weaknesses = []

    if emb >= 0.7:
        strengths.append("內容方向高度契合")
    elif emb >= 0.4:
        strengths.append("內容方向有交集")
    else:
        weaknesses.append("內容方向差異較大")

    if aud >= 0.7:
        strengths.append("受眾群體匹配度高")
    elif aud >= 0.4:
        pass  # neutral, skip
    else:
        weaknesses.append("受眾契合度偏低")

    if bud >= 0.8:
        strengths.append("預算完美吻合")
    elif bud >= 0.5:
        strengths.append("預算範圍合理")
    else:
        weaknesses.append("預算差距較大")

    if val >= 0.6:
        strengths.append("價值觀高度吻合")
    elif val >= 0.3:
        pass  # neutral
    else:
        weaknesses.append("價值觀有分歧")

    parts = []
    if strengths:
        parts.append("**優勢：**" + "、".join(strengths))
    if weaknesses:
        parts.append("**注意：**" + "、".join(weaknesses))

    if not parts:
        return "各維度表現均衡，建議進一步了解。"
    return "　".join(parts)


def get_match_verdict(weighted_score: float) -> tuple[str, str]:
    """Return (emoji, label) verdict for a weighted score."""
    if weighted_score >= 0.75:
        return "🟢", "強烈推薦"
    elif weighted_score >= 0.55:
        return "🟡", "值得考慮"
    elif weighted_score >= 0.35:
        return "🟠", "條件性推薦"
    else:
        return "🔴", "匹配度較低"
