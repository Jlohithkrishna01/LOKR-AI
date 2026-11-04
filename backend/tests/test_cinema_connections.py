import sys, os, re, asyncio
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.grounding_service import classify_query_intent
from app.services.web_search import perform_web_search
from app.services.ai_service import ai_service

async def test_actor_director_connection():
    print("=== TEST A: Actor-Director Collaboration (Jr NTR & Rajamouli) ===")
    query = "Jr NTR movies directed by Rajamouli"
    d = classify_query_intent(query)
    sources = perform_web_search(d.optimized_query, max_results=3)
    prompt = ai_service.build_system_prompt(sources=sources, user_query=query, search_attempted=True)
    tokens = []
    async for chunk in ai_service.generate_chat_stream([{"role": "user", "content": query}], prompt):
        tokens.append(chunk)
    text = "".join(tokens)
    clean_text = re.sub(r"[\u202f\xa0]", " ", text)
    print("\n--- RESPONSE ---")
    print(clean_text[:600] + "...")
    has_simhadri = "Simhadri" in clean_text
    has_yamadonga = "Yamadonga" in clean_text
    has_rrr = "RRR" in clean_text
    passed = (has_simhadri or has_yamadonga) and has_rrr
    print(f"Collaborations Identified (Simhadri/Yamadonga & RRR): {passed} ✅")
    return passed

async def test_ambiguous_movie_title():
    print("\n=== TEST B: Ambiguous Movie Title Disambiguation ('Don') ===")
    query = "Don"
    d = classify_query_intent(query)
    sources = perform_web_search(d.optimized_query, max_results=3)
    prompt = ai_service.build_system_prompt(sources=sources, user_query=query, search_attempted=True)
    tokens = []
    async for chunk in ai_service.generate_chat_stream([{"role": "user", "content": query}], prompt):
        tokens.append(chunk)
    text = "".join(tokens)
    clean_text = re.sub(r"[\u202f\xa0]", " ", text)
    print("\n--- RESPONSE ---")
    print(clean_text[:600] + "...")
    has_disambiguation = ("1978" in clean_text or "2006" in clean_text or "Amitabh" in clean_text or "Shah Rukh" in clean_text or "multiple" in clean_text.lower())
    print(f"Ambiguity / Multiple Releases Handled: {has_disambiguation} ✅")
    return has_disambiguation

async def test_user_list_verification():
    print("\n=== TEST C: User-Submitted List Verification ===")
    query = "Is this list of Robert Downey Jr movies correct: 1. Iron Man (2008) - Tony Stark, 2. Tropic Thunder (2008) - Tugg Speedman"
    d = classify_query_intent(query)
    sources = perform_web_search(d.optimized_query, max_results=3)
    prompt = ai_service.build_system_prompt(sources=sources, user_query=query, search_attempted=True)
    tokens = []
    async for chunk in ai_service.generate_chat_stream([{"role": "user", "content": query}], prompt):
        tokens.append(chunk)
    text = "".join(tokens)
    clean_text = re.sub(r"[\u202f\xa0]", " ", text)
    print("\n--- RESPONSE ---")
    print(clean_text)
    # Check that it identifies Tropic Thunder role as Kirk Lazarus (correcting Tugg Speedman)
    has_lazarus = "Kirk Lazarus" in clean_text
    has_correction = ("Correct" in clean_text or "Incorrect" in clean_text or "Correction" in clean_text or "❌" in clean_text or "✅" in clean_text or "🔄" in clean_text)
    passed = has_lazarus and has_correction
    print(f"Correctly identified Kirk Lazarus and flagged incorrect role: {passed} ✅")
    return passed

async def main():
    a = await test_actor_director_connection()
    await asyncio.sleep(10.0)
    b = await test_ambiguous_movie_title()
    await asyncio.sleep(10.0)
    c = await test_user_list_verification()
    print("\n============================================================")
    print(f"ALL CINEMA CONNECTION TESTS: {'PASS ✅' if all([a, b, c]) else 'SOME FAILED ❌'}")
    print("============================================================")

if __name__ == "__main__":
    asyncio.run(main())
