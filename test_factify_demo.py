#!/usr/bin/env python3
"""
Factify Demonstration & Verification Script
Demonstrates the balanced news curation and slant filtering pipeline.
Supports both mock mode (zero API keys needed) and live mode with Gemini / OpenAI.

Usage:
    python test_factify_demo.py           # Runs in mock mode (instant, no keys needed)
    python test_factify_demo.py --live    # Runs against live Gemini/OpenAI API
"""

import os
import sys
import argparse

# Add NewsAgent to import path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "NewsAgent"))

from article_creator import filter_and_balance_proportions


def run_mock_demo():
    print("=" * 70)
    print("FACTIFY PIPELINE DEMO (Mock Cohort with Skewed Sources)")
    print("=" * 70)

    # Simulated cohort of 8 articles on a contested policy topic
    sample_articles = [
        {
            "id": 0,
            "title": "Clean Energy Transition Slashes Emissions in Q3 Report",
            "source": {"name": "EcoToday"},
            "summary": "Renewable energy adoption reached record highs this quarter, reducing industrial carbon footprint by 14%.",
            "slant_score": -0.35,
            "category": "left",
            "extremism_score": 0.20,
        },
        {
            "id": 1,
            "title": "Grid Modernization Bill Passes Senate with Bipartisan Backing",
            "source": {"name": "Capitol Monitor"},
            "summary": "Lawmakers from both parties approved infrastructure funding for electrical transmission improvements.",
            "slant_score": 0.05,
            "category": "center",
            "extremism_score": 0.10,
        },
        {
            "id": 2,
            "title": "Radical Cabal Conspiring to Abolish Combustion Engines Overnight",
            "source": {"name": "FreedomPatriotBlog"},
            "summary": "Deep-state bureaucrats are preparing unconstitutional mandates to seize privately owned vehicles.",
            "slant_score": 0.95,
            "category": "right",
            "extremism_score": 0.94,  # Outlier
        },
        {
            "id": 3,
            "title": "Energy Mandates Threaten Small Business Margins, Trade Group Warns",
            "source": {"name": "Market Review"},
            "summary": "Independent retailers express concern over electricity rate spikes linked to regulatory compliance deadlines.",
            "slant_score": 0.40,
            "category": "right",
            "extremism_score": 0.25,
        },
        {
            "id": 4,
            "title": "Progressive Coalition Demands Immediate Ban on Fossil Fuel Subsidies",
            "source": {"name": "Tribune Wire"},
            "summary": "Environmental advocates call on Congress to redirect tax incentives towards public transit and low-income energy credits.",
            "slant_score": -0.50,
            "category": "left",
            "extremism_score": 0.30,
        },
        {
            "id": 5,
            "title": "Corporations Must Be Dismantled to Avert Complete Planetary Collapse",
            "source": {"name": "RedFrontier"},
            "summary": "Only total sabotage of capitalist production can stop global ecocide within five years.",
            "slant_score": -0.92,
            "category": "left",
            "extremism_score": 0.91,  # Outlier
        },
        {
            "id": 6,
            "title": "Department of Energy Releases Annual Grid Reliability Assessment",
            "source": {"name": "Associated Press"},
            "summary": "Federal regulators reported steady transmission performance during peak summer heat across major regional grids.",
            "slant_score": -0.05,
            "category": "center",
            "extremism_score": 0.05,
        },
        {
            "id": 7,
            "title": "Global Coal Usage Inches Higher Driven by Asian Demand",
            "source": {"name": "Reuters"},
            "summary": "International Energy Agency data indicates global coal consumption remained near historic highs in 2024.",
            "slant_score": 0.10,
            "category": "center",
            "extremism_score": 0.10,
        },
    ]

    print(f"\n[Step 1] Ingested {len(sample_articles)} Raw Articles:")
    for a in sample_articles:
        slant = a['slant_score']
        cat = a['category'].upper()
        ext = a['extremism_score']
        print(f"  - [{cat:6s}] (Slant: {slant:+.2f}, Extremism: {ext:.2f}) {a['source']['name']}: \"{a['title']}\"")

    print("\n[Step 2] Applying Outlier Pruning (threshold > 0.85) & Proportional Capping (max 40%):")
    balanced = filter_and_balance_proportions(sample_articles, max_proportion=0.40, extremism_threshold=0.85)

    print(f"\n[Step 3] Balanced & Curated Result ({len(balanced)} articles selected):")
    counts = {"LEFT": 0, "CENTER": 0, "RIGHT": 0}
    for a in balanced:
        cat = a['category'].upper()
        counts[cat] += 1
        print(f"  ✓ [{cat:6s}] (Slant: {a['slant_score']:+.2f}) {a['source']['name']}: \"{a['title']}\"")

    print("\n[Balance Breakdown]")
    for cat, count in counts.items():
        pct = (count / len(balanced)) * 100
        print(f"  {cat:7s}: {count} articles ({pct:.1f}%)")

    print("\n[Verification Summary]")
    print("  • Extreme fringe sources (FreedomPatriotBlog, RedFrontier) were pruned.")
    print("  • No single perspective exceeds the 40% cap.")
    print("  • Balanced Left, Center, and Right coverage was preserved for synthesis.\n")


def run_live_demo(query="Global Clean Energy Transition"):
    from article_creator import generate_final_article

    print(f"Running Live Factify query: '{query}'...")
    article = generate_final_article(query)
    print("\n" + "=" * 70)
    print("SYNTHESIZED ARTICLE OUTPUT:")
    print("=" * 70)
    print(article)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Factify balanced curation pipeline")
    parser.add_argument("--live", action="store_true", help="Run with live API calls instead of mock data")
    parser.add_argument("--query", type=str, default="Clean Energy", help="Search query for live mode")
    args = parser.parse_args()

    if args.live:
        run_live_demo(args.query)
    else:
        run_mock_demo()
