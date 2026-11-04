import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
import json
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.api.ai import chat_stream
from app.schemas.chat import SendMessageRequest
from app.services.greeting_service import (
    extract_preferred_name,
    is_pure_greeting,
    generate_greeting_response,
)

sys.stdout.reconfigure(encoding='utf-8')

TEST_QUERIES = [
    "hi",
    "hello",
    "What is Python?",
    "Who are you?",
    "RRR",
    "Who directed RRR?",
    "Prabhas movies",
    "Samantha movies",
    "Robert Downey Jr movies",
    "Tell me a joke",
]

def get_or_create_test_user(db: Session) -> User:
    user = db.query(User).filter(User.email == "test_lohith@lokr.ai").first()
    if not user:
        user = User(
            email="test_lohith@lokr.ai",
            name="J Lohithkrishna",
            password_hash="mock_hash_for_test"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

async def run_chat_query(user: User, db: Session, query: str, conversation_id: int = None):
    req = SendMessageRequest(
        conversation_id=conversation_id,
        content=query,
        enable_web_search=False,
        enable_image_generation=False
    )
    
    # Call chat_stream endpoint directly
    resp = await chat_stream(req=req, current_user=user, db=db)
    
    events = []
    tokens = []
    status_messages = []
    done_event = None
    
    async for raw_chunk in resp.body_iterator:
        lines = raw_chunk.strip().split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("data: "):
                data_str = line[6:]
                try:
                    ev = json.loads(data_str)
                    events.append(ev)
                    ev_type = ev.get("type")
                    if ev_type == "token":
                        tokens.append(ev.get("content", ""))
                    elif ev_type == "status":
                        status_messages.append(ev.get("message", ""))
                    elif ev_type == "done":
                        done_event = ev
                except Exception:
                    pass

    full_text = "".join(tokens).strip()
    return {
        "query": query,
        "token_count": len(tokens),
        "full_text": full_text,
        "status_messages": status_messages,
        "done": done_event is not None,
        "done_data": done_event
    }

async def main():
    print("=" * 70)
    print("LOKR AI CHATBOT FINAL VERIFICATION SUITE")
    print("=" * 70)

    # 1. Test greeting unit logic
    print("\n--- 1. Testing Greeting Logic & Persona Protection ---")
    assert extract_preferred_name("J Lohithkrishna") == "Lohith", "Failed extracting Lohith"
    assert extract_preferred_name("J. Lohithkrishna") == "Lohith"
    assert extract_preferred_name("Lohith Krishna") == "Lohith"
    assert extract_preferred_name("Guest Explorer") is None
    assert extract_preferred_name("") is None
    
    g_hi = generate_greeting_response(preferred_name="Lohith", user_query="hi")
    assert "Hi Lohith!" in g_hi and "Nani" not in g_hi, f"Unexpected g_hi: {g_hi}"
    
    g_hello = generate_greeting_response(preferred_name="Lohith", user_query="hello")
    assert "Hello Lohith!" in g_hello and "Nice to see you" in g_hello, f"Unexpected g_hello: {g_hello}"
    
    g_hey = generate_greeting_response(preferred_name="Lohith", user_query="hey")
    assert "Hey Lohith!" in g_hey, f"Unexpected g_hey: {g_hey}"
    
    g_anon = generate_greeting_response(preferred_name=None, user_query="hi")
    assert "Hi! 👋 How can I help you today?" in g_anon, f"Unexpected g_anon: {g_anon}"
    print("  [PASS] All Greeting logic assertions passed.")

    # 2. Test Live Chat Endpoint for all 10 queries
    print("\n--- 2. Testing 10 Target Queries on Real Chat Response Pipeline ---")
    db = SessionLocal()
    try:
        user = get_or_create_test_user(db)
        print(f"Authenticated Test User: {user.name} (Preferred: {user.preferred_name})")
        
        # Create a fresh conversation for this test run
        conv = Conversation(user_id=user.id, title="Test Suite Conversation")
        db.add(conv)
        db.commit()
        db.refresh(conv)
        conv_id = conv.id

        results = []
        for idx, query in enumerate(TEST_QUERIES, 1):
            print(f"\n[Test {idx}/10] Query: '{query}'")
            res = await run_chat_query(user, db, query, conversation_id=conv_id)
            results.append(res)
            
            # Assertions
            has_response = bool(res["full_text"])
            has_done = res["done"]
            calls_nani = "nani" in res["full_text"].lower() and "nani" not in query.lower()
            
            print(f"  Tokens: {res['token_count']} | Length: {len(res['full_text'])} | Done Event: {has_done}")
            print(f"  Preview: {repr(res['full_text'][:120])}")
            if calls_nani:
                print("  [ERROR] Chatbot illegally called user 'Nani'!")
            if not has_response:
                print(f"  [ERROR] Response is EMPTY for '{query}'!")
            
            assert has_response, f"Query '{query}' produced empty response!"
            assert has_done, f"Query '{query}' failed to emit done event!"
            assert not calls_nani, f"Query '{query}' called user 'Nani'!"

        print("\n" + "=" * 70)
        print("ALL 10 TARGET QUERIES PASSED SUCCESSFULLY!")
        print("=" * 70)
        for idx, r in enumerate(results, 1):
            print(f"{idx}. '{r['query']}' -> {r['token_count']} tokens -> OK")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
