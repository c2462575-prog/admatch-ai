"""
Price Calculator - 創作者報價計算工具
"""

CATEGORY_MULTIPLIERS = {
    "tech": 1.3,
    "finance": 1.25,
    "beauty": 1.1,
    "lifestyle": 1.0,
    "food": 1.0,
    "travel": 1.05,
}


def calculate_creator_price(followers: int, engagement_rate: float, category: str) -> dict:
    """根據創作者數據計算建議報價"""
    cpm = 50  # base cost per 1000 followers (TWD)
    base = followers / 1000 * cpm * engagement_rate * 100
    multiplier = CATEGORY_MULTIPLIERS.get(category, 1.0)
    base_price = round(base * multiplier, 2)
    return {
        "base_price": base_price,
        "suggested_range": (round(base_price * 0.8, 2), round(base_price * 1.2, 2)),
    }


def estimate_roi(price: float, expected_reach: int, conversion_rate: float) -> dict:
    """估算廣告投放 ROI"""
    if price <= 0:
        raise ValueError("price must be positive")
    estimated_conversions = expected_reach * conversion_rate
    cost_per_conversion = price / estimated_conversions if estimated_conversions > 0 else float("inf")
    roi_score = estimated_conversions / price * 1000
    return {
        "estimated_conversions": round(estimated_conversions, 2),
        "cost_per_conversion": round(cost_per_conversion, 2),
        "roi_score": round(roi_score, 4),
    }
