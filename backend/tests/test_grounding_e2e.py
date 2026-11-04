# ============================================================================
# LOKR AI - Comprehensive Grounding & Real-Time Accuracy Test Suite
# ============================================================================

import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.grounding_service import (
    classify_query_intent,
    rank_and_deduplicate_sources,
    score_source_authority
)
from app.services.web_search import should_search_web, perform_web_search
from app.services.date_time_service import get_live_time_snapshot, build_temporal_context
from app.services.ai_service import ai_service

def test_intent_classification():
    print("=== TEST 1: Intent Classification & Search Decision Layer ===")
    test_cases = [
        # (query, expected_intent, expected_search)
        ("What is the time right now?", "DATETIME_CLOCK", False),
        ("What is today's date?", "DATETIME_CLOCK", False),
        ("What time is it in New York?", "DATETIME_CLOCK", False),
        ("When is Diwali in 2026?", "SEARCH_MANDATORY", True),
        ("What date is Holi in 2026?", "SEARCH_MANDATORY", True),
        ("What is the latest version of Python?", "SEARCH_MANDATORY", True),
        ("Current weather in Mumbai", "SEARCH_MANDATORY", True),
        ("Who won the 2026 Super Bowl?", "SEARCH_MANDATORY", True),
        ("What is photosynthesis?", "GENERAL_KNOWLEDGE", False),
        ("Explain the quicksort algorithm in C++", "GENERAL_KNOWLEDGE", False),
        ("Who wrote Hamlet?", "GENERAL_KNOWLEDGE", False),
    ]

    all_passed = True
    for query, exp_intent, exp_search in test_cases:
        decision = classify_query_intent(query, client_timezone="Asia/Kolkata")
        actual_search = should_search_web(query, client_timezone="Asia/Kolkata")
        intent_val = getattr(decision.intent, "value", str(decision.intent))
        intent_match = intent_val == exp_intent
        search_match = actual_search == exp_search
        status = "✅ PASS" if (intent_match and search_match) else "❌ FAIL"
        if status.startswith("❌"):
            all_passed = False
        print(f"[{status}] Query: '{query}' -> Intent: {intent_val} (exp: {exp_intent}), Search: {actual_search} (exp: {exp_search})")
        if decision.optimized_query != query:
            print(f"         Enriched Query: '{decision.optimized_query}'")

    print(f"\nIntent Classification Summary: {'ALL PASSED ✅' if all_passed else 'SOME FAILED ❌'}\n")
    return all_passed

def test_source_authority_scoring():
    print("=== TEST 2: Domain Authority Scoring & Ranking ===")
    mock_sources = [
        {"title": "Spam Site Clickbait", "url": "https://www.quora.com/When-is-diwali", "snippet": "Someone answers...", "source_name": "Quora"},
        {"title": "Drik Panchang Diwali 2026", "url": "https://www.drikpanchang.com/diwali/diwali-date.html", "snippet": "Diwali on Sunday, November 8, 2026 according to the authentic Hindu Panchang calendar...", "source_name": "Drikpanchang"},
        {"title": "The Hindu News Report", "url": "https://www.thehindu.com/news/national/festival-dates-2026", "snippet": "National festival calendar announced by authorities for Diwali in November 2026...", "source_name": "Thehindu"},
        {"title": "Random Blog Post", "url": "https://randomblog123.com/post/diwali", "snippet": "Blog details about festival celebration and sweets...", "source_name": "Randomblog"},
        {"title": "Gov India Holiday List", "url": "https://india.gov.in/calendar-2026", "snippet": "Official Gazetted Holidays 2026 Diwali Amavasya...", "source_name": "India"},
    ]

    ranked = rank_and_deduplicate_sources(mock_sources, "Diwali 2026 date", max_results=5)
    print(f"Original Count: {len(mock_sources)} -> Ranked Count: {len(ranked)}")
    for i, s in enumerate(ranked, 1):
        print(f"  [{i}] ({s.get('source_name')}) {s.get('title')}")

    # Top sources should be authoritative (drikpanchang, india.gov.in, thehindu)
    top_names = [s.get("source_name", "").lower() for s in ranked[:2]]
    print(f"Top 2 Source Names: {top_names}")
    passed = any(n in ("drikpanchang", "india", "thehindu") for n in top_names)
    print(f"Authority Ranking Test: {'PASSED ✅' if passed else 'FAILED ❌'}\n")
    return passed

def test_live_web_search():
    print("=== TEST 3: Resilient Multi-Engine Web Search Live Execution ===")
    query = "Diwali 2026 date India"
    sources = perform_web_search(query, max_results=4, client_timezone="Asia/Kolkata")
    print(f"Live Search for '{query}': Retrieved {len(sources)} sources")
    for i, s in enumerate(sources, 1):
        print(f"  [{i}] [{s.get('source_name')}] {s.get('title')}\n      URL: {s.get('url')}\n      Snippet: {s.get('snippet')[:100]}...")

    passed = len(sources) > 0 and any("http" in s.get("url", "") for s in sources)
    print(f"Live Web Search Test: {'PASSED ✅' if passed else 'FAILED ❌'}\n")
    return passed

def test_prompt_injection():
    print("=== TEST 4: Grounded Prompt Construction & Anti-Hallucination Guardrails ===")
    mock_sources = [
        {
            "title": "Drik Panchang 2026 Diwali",
            "url": "https://www.drikpanchang.com/diwali/diwali-date.html",
            "source_name": "Drikpanchang",
            "snippet": "Diwali in 2026 will be celebrated on Sunday, November 8, 2026 according to the Hindu Panchang."
        }
    ]

    prompt_with_sources = ai_service.build_system_prompt(
        sources=mock_sources,
        user_query="When is Diwali in 2026?",
        client_timezone="Asia/Kolkata",
        search_attempted=True
    )

    has_verified = "VERIFIED REAL-TIME WEB GROUNDING SOURCES" in prompt_with_sources
    has_drik = "drikpanchang.com" in prompt_with_sources
    has_temporal = "ACCURATE REAL-TIME SYSTEM CLOCK & TEMPORAL CONTEXT" in prompt_with_sources

    prompt_no_sources = ai_service.build_system_prompt(
        sources=[],
        user_query="Who won the 2035 Mars Cup?",
        client_timezone="Asia/Kolkata",
        search_attempted=True
    )
    has_unverified_notice = "REAL-TIME WEB SEARCH NOTICE" in prompt_no_sources
    has_anti_hallucination = "I couldn't verify that information from a reliable source." in prompt_no_sources

    passed = all([has_verified, has_drik, has_temporal, has_unverified_notice, has_anti_hallucination])
    print(f"Grounding Prompt Injection Test: {'PASSED ✅' if passed else 'FAILED ❌'}\n")
    return passed

if __name__ == "__main__":
    t1 = test_intent_classification()
    t2 = test_source_authority_scoring()
    t3 = test_live_web_search()
    t4 = test_prompt_injection()

    print("============================================================")
    print(f"ALL TESTS: {'PASS ✅' if all([t1, t2, t3, t4]) else 'SOME TESTS FAILED ❌'}")
    print("============================================================")
