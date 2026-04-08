# -*- coding: utf-8 -*-
"""
Matching Engine - Cosine similarity, weighted scoring, and ASCII heatmap
"""

import math
from typing import Optional
from dataclasses import dataclass


@dataclass
class MatchScore:
    """Score components for a match"""
    advertiser_id: str
    creator_id: str
    embedding_score: float
    audience_score: float
    budget_score: float
    values_score: float
    weighted_score: float


class MatchingEngine:
    """Handles matching calculations and matrix generation"""

    # Weights for final score calculation
    WEIGHTS = {
        "embedding": 0.40,
        "audience": 0.25,
        "budget": 0.20,
        "values": 0.15
    }

    def __init__(self):
        self.raw_matrix = {}
        self.weighted_matrix = {}
        self.match_details = {}

    @staticmethod
    def cosine_similarity(vec1: list, vec2: list) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2:
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def calculate_audience_fit(self, advertiser: dict, creator: dict) -> float:
        """Calculate audience fit score based on target audience alignment"""
        adv_target = advertiser.get("target_audience", "")
        creator_styles = creator.get("content_style", [])

        # Simple mapping of advertiser targets to creator niches
        audience_mapping = {
            "urban_professionals": ["lifestyle", "coffee", "urban_exploration"],
            "tech_professionals": ["tech_review", "tutorials", "developer_tools"],
            "eco_conscious_women": ["sustainability", "organic", "zero_waste"]
        }

        expected_styles = audience_mapping.get(adv_target, [])
        if not expected_styles:
            return 0.5  # Default middle score

        # Count matches
        matches = len(set(creator_styles) & set(expected_styles))
        max_matches = max(len(expected_styles), len(creator_styles))

        if max_matches == 0:
            return 0.5

        return matches / max_matches

    def calculate_budget_fit(self, advertiser: dict, creator: dict) -> float:
        """Calculate budget fit score"""
        adv_budget = advertiser.get("budget_value", 0)
        creator_min = creator.get("min_fee", 0)
        creator_max = creator.get("max_fee", 0)

        if adv_budget <= 0 or creator_max <= 0:
            return 0.5

        # Check if budget is within creator's range
        if creator_min <= adv_budget <= creator_max:
            return 1.0
        elif adv_budget > creator_max:
            # Budget exceeds max - good for creator
            return 0.9
        else:
            # Budget below minimum
            ratio = adv_budget / creator_min
            return max(0.1, ratio)

    def calculate_values_alignment(self, advertiser: dict, creator: dict) -> float:
        """Calculate values alignment score"""
        adv_values = set(advertiser.get("values", []))
        creator_values = set(creator.get("values", []))

        if not adv_values or not creator_values:
            return 0.5

        # Count overlapping values
        overlap = len(adv_values & creator_values)
        total = len(adv_values | creator_values)

        if total == 0:
            return 0.5

        return overlap / total

    def calculate_match(
        self,
        advertiser: dict,
        creator: dict,
        adv_embedding: Optional[list],
        creator_embedding: Optional[list]
    ) -> MatchScore:
        """Calculate comprehensive match score between advertiser and creator"""
        adv_id = advertiser.get("id", "unknown")
        creator_id = creator.get("id", "unknown")

        # Calculate component scores
        embedding_score = self.cosine_similarity(adv_embedding, creator_embedding) if adv_embedding and creator_embedding else 0.5
        audience_score = self.calculate_audience_fit(advertiser, creator)
        budget_score = self.calculate_budget_fit(advertiser, creator)
        values_score = self.calculate_values_alignment(advertiser, creator)

        # Calculate weighted score
        weighted_score = (
            embedding_score * self.WEIGHTS["embedding"] +
            audience_score * self.WEIGHTS["audience"] +
            budget_score * self.WEIGHTS["budget"] +
            values_score * self.WEIGHTS["values"]
        )

        return MatchScore(
            advertiser_id=adv_id,
            creator_id=creator_id,
            embedding_score=embedding_score,
            audience_score=audience_score,
            budget_score=budget_score,
            values_score=values_score,
            weighted_score=weighted_score
        )

    def build_matrices(
        self,
        advertisers: dict,
        creators: dict,
        embeddings: dict
    ) -> tuple:
        """
        Build raw and weighted matching matrices

        Returns:
            Tuple of (raw_matrix, weighted_matrix, match_details)
        """
        adv_ids = list(advertisers.keys())
        creator_ids = list(creators.keys())

        self.raw_matrix = {adv_id: {} for adv_id in adv_ids}
        self.weighted_matrix = {adv_id: {} for adv_id in adv_ids}
        self.match_details = {}

        for adv_id in adv_ids:
            for creator_id in creator_ids:
                adv_data = advertisers[adv_id]
                creator_data = creators[creator_id]

                adv_embedding = embeddings["advertisers"].get(adv_id, {}).get("embedding")
                creator_embedding = embeddings["creators"].get(creator_id, {}).get("embedding")

                match = self.calculate_match(
                    adv_data, creator_data, adv_embedding, creator_embedding
                )

                self.raw_matrix[adv_id][creator_id] = match.embedding_score
                self.weighted_matrix[adv_id][creator_id] = match.weighted_score
                self.match_details[f"{adv_id}_{creator_id}"] = match

        return self.raw_matrix, self.weighted_matrix, self.match_details

    def render_ascii_heatmap(self, matrix: dict, title: str) -> str:
        """Render matrix as ASCII heatmap"""
        if not matrix:
            return "No data"

        adv_ids = list(matrix.keys())
        creator_ids = list(matrix[adv_ids[0]].keys())

        # Heatmap characters from low to high
        chars = " ░▒▓█"

        def score_to_char(score: float) -> str:
            idx = int(score * (len(chars) - 1))
            idx = max(0, min(idx, len(chars) - 1))
            return chars[idx]

        lines = []
        lines.append("")
        lines.append("=" * 60)
        lines.append(title)
        lines.append("=" * 60)

        # Header
        header = "          "
        for c_id in creator_ids:
            header += f" {c_id[:8]:^8}"
        lines.append(header)
        lines.append("-" * len(header))

        # Rows
        for adv_id in adv_ids:
            row = f"{adv_id[:9]:>9} |"
            for creator_id in creator_ids:
                score = matrix[adv_id][creator_id]
                char = score_to_char(score)
                row += f" {char*3} {score:.2f}"
            lines.append(row)

        # Legend
        lines.append("")
        lines.append("Legend: " + "".join([f"{chars[i]}={i*0.25:.2f}-{(i+1)*0.25:.2f} " for i in range(len(chars))]))
        lines.append("")

        return "\n".join(lines)

    def get_top_matches(self, n: int = 3) -> list:
        """Get top N matches sorted by weighted score"""
        if not self.match_details:
            return []

        # Sort by weighted score
        sorted_matches = sorted(
            self.match_details.values(),
            key=lambda x: x.weighted_score,
            reverse=True
        )

        return sorted_matches[:n]

    def get_match_summary(self) -> str:
        """Get summary of all matches"""
        lines = []
        lines.append("\n" + "=" * 60)
        lines.append("MATCH SUMMARY")
        lines.append("=" * 60)

        for key, match in self.match_details.items():
            lines.append(f"\n{match.advertiser_id} <-> {match.creator_id}:")
            lines.append(f"  Embedding Score:  {match.embedding_score:.3f} (weight: {self.WEIGHTS['embedding']})")
            lines.append(f"  Audience Score:   {match.audience_score:.3f} (weight: {self.WEIGHTS['audience']})")
            lines.append(f"  Budget Score:     {match.budget_score:.3f} (weight: {self.WEIGHTS['budget']})")
            lines.append(f"  Values Score:     {match.values_score:.3f} (weight: {self.WEIGHTS['values']})")
            lines.append(f"  WEIGHTED TOTAL:   {match.weighted_score:.3f}")

        return "\n".join(lines)

    def display_matrices(self):
        """Display both matrices with ASCII heatmaps"""
        print(self.render_ascii_heatmap(self.raw_matrix, "RAW EMBEDDING SIMILARITY MATRIX"))
        print(self.render_ascii_heatmap(self.weighted_matrix, "WEIGHTED COMPREHENSIVE MATRIX"))

        # Top matches
        top_matches = self.get_top_matches(3)
        print("\n" + "=" * 60)
        print("TOP 3 MATCHES FOR NEGOTIATION")
        print("=" * 60)
        for i, match in enumerate(top_matches, 1):
            print(f"{i}. {match.advertiser_id} + {match.creator_id}: {match.weighted_score:.3f}")
