# -*- coding: utf-8 -*-
"""
Audience Agent - Scores negotiations and provides intervention warnings
"""

import json
from typing import Optional
from model_router import ModelRouter


class AudienceAgent:
    """Agent representing a creator's audience in the negotiation process"""

    def __init__(self, audience_data: dict, creator_data: dict, router: ModelRouter):
        self.data = audience_data
        self.creator_data = creator_data
        self.router = router
        self.id = audience_data.get("id", "unknown")
        self.creator_id = creator_data.get("id", "unknown")
        self.threshold = audience_data.get("acceptance_threshold", 0.35)
        self.scores_history = []

    def score_negotiation_round(
        self,
        advertiser_data: dict,
        round_num: int,
        advertiser_message: str,
        creator_message: str
    ) -> dict:
        """
        Score a negotiation round using FLASH_LITE/LOW

        Args:
            advertiser_data: Advertiser's profile data
            round_num: Current negotiation round
            advertiser_message: Advertiser's message this round
            creator_message: Creator's response this round

        Returns:
            Dict with score and feedback
        """
        prompt = f"""你代表创作者"{self.creator_data.get('name')}"的粉丝群体。

粉丝群体特点：
{json.dumps(self.data, ensure_ascii=False, indent=2)}

广告主信息：
- 名称：{advertiser_data.get('name')}
- 行业：{advertiser_data.get('industry')}
- 核心价值：{advertiser_data.get('values')}

第{round_num}轮谈判内容：
广告主：{advertiser_message}
创作者：{creator_message}

请从粉丝角度评估这次合作，输出JSON格式（直接输出JSON，不要添加markdown代码块标记）：
{{
    "acceptance_score": 0.0到1.0之间的分数,
    "concerns": ["担忧点1", "担忧点2"],
    "positive_aspects": ["积极方面1", "积极方面2"],
    "brief_feedback": "简短评价（30字以内）"
}}

评分标准：
- 0.0-0.3：强烈反对，可能取关
- 0.3-0.5：有所保留，需要观察
- 0.5-0.7：基本接受，希望内容真实
- 0.7-1.0：积极支持，期待合作"""

        response = self.router.generate_content(
            task=f"audience_scoring_{self.id}_round{round_num}",
            prompt=prompt,
            model_key="FLASH_LITE",
            thinking_level="LOW"
        )

        if response:
            try:
                clean_response = response.strip()
                if clean_response.startswith("```"):
                    lines = clean_response.split("\n")
                    clean_response = "\n".join(lines[1:-1])

                result = json.loads(clean_response)
                result["round"] = round_num
                self.scores_history.append(result)
                return result
            except json.JSONDecodeError as e:
                print(f"[Audience Agent] Failed to parse score JSON: {e}")
                default_result = {
                    "acceptance_score": 0.5,
                    "concerns": [],
                    "positive_aspects": [],
                    "brief_feedback": "无法评估",
                    "round": round_num
                }
                self.scores_history.append(default_result)
                return default_result

        default_result = {
            "acceptance_score": 0.5,
            "concerns": [],
            "positive_aspects": [],
            "brief_feedback": "评估失败",
            "round": round_num
        }
        self.scores_history.append(default_result)
        return default_result

    def generate_intervention(self, current_score: float, negotiation_context: str) -> Optional[str]:
        """
        Generate intervention warning if score is below threshold using FLASH_LITE/LOW

        Args:
            current_score: Current acceptance score
            negotiation_context: Summary of negotiation so far

        Returns:
            Intervention message if needed, None otherwise
        """
        if current_score >= self.threshold:
            return None

        prompt = f"""你代表创作者"{self.creator_data.get('name')}"的粉丝群体。

当前粉丝接受度评分：{current_score:.2f}
接受阈值：{self.threshold}
评分已低于阈值，粉丝群体需要发出警告。

谈判背景：
{negotiation_context}

请以粉丝群体的口吻，生成一条简短的警告信息（50字以内），表达对这次合作的担忧。
直接输出警告内容，不要添加任何前缀。"""

        response = self.router.generate_content(
            task=f"audience_intervention_{self.id}",
            prompt=prompt,
            model_key="FLASH_LITE",
            thinking_level="LOW"
        )

        return response

    def get_final_verdict(self) -> dict:
        """
        Get final audience verdict based on all rounds

        Returns:
            Dict with final verdict and summary
        """
        if not self.scores_history:
            return {
                "verdict": "UNKNOWN",
                "average_score": 0.0,
                "passed_threshold": False,
                "summary": "无评分记录"
            }

        scores = [s.get("acceptance_score", 0.5) for s in self.scores_history]
        avg_score = sum(scores) / len(scores)
        final_score = scores[-1] if scores else 0.5

        passed = final_score >= self.threshold

        if passed:
            verdict = "APPROVED"
            summary = f"粉丝群体接受此次合作（评分：{final_score:.2f}，阈值：{self.threshold}）"
        else:
            verdict = "REJECTED"
            summary = f"粉丝群体反对此次合作（评分：{final_score:.2f}，阈值：{self.threshold}）"

        return {
            "verdict": verdict,
            "final_score": final_score,
            "average_score": avg_score,
            "passed_threshold": passed,
            "threshold": self.threshold,
            "summary": summary,
            "all_scores": scores
        }

    def check_threshold(self, score: float) -> bool:
        """Check if score passes the acceptance threshold"""
        return score >= self.threshold

    def get_score_trend(self) -> str:
        """Get trend of scores across rounds"""
        if len(self.scores_history) < 2:
            return "STABLE"

        scores = [s.get("acceptance_score", 0.5) for s in self.scores_history]
        diff = scores[-1] - scores[0]

        if diff > 0.1:
            return "IMPROVING"
        elif diff < -0.1:
            return "DECLINING"
        else:
            return "STABLE"
