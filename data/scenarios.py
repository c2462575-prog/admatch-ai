# -*- coding: utf-8 -*-
"""
Hard-coded test scenarios for AdMatch AI MVP
Contains 3 advertisers, 3 creators, and 3 audiences (Chinese content)
"""

ADVERTISERS = {
    "brewlab": {
        "id": "brewlab",
        "name": "BrewLab Coffee",
        "name_cn": "酿造实验室咖啡",
        "industry": "food_beverage",
        "description": """
        BrewLab Coffee 是一家精品咖啡品牌，专注于单一产地咖啡豆和手冲咖啡体验。
        我们的目标客户是25-40岁的都市白领，追求生活品质和独特体验。
        品牌核心价值：匠心工艺、可持续采购、社区连接。
        本次推广预算：中等（5-10万元）
        推广目标：提升品牌知名度，吸引新客户到店体验。
        理想合作伙伴：生活方式类、美食类、文化类创作者。
        """,
        "budget_range": "medium",
        "budget_value": 75000,
        "target_audience": "urban_professionals",
        "values": ["craftsmanship", "sustainability", "community"],
        "campaign_goal": "brand_awareness"
    },
    "clouddesk": {
        "id": "clouddesk",
        "name": "CloudDesk SaaS",
        "name_cn": "云端办公",
        "industry": "technology",
        "description": """
        CloudDesk 是一款面向中小企业的云端协作办公平台。
        核心功能：项目管理、团队协作、文档共享、视频会议。
        目标用户：初创公司、远程团队、科技从业者。
        本次推广预算：高（15-25万元）
        推广目标：获取新用户注册，提高付费转化率。
        理想合作伙伴：科技类、效率工具类、创业类创作者。
        品牌调性：专业、高效、创新。
        """,
        "budget_range": "high",
        "budget_value": 200000,
        "target_audience": "tech_professionals",
        "values": ["innovation", "efficiency", "collaboration"],
        "campaign_goal": "user_acquisition"
    },
    "naturestep": {
        "id": "naturestep",
        "name": "NatureStep Skincare",
        "name_cn": "自然之步护肤",
        "industry": "beauty",
        "description": """
        NatureStep 是一个主打天然有机成分的护肤品牌。
        产品特点：纯植物配方、零残忍测试、环保包装。
        目标客户：注重健康生活方式的女性，18-35岁。
        本次推广预算：中高（8-15万元）
        推广目标：强调产品的环保理念，建立品牌忠诚度。
        理想合作伙伴：环保类、美妆类、健康生活类创作者。
        核心诉求：自然之美、环境责任、纯净配方。
        """,
        "budget_range": "medium_high",
        "budget_value": 120000,
        "target_audience": "eco_conscious_women",
        "values": ["sustainability", "natural", "cruelty_free"],
        "campaign_goal": "brand_loyalty"
    }
}

CREATORS = {
    "ken": {
        "id": "ken",
        "name": "Ken",
        "name_cn": "肯叔生活志",
        "niche": "lifestyle",
        "description": """
        我是Ken，一名生活方式博主，分享都市生活的美好瞬间。
        内容方向：咖啡文化、城市探店、生活美学、旅行见闻。
        粉丝画像：25-40岁都市白领，追求品质生活。
        粉丝数量：50万
        合作偏好：与品牌调性契合，内容自然融入。
        过往合作：咖啡品牌、生活用品、旅行平台。
        期望报酬：3-8万元/条
        底线：不接受虚假宣传，需保持内容真实性。
        """,
        "follower_count": 500000,
        "engagement_rate": 0.045,
        "content_style": ["lifestyle", "coffee", "urban_exploration"],
        "min_fee": 30000,
        "max_fee": 80000,
        "values": ["authenticity", "quality", "aesthetics"]
    },
    "mia": {
        "id": "mia",
        "name": "Mia",
        "name_cn": "绿色生活家Mia",
        "niche": "sustainability",
        "description": """
        我是Mia，专注于可持续生活方式的内容创作者。
        内容方向：环保生活、零废弃挑战、有机护肤、素食食谱。
        粉丝画像：关注环保议题的年轻人，18-35岁。
        粉丝数量：30万
        合作偏好：只与真正践行环保理念的品牌合作。
        过往合作：有机食品、环保品牌、可持续时尚。
        期望报酬：2-5万元/条
        底线：品牌必须有实际的环保行动，拒绝"漂绿"行为。
        """,
        "follower_count": 300000,
        "engagement_rate": 0.065,
        "content_style": ["sustainability", "organic", "zero_waste"],
        "min_fee": 20000,
        "max_fee": 50000,
        "values": ["sustainability", "authenticity", "environmental_action"]
    },
    "devtalk": {
        "id": "devtalk",
        "name": "DevTalk",
        "name_cn": "开发者茶话会",
        "niche": "technology",
        "description": """
        DevTalk 是一个面向开发者和科技爱好者的频道。
        内容方向：编程教程、开发工具评测、科技新闻、职业发展。
        粉丝画像：程序员、产品经理、科技从业者，22-40岁。
        粉丝数量：80万
        合作偏好：产品需要真正有价值，愿意提供深度体验。
        过往合作：云服务、开发工具、在线教育平台。
        期望报酬：5-12万元/条
        底线：需要亲自体验产品，不接受纯脚本念稿。
        """,
        "follower_count": 800000,
        "engagement_rate": 0.038,
        "content_style": ["tech_review", "tutorials", "developer_tools"],
        "min_fee": 50000,
        "max_fee": 120000,
        "values": ["technical_accuracy", "hands_on_experience", "value_driven"]
    }
}

AUDIENCES = {
    "ken_audience": {
        "id": "ken_audience",
        "creator_id": "ken",
        "name": "Ken的粉丝群体",
        "description": """
        我们是Ken的忠实粉丝，喜欢他分享的生活方式内容。
        我们期望看到真实的产品体验，而不是硬广。
        对于品牌合作，我们持开放态度，但希望内容依然保持Ken的风格。
        如果广告太明显或产品与Ken的调性不符，我们会表达不满。
        """,
        "acceptance_threshold": 0.35,
        "sensitivity_factors": ["authenticity", "content_fit", "subtlety"],
        "rejection_triggers": ["obvious_ads", "mismatched_products", "excessive_promotion"]
    },
    "mia_audience": {
        "id": "mia_audience",
        "creator_id": "mia",
        "name": "Mia的粉丝群体",
        "description": """
        我们关注Mia是因为她对环保的真诚态度。
        对于品牌合作，我们有严格的要求：品牌必须有真实的环保实践。
        我们会仔细审视合作品牌的背景，如果发现"漂绿"行为会强烈反对。
        只有真正符合可持续理念的合作才能获得我们的认可。
        """,
        "acceptance_threshold": 0.45,
        "sensitivity_factors": ["environmental_authenticity", "brand_ethics", "greenwashing_detection"],
        "rejection_triggers": ["greenwashing", "unethical_brands", "fake_sustainability_claims"]
    },
    "devtalk_audience": {
        "id": "devtalk_audience",
        "creator_id": "devtalk",
        "name": "DevTalk的粉丝群体",
        "description": """
        我们是技术从业者，关注DevTalk获取专业的技术内容。
        对于工具类产品的推广，我们持较为宽容的态度。
        只要产品确实有用，推广方式专业，我们可以接受。
        但如果产品质量差或推广过于夸张，我们会在评论区指出。
        """,
        "acceptance_threshold": 0.30,
        "sensitivity_factors": ["product_quality", "technical_accuracy", "professional_presentation"],
        "rejection_triggers": ["low_quality_products", "exaggerated_claims", "unprofessional_content"]
    }
}


def get_advertiser(advertiser_id: str) -> dict:
    """Get advertiser by ID"""
    return ADVERTISERS.get(advertiser_id)


def get_creator(creator_id: str) -> dict:
    """Get creator by ID"""
    return CREATORS.get(creator_id)


def get_audience(audience_id: str) -> dict:
    """Get audience by ID"""
    return AUDIENCES.get(audience_id)


def get_audience_for_creator(creator_id: str) -> dict:
    """Get audience for a specific creator"""
    audience_id = f"{creator_id}_audience"
    return AUDIENCES.get(audience_id)
