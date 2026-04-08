# -*- coding: utf-8 -*-
"""
Advertiser Agent - Analyzes advertiser profile and handles negotiation
"""

import json
from typing import Optional
from model_router import ModelRouter


class AdvertiserAgent:
    """Agent representing an advertiser in the matching and negotiation process"""

    def __init__(self, advertiser_data: dict, router: ModelRouter):
        self.data = advertiser_data
        self.router = router
        self.profile = None
        self.id = advertiser_data.get("id", "unknown")
        self.name = advertiser_data.get("name", "Unknown Advertiser")

    def analyze_profile(self) -> Optional[dict]:
        """
        Deep analysis of advertiser profile using PRO/HIGH

        Returns:
            Structured profile dict with analysis results
        """
        prompt = f"""你是一位专业的广告策略分析师。请深入分析以下广告主的信息，并输出结构化的JSON分析结果。

广告主信息：
{json.dumps(self.data, ensure_ascii=False, indent=2)}

请分析并输出以下JSON格式（直接输出JSON，不要添加markdown代码块标记）：
{{
    "campaign_summary": "推广活动的核心目标和策略摘要（50-100字）",
    "ideal_partner_traits": ["理想合作创作者的特征1", "特征2", "特征3"],
    "negotiation_priorities": {{
        "must_have": ["必须满足的条件"],
        "nice_to_have": ["希望但可协商的条件"],
        "dealbreakers": ["无法接受的条件"]
    }},
    "budget_strategy": {{
        "initial_offer_ratio": 0.7,
        "max_offer_ratio": 1.0,
        "preferred_payment_model": "按效果付费/固定费用/混合模式"
    }},
    "embedding_description": "用于匹配算法的简短描述（100字以内）"
}}"""

        response = self.router.generate_content(
            task=f"advertiser_analysis_{self.id}",
            prompt=prompt,
            model_key="PRO",
            thinking_level="HIGH"
        )

        if response:
            try:
                # Try to parse JSON from response
                # Handle potential markdown code blocks
                clean_response = response.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])

                self.profile = json.loads(clean_response)
                print(f"[Advertiser Agent] {self.name} profile analyzed successfully")
                return self.profile
            except json.JSONDecodeError as e:
                print(f"[Advertiser Agent] Failed to parse profile JSON: {e}")
                # Create minimal profile from raw response
                self.profile = {
                    "campaign_summary": response[:200],
                    "ideal_partner_traits": [],
                    "negotiation_priorities": {"must_have": [], "nice_to_have": [], "dealbreakers": []},
                    "budget_strategy": {"initial_offer_ratio": 0.7, "max_offer_ratio": 1.0},
                    "embedding_description": self.data.get("description", "")[:100]
                }
                return self.profile

        return None

    def generate_offer(self, creator_data: dict, round_num: int, previous_response: str = None) -> Optional[str]:
        """
        Generate negotiation offer using PRO/MEDIUM

        Args:
            creator_data: Creator's profile data
            round_num: Current negotiation round (1-3)
            previous_response: Creator's previous response (for rounds 2-3)

        Returns:
            Offer text
        """
        context = f"""你是广告主"{self.name}"的谈判代表。

广告主信息：
{json.dumps(self.data, ensure_ascii=False, indent=2)}

创作者信息：
{json.dumps(creator_data, ensure_ascii=False, indent=2)}

当前是第{round_num}轮谈判。"""

        if round_num == 1:
            prompt = context + """

请生成初始合作邀约，包括：
1. 简短的自我介绍和合作意向
2. 初步的合作方案建议
3. 预算范围（可以略低于最高预算作为起点）
4. 期望的内容形式和发布安排

直接输出邀约内容，使用中文，控制在200字以内。"""
        elif round_num == 2:
            prompt = context + f"""

创作者的回应：
{previous_response}

请根据创作者的回应，调整合作方案：
1. 回应创作者提出的关切或要求
2. 适当提高预算（如有必要）
3. 就具体细节进行协商
4. 保持合作诚意

直接输出回应内容，使用中文，控制在200字以内。"""
        else:  # round 3
            prompt = context + f"""

创作者的回应：
{previous_response}

这是最终轮谈判，请：
1. 做出最终报价
2. 明确所有合作条款
3. 表达合作期待或遗憾

直接输出最终回应，使用中文，控制在200字以内。"""

        response = self.router.generate_content(
            task=f"advertiser_negotiation_{self.id}_round{round_num}",
            prompt=prompt,
            model_key="PRO",
            thinking_level="MEDIUM"
        )

        return response

    def decide_final_outcome(self, negotiation_history: list) -> dict:
        """
        Decide final negotiation outcome

        Returns:
            Dict with decision and reasoning
        """
        prompt = f"""你是广告主"{self.name}"的决策者。

广告主预算：{self.data.get('budget_value', 0)}元
创作者期望报酬：基于谈判内容

谈判历史：
{json.dumps(negotiation_history, ensure_ascii=False, indent=2)}

请判断是否达成合作，输出JSON格式（直接输出JSON，不要添加markdown代码块标记）：
{{
    "decision": "ACCEPT" 或 "REJECT",
    "final_price": 最终商定价格（数字）,
    "reasoning": "决策理由（50字以内）"
}}"""

        response = self.router.generate_content(
            task=f"advertiser_decision_{self.id}",
            prompt=prompt,
            model_key="PRO",
            thinking_level="MEDIUM"
        )

        if response:
            try:
                clean_response = response.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])
                return json.loads(clean_response)
            except json.JSONDecodeError:
                return {"decision": "REJECT", "final_price": 0, "reasoning": "无法解析决策"}

        return {"decision": "REJECT", "final_price": 0, "reasoning": "未能完成决策"}
