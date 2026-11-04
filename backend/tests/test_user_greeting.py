import sys
import os
import asyncio
from typing import Optional

sys.stdout.reconfigure(encoding="utf-8")

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.greeting_service import (
    extract_preferred_name,
    is_pure_greeting,
    generate_greeting_response,
    build_user_persona_instructions,
)
from app.services.ai_service import ai_service


def test_name_extraction():
    print("\n--- Test Suite 1: Preferred Name Extraction ---")
    test_cases = [
        ("J Lohithkrishna", "Lohith"),
        ("J. Lohithkrishna", "Lohith"),
        ("Jangiti Lohithkrishna", "Lohith"),
        ("Lohithkrishna", "Lohith"),
        ("Lohith Krishna", "Lohith"),
        ("Lohith", "Lohith"),
        ("John Doe", "John"),
        ("Alice Smith", "Alice"),
        ("Dr. Jane Watson", "Jane"),
        ("K. Rahul", "Rahul"),
        ("Mr. David Miller", "David"),
        ("Nani", "Nani"),
        ("Guest Explorer", None),
        ("Guest", None),
        ("User", None),
        ("Anonymous", None),
        ("", None),
        (None, None),
    ]

    for raw, expected in test_cases:
        actual = extract_preferred_name(raw)
        assert actual == expected, f"Failed for raw={raw!r}: expected {expected!r}, got {actual!r}"
        print(f"  [PASS] {str(raw)!r:25} -> {str(actual)!r}")


def test_pure_greetings():
    print("\n--- Test Suite 2: Pure Greeting Detection ---")
    truthy = [
        "Hi", "hi", "Hello", "hello", "Hey", "hey!", "Hi!", "Hello 👋",
        "Hi LOKR", "Hello LOKR AI", "Hey LOKR AI", "Hi there", "Hello there",
        "Good morning", "Good afternoon", "Good evening", "Greetings", "howdy"
    ]
    falsy = [
        "Hi, how are you?", "Hi, write a python script",
        "What is Python?", "Who are you?", "Explain recursion",
        "", None
    ]

    for t in truthy:
        assert is_pure_greeting(t) is True, f"Expected {t!r} to be pure greeting"
        print(f"  [PASS] Pure: {t!r}")

    for f in falsy:
        assert is_pure_greeting(f) is False, f"Expected {f!r} NOT to be pure greeting"
        print(f"  [PASS] Non-pure: {f!r}")


def test_greeting_responses():
    print("\n--- Test Suite 3: Greeting Response Exact & Varied Formatting ---")
    
    # 1. User says 'hi' (New user with name)
    r1 = generate_greeting_response(preferred_name="Lohith", is_returning_user=False, user_query="hi")
    assert "Hi Lohith! 👋" in r1 and "How can I help you today?" in r1
    print(f"  [PASS] 'hi' with name:\n{r1}")

    # 2. User says 'hello' (with name)
    r2 = generate_greeting_response(preferred_name="Lohith", is_returning_user=False, user_query="hello")
    assert "Hello Lohith! 👋" in r2 and "Nice to see you." in r2
    print(f"  [PASS] 'hello' with name:\n{r2}")

    # 3. User says 'hey' (with name)
    r3 = generate_greeting_response(preferred_name="Lohith", is_returning_user=False, user_query="hey")
    assert "Hey Lohith! 👋" in r3 and "What can I help you with today?" in r3
    print(f"  [PASS] 'hey' with name:\n{r3}")

    # 4. Returning user greeting
    r4 = generate_greeting_response(preferred_name="Lohith", is_returning_user=True, user_query="hi")
    assert "Welcome back, Lohith! 👋" in r4 and "What would you like to work on today?" in r4
    print(f"  [PASS] Returning user:\n{r4}")

    # 5. User without name
    r5 = generate_greeting_response(preferred_name=None, is_returning_user=False, user_query="hi")
    assert "Hi! 👋 How can I help you today?" in r5
    print(f"  [PASS] User without name:\n{r5}")

    # 6. 'Nani' restriction check
    assert "Nani" not in r1
    assert "Nani" not in r2
    assert "Nani" not in r3
    print("  [PASS] 'Nani' nickname is never used for Lohith.")


async def test_live_chat_flow():
    print("\n--- Test Suite 4: End-to-End Live Chat Stream Testing ---")
    import httpx

    client = httpx.AsyncClient(timeout=30.0)
    login_resp = await client.post('http://127.0.0.1:8000/api/auth/login', json={'email': 'test_greeting@lokr.ai', 'password': 'Password123!'})
    token = login_resp.json()['access_token']
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

    test_queries = [
        "hi",
        "hello",
        "hey",
        "how are you?",
        "what is your name?",
        "Write a 1-line Python code to reverse a list."
    ]

    for q in test_queries:
        print(f"\n>> Sending message: {q!r}")
        async with client.stream('POST', 'http://127.0.0.1:8000/api/ai/chat/stream', json={'content': q}, headers=headers) as resp:
            assert resp.status_code == 200, f"Error status {resp.status_code}"
            tokens = []
            status_received = False
            done_received = False
            async for line in resp.aiter_lines():
                if line.startswith('data: '):
                    import json
                    event = json.loads(line[6:])
                    if event.get('type') == 'status':
                        status_received = True
                    elif event.get('type') == 'token':
                        tokens.append(event.get('content', ''))
                    elif event.get('type') == 'done':
                        done_received = True

            full_reply = "".join(tokens).strip()
            print(f"   Status Indicator Received: {status_received}")
            print(f"   Done Event Received: {done_received}")
            print(f"   AI Response:\n{full_reply}")
            assert len(full_reply) > 0, f"Empty response received for query {q!r}!"
            assert done_received, f"Missing done event for query {q!r}!"


def run_all():
    test_name_extraction()
    test_pure_greetings()
    test_greeting_responses()
    asyncio.run(test_live_chat_flow())
    print("\n" + "="*60)
    print("  ALL MESSAGE FLOW & GREETING TESTS VERIFIED! (100% PASS)")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all()
