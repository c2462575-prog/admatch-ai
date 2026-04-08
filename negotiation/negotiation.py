# -*- coding: utf-8 -*-
"""
Negotiation Engine - 3-round negotiation flow with audience feedback
"""

from typing import Optional
from dataclasses import dataclass, field
from enum import Enum

from model_router import ModelRouter
from agents.advertiser_agent import AdvertiserAgent
from agents.creator_agent import CreatorAgent
from agents.audience_agent import AudienceAgent
from data.scenarios import get_audience_for_creator


class NegotiationOutcome(Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    AUDIENCE_REJECTED = "AUDIENCE_REJECTED"
    IN_PROGRESS = "IN_PROGRESS"


@dataclass
class NegotiationRound:
    """Data for a single negotiation round"""
    round_num: int
    advertiser_message: str
    creator_message: str
    audience_score: float
    audience_feedback: str
    intervention_warning: Optional[str] = None


@dataclass
class NegotiationResult:
    """Complete result of a negotiation"""
    advertiser_id: str
    creator_id: str
    outcome: NegotiationOutcome
    rounds: list = field(default_factory=list)
    final_price: int = 0
    advertiser_decision: dict = field(default_factory=dict)
    creator_decision: dict = field(default_factory=dict)
    audience_verdict: dict = field(default_factory=dict)
    summary: str = ""


class NegotiationEngine:
    """Handles the 3-round negotiation process with audience feedback"""

    def __init__(self, router: ModelRouter):
        self.router = router
        self.results = []

    def run_negotiation(
        self,
        advertiser_data: dict,
        creator_data: dict,
        match_score: float
    ) -> NegotiationResult:
        """
        Run a complete 3-round negotiation

        Args:
            advertiser_data: Advertiser's profile data
            creator_data: Creator's profile data
            match_score: Pre-calculated match score

        Returns:
            NegotiationResult with complete outcome
        """
        advertiser_id = advertiser_data.get("id", "unknown")
        creator_id = creator_data.get("id", "unknown")

        print("\n" + "=" * 60)
        print(f"NEGOTIATION: {advertiser_data.get('name')} <-> {creator_data.get('name')}")
        print(f"Match Score: {match_score:.3f}")
        print("=" * 60)

        # Initialize agents
        advertiser_agent = AdvertiserAgent(advertiser_data, self.router)
        creator_agent = CreatorAgent(creator_data, self.router)

        # Get audience data and initialize audience agent
        audience_data = get_audience_for_creator(creator_id)
        if not audience_data:
            audience_data = {
                "id": f"{creator_id}_audience",
                "creator_id": creator_id,
                "name": f"{creator_data.get('name')}的粉丝",
                "acceptance_threshold": 0.35,
                "description": "默认粉丝群体"
            }

        audience_agent = AudienceAgent(audience_data, creator_data, self.router)

        result = NegotiationResult(
            advertiser_id=advertiser_id,
            creator_id=creator_id,
            outcome=NegotiationOutcome.IN_PROGRESS
        )

        # Run 3 rounds of negotiation
        previous_creator_response = None
        audience_rejected = False

        for round_num in range(1, 4):
            print(f"\n--- Round {round_num} ---")

            # Advertiser makes offer
            advertiser_message = advertiser_agent.generate_offer(
                creator_data, round_num, previous_creator_response
            )

            if not advertiser_message:
                advertiser_message = f"[广告主{advertiser_data.get('name')}未能生成回应]"

            print(f"\n[Advertiser] {advertiser_data.get('name')}:")
            print(f"  {advertiser_message[:100]}..." if len(advertiser_message) > 100 else f"  {advertiser_message}")

            # Creator responds
            creator_message = creator_agent.generate_response(
                advertiser_data, round_num, advertiser_message
            )

            if not creator_message:
                creator_message = f"[创作者{creator_data.get('name')}未能生成回应]"

            print(f"\n[Creator] {creator_data.get('name')}:")
            print(f"  {creator_message[:100]}..." if len(creator_message) > 100 else f"  {creator_message}")

            previous_creator_response = creator_message

            # Audience scores the round
            audience_result = audience_agent.score_negotiation_round(
                advertiser_data, round_num, advertiser_message, creator_message
            )

            audience_score = audience_result.get("acceptance_score", 0.5)
            audience_feedback = audience_result.get("brief_feedback", "")

            print(f"\n[Audience] Score: {audience_score:.2f} (threshold: {audience_agent.threshold})")
            print(f"  Feedback: {audience_feedback}")

            # Check for intervention
            intervention_warning = None
            if not audience_agent.check_threshold(audience_score):
                negotiation_context = f"""
广告主：{advertiser_data.get('name')}
创作者：{creator_data.get('name')}
当前轮次：{round_num}
最新对话：
- 广告主：{advertiser_message[:100]}
- 创作者：{creator_message[:100]}
"""
                intervention_warning = audience_agent.generate_intervention(
                    audience_score, negotiation_context
                )

                if intervention_warning:
                    print(f"\n[WARNING] Audience Intervention:")
                    print(f"  {intervention_warning}")

                # If audience score is very low in final round, mark as rejected
                if round_num == 3 and audience_score < audience_agent.threshold:
                    audience_rejected = True

            # Record round
            round_data = NegotiationRound(
                round_num=round_num,
                advertiser_message=advertiser_message,
                creator_message=creator_message,
                audience_score=audience_score,
                audience_feedback=audience_feedback,
                intervention_warning=intervention_warning
            )
            result.rounds.append(round_data)

        # Get final decisions
        negotiation_history = [
            {
                "round": r.round_num,
                "advertiser": r.advertiser_message,
                "creator": r.creator_message,
                "audience_score": r.audience_score
            }
            for r in result.rounds
        ]

        # Get audience verdict
        audience_verdict = audience_agent.get_final_verdict()
        result.audience_verdict = audience_verdict

        print(f"\n[Audience Final Verdict] {audience_verdict.get('verdict')}")
        print(f"  {audience_verdict.get('summary')}")

        # If audience rejected, mark outcome
        if audience_verdict.get("verdict") == "REJECTED":
            result.outcome = NegotiationOutcome.AUDIENCE_REJECTED
            result.summary = f"粉丝群体反对此次合作（最终评分：{audience_verdict.get('final_score', 0):.2f}）"
            print(f"\n[OUTCOME] AUDIENCE_REJECTED - {result.summary}")
        else:
            # Get agent decisions
            advertiser_decision = advertiser_agent.decide_final_outcome(negotiation_history)
            creator_decision = creator_agent.decide_final_outcome(negotiation_history)

            result.advertiser_decision = advertiser_decision
            result.creator_decision = creator_decision

            print(f"\n[Advertiser Decision] {advertiser_decision.get('decision')}: {advertiser_decision.get('reasoning')}")
            print(f"[Creator Decision] {creator_decision.get('decision')}: {creator_decision.get('reasoning')}")

            # Determine final outcome
            if advertiser_decision.get("decision") == "ACCEPT" and creator_decision.get("decision") == "ACCEPT":
                result.outcome = NegotiationOutcome.SUCCESS
                result.final_price = creator_decision.get("final_price", 0) or advertiser_decision.get("final_price", 0)
                result.summary = f"合作达成！最终价格：{result.final_price}元"
            else:
                result.outcome = NegotiationOutcome.FAILED
                reason = advertiser_decision.get("reasoning") if advertiser_decision.get("decision") == "REJECT" else creator_decision.get("reasoning")
                result.summary = f"谈判失败：{reason}"

            print(f"\n[OUTCOME] {result.outcome.value} - {result.summary}")

        self.results.append(result)
        return result

    def run_all_negotiations(
        self,
        top_matches: list,
        advertisers: dict,
        creators: dict
    ) -> list:
        """
        Run negotiations for all top matches

        Args:
            top_matches: List of MatchScore objects
            advertisers: Dict of advertiser data
            creators: Dict of creator data

        Returns:
            List of NegotiationResult objects
        """
        print("\n" + "=" * 60)
        print("NEGOTIATION PHASE")
        print("=" * 60)

        for match in top_matches:
            advertiser_data = advertisers.get(match.advertiser_id)
            creator_data = creators.get(match.creator_id)

            if advertiser_data and creator_data:
                self.run_negotiation(
                    advertiser_data,
                    creator_data,
                    match.weighted_score
                )

        return self.results

    def get_summary(self) -> dict:
        """Get summary of all negotiations"""
        total = len(self.results)
        success = sum(1 for r in self.results if r.outcome == NegotiationOutcome.SUCCESS)
        failed = sum(1 for r in self.results if r.outcome == NegotiationOutcome.FAILED)
        audience_rejected = sum(1 for r in self.results if r.outcome == NegotiationOutcome.AUDIENCE_REJECTED)

        return {
            "total_negotiations": total,
            "successful": success,
            "failed": failed,
            "audience_rejected": audience_rejected,
            "success_rate": success / total if total > 0 else 0,
            "results": [
                {
                    "advertiser_id": r.advertiser_id,
                    "creator_id": r.creator_id,
                    "outcome": r.outcome.value,
                    "final_price": r.final_price,
                    "summary": r.summary
                }
                for r in self.results
            ]
        }
