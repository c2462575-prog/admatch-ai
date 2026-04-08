# -*- coding: utf-8 -*-
"""
Report Generator - Generate comprehensive markdown report
"""

from datetime import datetime
from typing import Optional

from model_router import ModelRouter
from engine.matching import MatchScore
from negotiation.negotiation import NegotiationResult, NegotiationOutcome


class ReportGenerator:
    """Generates comprehensive markdown report of the matching and negotiation process"""

    def __init__(self, router: ModelRouter):
        self.router = router

    def generate_report(
        self,
        advertisers: dict,
        creators: dict,
        embeddings: dict,
        raw_matrix: dict,
        weighted_matrix: dict,
        match_details: dict,
        negotiation_results: list,
        api_stats: dict
    ) -> str:
        """
        Generate comprehensive markdown report

        Args:
            advertisers: Dict of advertiser data
            creators: Dict of creator data
            embeddings: Dict of embedding results
            raw_matrix: Raw similarity matrix
            weighted_matrix: Weighted match matrix
            match_details: Detailed match scores
            negotiation_results: List of NegotiationResult objects
            api_stats: API usage statistics

        Returns:
            Markdown report content
        """
        report_sections = []

        # Header
        report_sections.append(self._generate_header())

        # Executive Summary
        report_sections.append(self._generate_executive_summary(
            advertisers, creators, negotiation_results, api_stats
        ))

        # Advertiser Profiles
        report_sections.append(self._generate_advertiser_profiles(advertisers, embeddings))

        # Creator Profiles
        report_sections.append(self._generate_creator_profiles(creators, embeddings))

        # Matching Matrices
        report_sections.append(self._generate_matrices_section(
            raw_matrix, weighted_matrix, match_details, advertisers, creators
        ))

        # Negotiation Results
        report_sections.append(self._generate_negotiation_section(negotiation_results))

        # API Statistics
        report_sections.append(self._generate_api_stats_section(api_stats))

        # Footer
        report_sections.append(self._generate_footer())

        return "\n\n".join(report_sections)

    def _generate_header(self) -> str:
        """Generate report header"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""# AdMatch AI - 匹配与谈判报告

**生成时间**: {timestamp}

---"""

    def _generate_executive_summary(
        self,
        advertisers: dict,
        creators: dict,
        negotiation_results: list,
        api_stats: dict
    ) -> str:
        """Generate executive summary section"""
        total_negotiations = len(negotiation_results)
        successful = sum(1 for r in negotiation_results if r.outcome == NegotiationOutcome.SUCCESS)
        failed = sum(1 for r in negotiation_results if r.outcome == NegotiationOutcome.FAILED)
        audience_rejected = sum(1 for r in negotiation_results if r.outcome == NegotiationOutcome.AUDIENCE_REJECTED)

        success_rate = (successful / total_negotiations * 100) if total_negotiations > 0 else 0

        return f"""## 执行摘要

### 参与方概览
- **广告主数量**: {len(advertisers)}
- **创作者数量**: {len(creators)}
- **进行谈判数**: {total_negotiations}

### 谈判结果统计
| 结果类型 | 数量 | 占比 |
|---------|------|------|
| 成功达成 | {successful} | {successful/total_negotiations*100 if total_negotiations else 0:.1f}% |
| 谈判失败 | {failed} | {failed/total_negotiations*100 if total_negotiations else 0:.1f}% |
| 粉丝否决 | {audience_rejected} | {audience_rejected/total_negotiations*100 if total_negotiations else 0:.1f}% |

**综合成功率**: {success_rate:.1f}%

### API调用统计
- **总调用次数**: {api_stats.get('total_calls', 0)}
- **成功调用**: {api_stats.get('successful_calls', 0)}
- **失败调用**: {api_stats.get('failed_calls', 0)}"""

    def _generate_advertiser_profiles(self, advertisers: dict, embeddings: dict) -> str:
        """Generate advertiser profiles section"""
        lines = ["## 广告主档案", ""]

        for adv_id, adv_data in advertisers.items():
            embedding_info = embeddings.get("advertisers", {}).get(adv_id, {})
            description = embedding_info.get("description", "")[:200]

            lines.append(f"### {adv_data.get('name')} ({adv_data.get('name_cn', '')})")
            lines.append("")
            lines.append(f"- **行业**: {adv_data.get('industry', 'N/A')}")
            lines.append(f"- **预算范围**: {adv_data.get('budget_range', 'N/A')}")
            lines.append(f"- **预算金额**: ¥{adv_data.get('budget_value', 0):,}")
            lines.append(f"- **目标受众**: {adv_data.get('target_audience', 'N/A')}")
            lines.append(f"- **核心价值**: {', '.join(adv_data.get('values', []))}")
            lines.append(f"- **推广目标**: {adv_data.get('campaign_goal', 'N/A')}")
            lines.append("")
            if description:
                lines.append(f"**嵌入描述**: {description}...")
            lines.append("")

        return "\n".join(lines)

    def _generate_creator_profiles(self, creators: dict, embeddings: dict) -> str:
        """Generate creator profiles section"""
        lines = ["## 创作者档案", ""]

        for creator_id, creator_data in creators.items():
            embedding_info = embeddings.get("creators", {}).get(creator_id, {})
            description = embedding_info.get("description", "")[:200]

            lines.append(f"### {creator_data.get('name')} ({creator_data.get('name_cn', '')})")
            lines.append("")
            lines.append(f"- **内容领域**: {creator_data.get('niche', 'N/A')}")
            lines.append(f"- **粉丝数量**: {creator_data.get('follower_count', 0):,}")
            lines.append(f"- **互动率**: {creator_data.get('engagement_rate', 0)*100:.1f}%")
            lines.append(f"- **内容风格**: {', '.join(creator_data.get('content_style', []))}")
            lines.append(f"- **报价范围**: ¥{creator_data.get('min_fee', 0):,} - ¥{creator_data.get('max_fee', 0):,}")
            lines.append(f"- **核心价值**: {', '.join(creator_data.get('values', []))}")
            lines.append("")
            if description:
                lines.append(f"**嵌入描述**: {description}...")
            lines.append("")

        return "\n".join(lines)

    def _generate_matrices_section(
        self,
        raw_matrix: dict,
        weighted_matrix: dict,
        match_details: dict,
        advertisers: dict,
        creators: dict
    ) -> str:
        """Generate matching matrices section"""
        lines = ["## 匹配矩阵", ""]

        # Raw matrix
        lines.append("### 原始嵌入相似度矩阵")
        lines.append("")
        lines.append(self._render_matrix_table(raw_matrix, advertisers, creators))
        lines.append("")

        # Weighted matrix
        lines.append("### 加权综合匹配矩阵")
        lines.append("")
        lines.append("**权重配置**: 嵌入相似度(40%) + 受众匹配(25%) + 预算匹配(20%) + 价值观匹配(15%)")
        lines.append("")
        lines.append(self._render_matrix_table(weighted_matrix, advertisers, creators))
        lines.append("")

        # Top matches
        lines.append("### 最佳匹配排名")
        lines.append("")

        sorted_matches = sorted(
            match_details.values(),
            key=lambda x: x.weighted_score,
            reverse=True
        )

        lines.append("| 排名 | 广告主 | 创作者 | 嵌入分 | 受众分 | 预算分 | 价值分 | 综合分 |")
        lines.append("|------|--------|--------|--------|--------|--------|--------|--------|")

        for i, match in enumerate(sorted_matches, 1):
            adv_name = advertisers.get(match.advertiser_id, {}).get("name", match.advertiser_id)
            creator_name = creators.get(match.creator_id, {}).get("name", match.creator_id)
            lines.append(f"| {i} | {adv_name} | {creator_name} | "
                        f"{match.embedding_score:.3f} | {match.audience_score:.3f} | "
                        f"{match.budget_score:.3f} | {match.values_score:.3f} | "
                        f"**{match.weighted_score:.3f}** |")

        return "\n".join(lines)

    def _render_matrix_table(self, matrix: dict, advertisers: dict, creators: dict) -> str:
        """Render matrix as markdown table"""
        if not matrix:
            return "*无数据*"

        adv_ids = list(matrix.keys())
        creator_ids = list(matrix[adv_ids[0]].keys())

        # Header
        header = "| 广告主 |"
        for c_id in creator_ids:
            creator_name = creators.get(c_id, {}).get("name", c_id)
            header += f" {creator_name} |"

        separator = "|" + "|".join(["---"] * (len(creator_ids) + 1)) + "|"

        lines = [header, separator]

        # Rows
        for adv_id in adv_ids:
            adv_name = advertisers.get(adv_id, {}).get("name", adv_id)
            row = f"| {adv_name} |"
            for creator_id in creator_ids:
                score = matrix[adv_id][creator_id]
                row += f" {score:.3f} |"
            lines.append(row)

        return "\n".join(lines)

    def _generate_negotiation_section(self, negotiation_results: list) -> str:
        """Generate negotiation results section"""
        lines = ["## 谈判详情", ""]

        for i, result in enumerate(negotiation_results, 1):
            outcome_emoji = "✅" if result.outcome == NegotiationOutcome.SUCCESS else \
                           "❌" if result.outcome == NegotiationOutcome.FAILED else "🚫"

            lines.append(f"### 谈判 {i}: {result.advertiser_id} × {result.creator_id}")
            lines.append("")
            lines.append(f"**结果**: {outcome_emoji} {result.outcome.value}")
            lines.append(f"**摘要**: {result.summary}")
            lines.append("")

            if result.final_price > 0:
                lines.append(f"**最终价格**: ¥{result.final_price:,}")
                lines.append("")

            # Rounds detail
            lines.append("#### 谈判轮次")
            lines.append("")

            for round_data in result.rounds:
                lines.append(f"**第 {round_data.round_num} 轮**")
                lines.append("")
                lines.append(f"- 广告主: {round_data.advertiser_message[:100]}...")
                lines.append(f"- 创作者: {round_data.creator_message[:100]}...")
                lines.append(f"- 粉丝评分: {round_data.audience_score:.2f} ({round_data.audience_feedback})")

                if round_data.intervention_warning:
                    lines.append(f"- ⚠️ 粉丝警告: {round_data.intervention_warning}")

                lines.append("")

            # Audience verdict
            if result.audience_verdict:
                lines.append("#### 粉丝最终裁决")
                lines.append("")
                lines.append(f"- **裁决**: {result.audience_verdict.get('verdict', 'N/A')}")
                lines.append(f"- **最终评分**: {result.audience_verdict.get('final_score', 0):.2f}")
                lines.append(f"- **阈值**: {result.audience_verdict.get('threshold', 0)}")
                lines.append(f"- **摘要**: {result.audience_verdict.get('summary', '')}")
                lines.append("")

            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def _generate_api_stats_section(self, api_stats: dict) -> str:
        """Generate API statistics section"""
        lines = ["## API使用统计", ""]

        lines.append("### 总体统计")
        lines.append("")
        lines.append(f"- **总调用次数**: {api_stats.get('total_calls', 0)}")
        lines.append(f"- **成功调用**: {api_stats.get('successful_calls', 0)}")
        lines.append(f"- **失败调用**: {api_stats.get('failed_calls', 0)}")
        lines.append("")

        # By model
        lines.append("### 按模型统计")
        lines.append("")
        lines.append("| 模型 | 成功 | 失败 |")
        lines.append("|------|------|------|")

        for model, counts in api_stats.get("calls_by_model", {}).items():
            lines.append(f"| {model} | {counts.get('success', 0)} | {counts.get('failed', 0)} |")

        lines.append("")

        # By task
        lines.append("### 按任务统计")
        lines.append("")
        lines.append("| 任务 | 成功 | 失败 |")
        lines.append("|------|------|------|")

        for task, counts in api_stats.get("calls_by_task", {}).items():
            lines.append(f"| {task[:30]}... | {counts.get('success', 0)} | {counts.get('failed', 0)} |")

        return "\n".join(lines)

    def _generate_footer(self) -> str:
        """Generate report footer"""
        return """---

*本报告由 AdMatch AI 系统自动生成*

**技术栈**: Google Gemini API | Python | AI Agent Architecture"""

    def save_report(self, content: str, filepath: str = "report.md"):
        """Save report to file"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\n[Report] Saved to {filepath}")

    def generate_ai_summary(self, report_content: str) -> Optional[str]:
        """
        Generate AI summary of the report using PRO/MEDIUM

        Args:
            report_content: Full report content

        Returns:
            AI-generated summary
        """
        prompt = f"""请阅读以下广告匹配与谈判报告，生成一段简洁的管理层摘要（200字以内），
重点说明：
1. 整体匹配效果
2. 谈判成功率及原因
3. 关键洞察和建议

报告内容：
{report_content[:5000]}...

请直接输出摘要内容。"""

        return self.router.generate_content(
            task="report_ai_summary",
            prompt=prompt,
            model_key="PRO",
            thinking_level="MEDIUM"
        )
