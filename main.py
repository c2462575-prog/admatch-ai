# -*- coding: utf-8 -*-
"""
AdMatch AI MVP - Main Orchestrator
Runs all 4 flows: Agent Analysis, Embedding & Matching, Negotiation, Report Generation
"""

import sys
from datetime import datetime

from model_router import ModelRouter
from data.scenarios import ADVERTISERS, CREATORS, AUDIENCES
from engine.embedding import EmbeddingEngine
from engine.matching import MatchingEngine
from agents.advertiser_agent import AdvertiserAgent
from agents.creator_agent import CreatorAgent
from negotiation.negotiation import NegotiationEngine
from report.generator import ReportGenerator


def print_banner():
    """Print startup banner"""
    print("=" * 60)
    print("   AdMatch AI - 广告匹配平台 MVP")
    print("   Three-Party AI Agent Matching System")
    print("=" * 60)
    print(f"   Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


def flow1_agent_analysis(router: ModelRouter) -> dict:
    """
    Flow 1: Agent Deep Analysis
    Each agent analyzes their role using PRO/HIGH
    """
    print("\n" + "=" * 60)
    print("FLOW 1: AGENT DEEP ANALYSIS")
    print("Using: gemini-3.1-pro-preview / thinking_level=HIGH")
    print("=" * 60)

    profiles = {
        "advertisers": {},
        "creators": {}
    }

    # Analyze advertisers
    print("\n--- Analyzing Advertisers ---")
    for adv_id, adv_data in ADVERTISERS.items():
        print(f"\nAnalyzing: {adv_data['name']}")
        agent = AdvertiserAgent(adv_data, router)
        profile = agent.analyze_profile()
        if profile:
            profiles["advertisers"][adv_id] = profile
            print(f"  Campaign Summary: {profile.get('campaign_summary', '')[:60]}...")
        else:
            print(f"  [WARNING] Failed to analyze {adv_id}")

    # Analyze creators
    print("\n--- Analyzing Creators ---")
    for creator_id, creator_data in CREATORS.items():
        print(f"\nAnalyzing: {creator_data['name']}")
        agent = CreatorAgent(creator_data, router)
        profile = agent.analyze_profile()
        if profile:
            profiles["creators"][creator_id] = profile
            print(f"  Content Summary: {profile.get('content_summary', '')[:60]}...")
        else:
            print(f"  [WARNING] Failed to analyze {creator_id}")

    print("\n[Flow 1 Complete] Agent profiles generated")
    return profiles


def flow2_embedding_matching(router: ModelRouter) -> tuple:
    """
    Flow 2: Embedding & Matching Matrix
    Generate embeddings and compute matching matrices
    """
    print("\n" + "=" * 60)
    print("FLOW 2: EMBEDDING & MATCHING")
    print("Using: gemini-3-flash-preview/MEDIUM (descriptions)")
    print("       gemini-embedding-2-preview (vectors)")
    print("=" * 60)

    # Initialize engines
    embedding_engine = EmbeddingEngine(router)
    matching_engine = MatchingEngine()

    # Process all entities
    embeddings = embedding_engine.process_all_entities(ADVERTISERS, CREATORS)

    # Build matching matrices
    print("\n--- Building Matching Matrices ---")
    raw_matrix, weighted_matrix, match_details = matching_engine.build_matrices(
        ADVERTISERS, CREATORS, embeddings
    )

    # Display matrices
    matching_engine.display_matrices()

    # Print detailed match summary
    print(matching_engine.get_match_summary())

    # Get top matches for negotiation
    top_matches = matching_engine.get_top_matches(3)

    print("\n[Flow 2 Complete] Matching matrices generated")
    return embeddings, raw_matrix, weighted_matrix, match_details, top_matches


def flow3_negotiation(router: ModelRouter, top_matches: list) -> list:
    """
    Flow 3: Negotiation Simulation
    Run 3-round negotiations with audience feedback
    """
    print("\n" + "=" * 60)
    print("FLOW 3: NEGOTIATION SIMULATION")
    print("Using: gemini-3.1-pro-preview/MEDIUM (dialogue)")
    print("       gemini-3.1-flash-lite-preview/LOW (audience)")
    print("=" * 60)

    negotiation_engine = NegotiationEngine(router)

    results = negotiation_engine.run_all_negotiations(
        top_matches, ADVERTISERS, CREATORS
    )

    # Print summary
    summary = negotiation_engine.get_summary()
    print("\n" + "=" * 60)
    print("NEGOTIATION SUMMARY")
    print("=" * 60)
    print(f"Total Negotiations: {summary['total_negotiations']}")
    print(f"Successful: {summary['successful']}")
    print(f"Failed: {summary['failed']}")
    print(f"Audience Rejected: {summary['audience_rejected']}")
    print(f"Success Rate: {summary['success_rate']*100:.1f}%")

    print("\n[Flow 3 Complete] Negotiations finished")
    return results


def flow4_report_generation(
    router: ModelRouter,
    embeddings: dict,
    raw_matrix: dict,
    weighted_matrix: dict,
    match_details: dict,
    negotiation_results: list
) -> str:
    """
    Flow 4: Final Report Generation
    Generate comprehensive markdown report
    """
    print("\n" + "=" * 60)
    print("FLOW 4: REPORT GENERATION")
    print("Using: gemini-3.1-pro-preview/MEDIUM")
    print("=" * 60)

    report_generator = ReportGenerator(router)

    # Get API stats
    api_stats = router.get_stats_dict()

    # Generate report
    print("\nGenerating comprehensive report...")
    report_content = report_generator.generate_report(
        advertisers=ADVERTISERS,
        creators=CREATORS,
        embeddings=embeddings,
        raw_matrix=raw_matrix,
        weighted_matrix=weighted_matrix,
        match_details=match_details,
        negotiation_results=negotiation_results,
        api_stats=api_stats
    )

    # Generate AI summary
    print("\nGenerating AI summary...")
    ai_summary = report_generator.generate_ai_summary(report_content)
    if ai_summary:
        # Insert AI summary after executive summary
        insert_point = report_content.find("## 广告主档案")
        if insert_point > 0:
            ai_summary_section = f"\n### AI 智能摘要\n\n{ai_summary}\n\n"
            report_content = report_content[:insert_point] + ai_summary_section + report_content[insert_point:]

    # Save report
    report_generator.save_report(report_content, "report.md")

    print("\n[Flow 4 Complete] Report generated and saved")
    return report_content


def main():
    """Main entry point - orchestrates all 4 flows"""
    print_banner()

    try:
        # Initialize router
        print("\nInitializing Model Router...")
        router = ModelRouter()
        print("Model Router initialized successfully")

        # Flow 1: Agent Analysis
        agent_profiles = flow1_agent_analysis(router)

        # Flow 2: Embedding & Matching
        embeddings, raw_matrix, weighted_matrix, match_details, top_matches = flow2_embedding_matching(router)

        # Flow 3: Negotiation
        negotiation_results = flow3_negotiation(router, top_matches)

        # Flow 4: Report Generation
        report_content = flow4_report_generation(
            router,
            embeddings,
            raw_matrix,
            weighted_matrix,
            match_details,
            negotiation_results
        )

        # Final statistics
        print("\n" + "=" * 60)
        print("EXECUTION COMPLETE")
        print("=" * 60)
        print(router.get_stats_summary())

        print("\n" + "=" * 60)
        print("   AdMatch AI MVP - Execution Complete")
        print(f"   End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("   Report saved to: report.md")
        print("=" * 60)

        return 0

    except ValueError as e:
        print(f"\n[ERROR] Configuration Error: {e}")
        print("Please ensure GEMINI_API_KEY environment variable is set.")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
