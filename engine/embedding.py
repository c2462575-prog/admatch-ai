# -*- coding: utf-8 -*-
"""
Embedding Engine - Generate descriptions and vector embeddings
"""

import json
from typing import Optional
from model_router import ModelRouter


class EmbeddingEngine:
    """Handles embedding description generation and vectorization"""

    def __init__(self, router: ModelRouter):
        self.router = router
        self.embeddings_cache = {}

    def generate_embedding_description(self, entity_type: str, entity_data: dict) -> Optional[str]:
        """
        Generate a concise description for embedding using FLASH/MEDIUM

        Args:
            entity_type: "advertiser" or "creator"
            entity_data: The entity's profile data

        Returns:
            Generated description text for embedding
        """
        if entity_type == "advertiser":
            prompt = f"""分析以下广告主信息，生成一段简洁的描述文本（100-150字），用于匹配算法。
描述应包含：行业特点、目标受众、核心价值观、合作偏好。

广告主信息：
{json.dumps(entity_data, ensure_ascii=False, indent=2)}

请直接输出描述文本，不要添加任何前缀或解释。"""
        else:
            prompt = f"""分析以下创作者信息，生成一段简洁的描述文本（100-150字），用于匹配算法。
描述应包含：内容风格、粉丝特征、合作偏好、核心价值观。

创作者信息：
{json.dumps(entity_data, ensure_ascii=False, indent=2)}

请直接输出描述文本，不要添加任何前缀或解释。"""

        description = self.router.generate_content(
            task=f"embedding_description_{entity_type}_{entity_data.get('id', 'unknown')}",
            prompt=prompt,
            model_key="FLASH",
            thinking_level="MEDIUM"
        )

        return description

    def generate_embedding_vector(self, entity_id: str, text: str) -> Optional[list]:
        """
        Generate embedding vector for text using EMBED model

        Args:
            entity_id: ID of the entity (for caching)
            text: Text to embed

        Returns:
            Embedding vector
        """
        # Check cache
        if entity_id in self.embeddings_cache:
            return self.embeddings_cache[entity_id]

        embedding = self.router.generate_embedding(
            task=f"embedding_vector_{entity_id}",
            text=text
        )

        if embedding:
            self.embeddings_cache[entity_id] = embedding

        return embedding

    def process_entity(self, entity_type: str, entity_data: dict) -> dict:
        """
        Full processing pipeline for an entity

        Args:
            entity_type: "advertiser" or "creator"
            entity_data: The entity's profile data

        Returns:
            Dict with description and embedding
        """
        entity_id = entity_data.get("id", "unknown")
        print(f"\n[Embedding] Processing {entity_type}: {entity_id}")

        # Generate description
        description = self.generate_embedding_description(entity_type, entity_data)
        if not description:
            print(f"  [WARNING] Failed to generate description for {entity_id}")
            description = entity_data.get("description", "")

        print(f"  Description generated ({len(description)} chars)")

        # Generate embedding
        embedding = self.generate_embedding_vector(entity_id, description)
        if not embedding:
            print(f"  [WARNING] Failed to generate embedding for {entity_id}")

        print(f"  Embedding generated ({len(embedding) if embedding else 0} dimensions)")

        return {
            "id": entity_id,
            "type": entity_type,
            "description": description,
            "embedding": embedding
        }

    def process_all_entities(self, advertisers: dict, creators: dict) -> dict:
        """
        Process all advertisers and creators

        Returns:
            Dict with processed embeddings for all entities
        """
        results = {
            "advertisers": {},
            "creators": {}
        }

        print("\n" + "=" * 50)
        print("EMBEDDING GENERATION")
        print("=" * 50)

        # Process advertisers
        print("\n--- Processing Advertisers ---")
        for adv_id, adv_data in advertisers.items():
            result = self.process_entity("advertiser", adv_data)
            results["advertisers"][adv_id] = result

        # Process creators
        print("\n--- Processing Creators ---")
        for creator_id, creator_data in creators.items():
            result = self.process_entity("creator", creator_data)
            results["creators"][creator_id] = result

        return results
