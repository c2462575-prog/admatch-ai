# -*- coding: utf-8 -*-
"""
Creator Agent - Analyzes creator profile and handles negotiation
"""

import json
from typing import Optional
from model_router import ModelRouter


class CreatorAgent:
    """Agent representing a creator in the matching and negotiation process"""

    def __init__(self, creator_data: dict, router: ModelRouter):
        self.data = creator_data
        self.router = router
        self.profile = None
        self.id = creator_data.get("id", "unknown")
        self.name = creator_data.get("name", "Unknown Creator")

    def analyze_profile(self) -> Optional[dict]:
        """
        Deep analysis of creator profile using PRO/HIGH

        Returns:
            Structured profile dict with analysis results
        """
        prompt = f"""你是一位专业的内容创作者经纪人。请深入分析以下创作者的信息，并输出结构化的JSON分析结果。

创作者信息：
{json.dumps(self.data, ensure_ascii=False, indent=2)}

请分析并输出以下JSON格式（直接输出JSON，不要添加markdown代码块标记）：
{{
    "content_summary": "创作者的内容风格和特点摘要（50-100字）",
    "ideal_brand_traits": ["理想合作品牌的特征1", "特征2", "特征3"],
    "negotiation_priorities": {{
        "must_have": ["必须满足的条件"],
        "nice_to_have": ["希望但可协商的条件"],
        "dealbreakers": ["无法接受的条件"]
    }},
    "pricing_strategy": {{
        "minimum_acceptable": {self.data.get('min_fee', 0)},
        "ideal_price": {int((self.data.get('min_fee', 0) + self.data.get('max_fee', 0)) / 2)},
        "premium_triggers": ["可以接受更高报价的条件"]
    }},
    "audience_considerations": "需要考虑的粉丝因素（50字以内）",
    "embedding_description": "用于匹配算法的简短描述（100字以内）"
}}"""

        response = self.router.generate_content(
            task=f"creator_analysis_{self.id}",
            prompt=prompt,
            model_key="PRO",
            thinking_level="HIGH"
        )

        if response:
            try:
                clean_response = response.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])

                self.profile = json.loads(clean_response)
                print(f"[Creator Agent] {self.name} profile analyzed successfully")
                return self.profile
            except json.JSONDecodeError as e:
                print(f"[Creator Agent] Failed to parse profile JSON: {e}")
                self.profile = {
                    "content_summary": response[:200],
                    "ideal_brand_traits": [],
                    "negotiation_priorities": {"must_have": [], "nice_to_have": [], "dealbreakers": []},
                    "pricing_strategy": {
                        "minimum_acceptable": self.data.get("min_fee", 0),
                        "ideal_price": (self.data.get("min_fee", 0) + self.data.get("max_fee", 0)) // 2
                    },
                    "audience_considerations": "",
                    "embedding_description": self.data.get("description", "")[:100]
                }
                return self.profile

        return None

    def generate_response(self, advertiser_data: dict, round_num: int, advertiser_offer: str) -> Optional[str]:
        """
        Generate negotiation response using PRO/MEDIUM

        Args:
            advertiser_data: Advertiser's profile data
            round_num: Current negotiation round (1-3)
            advertiser_offer: Advertiser's current offer

        Returns:
            Response text
        """
        context = f"""你是创作者"{self.name}"的谈判代表。

创作者信息：
{json.dumps(self.data, ensure_ascii=False, indent=2)}

广告主信息：
{json.dumps(advertiser_data, ensure_ascii=False, indent=2)}

当前是第{round_num}轮谈判。"""

        if round_num == 1:
            prompt = context + f"""

广告主的初始邀约：
{advertiser_offer}

请生成回应，包括：
1. 对合作邀约的初步态度
2. 对报价的反馈（是否符合期望）
3. 提出自己的条件或要求
4. 关于内容创作的想法

直接输出回应内容，使用中文，控制在200字以内。"""
        elif round_num == 2:
            prompt = context + f"""

广告主的当前提案：
{advertiser_offer}

请继续协商：
1. 评估广告主的调整是否满意
2. 就细节进行进一步讨论
3. 明确自己的底线
4. 展示合作诚意

直接输出回应内容，使用中文，控制在200字以内。"""
        else:  # round 3
            prompt = context + f"""

广告主的最终提案：
{advertiser_offer}

这是最终轮谈判，请：
1. 做出最终决定
2. 如接受，确认所有条款
3. 如拒绝，说明原因
4. 无论结果如何，保持专业

直接输出最终回应，使用中文，控制在200字以内。"""

        response = self.router.generate_content(
            task=f"creator_negotiation_{self.id}_round{round_num}",
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
        prompt = f"""你是创作者"{self.name}"的决策者。

创作者期望报酬：{self.data.get('min_fee', 0)}-{self.data.get('max_fee', 0)}元

谈判历史：
{json.dumps(negotiation_history, ensure_ascii=False, indent=2)}

请判断是否接受合作，输出JSON格式（直接输出JSON，不要添加markdown代码块标记）：
{{
    "decision": "ACCEPT" 或 "REJECT",
    "final_price": 最终商定价格（数字）,
    "reasoning": "决策理由（50字以内）"
}}"""

        response = self.router.generate_content(
            task=f"creator_decision_{self.id}",
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
