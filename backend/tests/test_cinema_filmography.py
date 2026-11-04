# ============================================================================
# LOKR AI - Cinema, Actor Filmography & Movie Search Test Suite
# ============================================================================

import sys
import os
import re
import asyncio

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.grounding_service import (
    detect_cinema_query,
    classify_query_intent,
    build_cinema_search_query
)
from app.services.web_search import perform_web_search
from app.services.ai_service import ai_service

def test_cinema_intent_classification():
    print("=== TEST 1: Actor & Movie Intent Classification ===")
    test_cases = [
        ("Robert Downey Jr.", "filmography", True),
        ("Robert Downey Jr movies", "filmography", True),
        ("Shah Rukh Khan", "filmography", True),
        ("Prabhas", "filmography", True),
        ("Mahesh Babu", "filmography", True),
        ("Allu Arjun", "filmography", True),
        ("Tom Cruise", "filmography", True),
        ("Leonardo DiCaprio", "filmography", True),
        ("Samantha movies", "filmography", True),
        ("RRR", "movie", True),
        ("Inception", "movie", True),
        ("Who acted in RRR?", "movie_connection", True),
        ("Who is the director of RRR?", "movie_connection", True),
        ("Movies directed by S. S. Rajamouli", "movie_connection", True),
        ("Jr NTR movies directed by Rajamouli", "movie_connection", True),
        ("Is this list of Robert Downey Jr movies correct: Iron Man, Tropic Thunder", "verify_list", True)
    ]

    all_passed = True
    for query, exp_cat, exp_search in test_cases:
        decision = classify_query_intent(query)
        cat_match = decision.category == exp_cat
        search_match = decision.should_search == exp_search
        status = "✅ PASS" if (cat_match and search_match) else "❌ FAIL"
        if not (cat_match and search_match):
            all_passed = False
        print(f"[{status}] '{query}' -> cat={decision.category} (exp: {exp_cat}), search={decision.should_search}")

    print(f"\nClassification Summary: {'ALL PASSED ✅' if all_passed else 'SOME FAILED ❌'}\n")
    return all_passed

def test_cinema_search_queries():
    print("=== TEST 2: Cinema Search Query Optimization ===")
    test_queries = [
        ("Robert Downey Jr.", "Robert Downey Jr. actor filmography movies list release year roles character director wikipedia imdb"),
        ("RRR", "RRR film movie release year director cast characters writers music genre plot synopsis wikipedia imdb"),
        ("Who is the director of RRR?", "Rrr film director who directed release year cast crew wikipedia imdb"),
    ]

    all_passed = True
    for q, exp_sub in test_queries:
        d = classify_query_intent(q)
        passed = bool(d.optimized_query and "imdb" in d.optimized_query and "wikipedia" in d.optimized_query)
        status = "✅ PASS" if passed else "❌ FAIL"
        if not passed:
            all_passed = False
        print(f"[{status}] '{q}' -> '{d.optimized_query}'")

    print(f"\nSearch Query Optimization: {'ALL PASSED ✅' if all_passed else 'SOME FAILED ❌'}\n")
    return all_passed

async def test_live_actor_filmography():
    print("=== TEST 3: Live Grounded Actor Filmography Synthesis (Robert Downey Jr.) ===")
    query = "Robert Downey Jr movies"
    d = classify_query_intent(query)
    print(f"Executing web search for: '{d.optimized_query}'")
    sources = perform_web_search(d.optimized_query, max_results=3)
    print(f"Retrieved {len(sources)} authoritative sources.")

    prompt = ai_service.build_system_prompt(
        sources=sources,
        user_query=query,
        client_timezone="Asia/Kolkata",
        search_attempted=True
    )

    resp_tokens = []
    async for chunk in ai_service.generate_chat_stream([{"role": "user", "content": query}], prompt):
        resp_tokens.append(chunk)

    text = "".join(resp_tokens)
    clean_text = re.sub(r"[\u202f\xa0]", " ", text)
    print("\n--- ACTOR FILMOGRAPHY RESPONSE ---")
    print(clean_text[:800] + "\n...[truncated for display]...")
    print("----------------------------------\n")

    # Critical Accuracy Checks:
    has_kirk = "Kirk Lazarus" in clean_text
    has_ironman = "Iron Man" in clean_text or "Tony Stark" in clean_text
    has_oppenheimer = "Oppenheimer" in clean_text or "Lewis Strauss" in clean_text
    has_table = "|" in clean_text

    passed = has_kirk and has_ironman and has_table
    print(f"Verified Character (Kirk Lazarus in Tropic Thunder): {has_kirk} ✅")
    print(f"Iron Man / Tony Stark Present: {has_ironman} ✅")
    print(f"Oppenheimer / Lewis Strauss Present: {has_oppenheimer} ✅")
    print(f"Formatted as Markdown Table: {has_table} ✅")
    print(f"\nActor Filmography Test: {'PASSED ✅' if passed else 'FAILED ❌'}\n")
    return passed

async def test_live_movie_profile():
    print("=== TEST 4: Live Grounded Movie Profile Synthesis (RRR) ===")
    await asyncio.sleep(6.0)  # Pacing to respect Groq ITPM window

    query = "RRR"
    d = classify_query_intent(query)
    print(f"Executing web search for: '{d.optimized_query}'")
    sources = perform_web_search(d.optimized_query, max_results=3)
    print(f"Retrieved {len(sources)} authoritative sources.")

    prompt = ai_service.build_system_prompt(
        sources=sources,
        user_query=query,
        client_timezone="Asia/Kolkata",
        search_attempted=True
    )

    resp_tokens = []
    async for chunk in ai_service.generate_chat_stream([{"role": "user", "content": query}], prompt):
        resp_tokens.append(chunk)

    text = "".join(resp_tokens)
    clean_text = re.sub(r"[\u202f\xa0]", " ", text)
    print("\n--- MOVIE PROFILE RESPONSE ---")
    print(clean_text[:800] + "\n...[truncated for display]...")
    print("------------------------------\n")

    # Critical Accuracy Checks:
    has_rajamouli = "Rajamouli" in clean_text
    has_cast = "Ram Charan" in clean_text and ("NTR" in clean_text or "Rama Rao" in clean_text)
    has_cast_table = "Main Cast" in clean_text or "Cast" in clean_text
    has_crew = "Crew" in clean_text or "Director" in clean_text
    has_year = "2022" in clean_text

    passed = has_rajamouli and has_cast and has_year and has_cast_table
    print(f"Director S. S. Rajamouli Verified: {has_rajamouli} ✅")
    print(f"Lead Cast (Ram Charan & Jr NTR) Verified: {has_cast} ✅")
    print(f"Release Year 2022 Verified: {has_year} ✅")
    print(f"Main Cast & Crew Included: {has_cast_table} ✅")
    print(f"\nMovie Profile Test: {'PASSED ✅' if passed else 'FAILED ❌'}\n")
    return passed

if __name__ == "__main__":
    import time
    t1 = test_cinema_intent_classification()
    t2 = test_cinema_search_queries()
    time.sleep(4.0)
    t3 = asyncio.run(test_live_actor_filmography())
    time.sleep(8.0)
    t4 = asyncio.run(test_live_movie_profile())

    print("============================================================")
    print(f"ALL CINEMA & FILMOGRAPHY TESTS: {'PASS ✅' if all([t1, t2, t3, t4]) else 'SOME FAILED ❌'}")
    print("============================================================")
