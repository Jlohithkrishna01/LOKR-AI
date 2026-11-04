import re
from typing import Optional

# Titles / honorifics to strip
TITLES_PATTERN = r"^(dr\.?|mr\.?|mrs\.?|ms\.?|prof\.?|er\.?|shri\.?|smt\.?)\s+"

# Known compound suffixes in personal / Indian names
COMPOUND_SUFFIXES = (
    "krishna", "kumar", "prasad", "reddy", "rao", "sharma",
    "singh", "babu", "teja", "vardhan", "nathan", "murthy"
)

# Generic / placeholder names that should not be used as real user names
GENERIC_NAMES = {
    "guest", "guest explorer", "user", "anonymous", "none",
    "null", "test", "tester", "benchmark tester", "unknown",
    "admin", "developer", "there"
}

# Pure greeting tokens
PURE_GREETING_WORDS = {
    "hi", "hello", "hey", "hey there", "hi there", "hello there",
    "greetings", "good morning", "good afternoon", "good evening",
    "howdy", "yo", "welcome", "hi lokr", "hello lokr", "hey lokr",
    "hi lokr ai", "hello lokr ai", "hey lokr ai"
}

def extract_preferred_name(full_name: Optional[str]) -> Optional[str]:
    """
    Extracts the user's natural first/preferred name from their full profile name.
    
    Examples:
    - 'J Lohithkrishna' -> 'Lohith'
    - 'J. Lohithkrishna' -> 'Lohith'
    - 'Jangiti Lohithkrishna' -> 'Lohith'
    - 'Lohithkrishna' -> 'Lohith'
    - 'Lohith Krishna' -> 'Lohith'
    - 'John Doe' -> 'John'
    - 'Alice Smith' -> 'Alice'
    - 'Dr. Jane Watson' -> 'Jane'
    - 'K. Rahul' -> 'Rahul'
    - 'Guest Explorer' -> None
    - '' or None -> None
    """
    if not full_name:
        return None

    name = full_name.strip()
    if not name or len(name) < 2:
        return None

    if name.lower() in GENERIC_NAMES:
        return None

    # 1. Remove salutations/titles (e.g., 'Dr.', 'Mr.', 'Prof.')
    name = re.sub(TITLES_PATTERN, "", name, flags=re.IGNORECASE).strip()

    tokens = [t for t in re.split(r"\s+", name) if t]
    if not tokens:
        return None

    # 2. Filter out single-letter initials (with or without dot), e.g. 'J' or 'J.' or 'K.'
    non_initial_tokens = []
    for t in tokens:
        clean_t = t.rstrip(".")
        # If token is longer than 1 character and not an all-caps 2-letter acronym
        if len(clean_t) > 1 and not (len(clean_t) == 2 and clean_t.isupper()):
            non_initial_tokens.append(clean_t)

    # If all tokens were initials (e.g. 'A. B.'), fall back to the first token stripped of dot
    candidate = non_initial_tokens[0] if non_initial_tokens else tokens[0].rstrip(".")

    # 3. Handle known surnames if placed first, e.g. 'Jangiti Lohithkrishna'
    if candidate.lower() == "jangiti" and len(non_initial_tokens) > 1:
        candidate = non_initial_tokens[1]

    # 4. Handle compound Indian names: e.g. 'Lohithkrishna' -> 'Lohith'
    candidate_lower = candidate.lower()
    for suffix in COMPOUND_SUFFIXES:
        if candidate_lower.endswith(suffix) and len(candidate_lower) > len(suffix) + 2:
            base = candidate[: -len(suffix)]
            candidate = base.capitalize()
            break

    candidate = candidate.strip().capitalize()
    return candidate if candidate and candidate.lower() not in GENERIC_NAMES else None


def is_pure_greeting(text: Optional[str]) -> bool:
    """
    Detects if a user message is purely a greeting.
    """
    if not text:
        return False
    # Remove punctuation & emojis
    cleaned = re.sub(r"[^\w\s]", "", text.strip().lower())
    # Remove lokr, lokr ai, ai, assistant, bot
    cleaned = re.sub(r"\b(lokr\s+ai|lokr|ai|assistant|bot)\b", "", cleaned).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned in PURE_GREETING_WORDS


def generate_greeting_response(
    preferred_name: Optional[str] = None,
    is_returning_user: bool = False,
    user_query: Optional[str] = None
) -> str:
    """
    Generates varied, professional, personal AI assistant greeting responses.
    
    Examples:
    - User says 'hi':
      Hi Lohith! 👋
      How can I help you today?

    - User says 'hello':
      Hello Lohith! 👋
      Nice to see you. How can I help you today?

    - User says 'hey':
      Hey Lohith! 👋
      What can I help you with today?

    - Returning user:
      Welcome back, Lohith! 👋
      What would you like to work on today?

    - User name unavailable:
      Hi! 👋 How can I help you today?
    """
    clean_query = (user_query or "").strip().lower()

    # Determine greeting variant based on user input
    if "hello" in clean_query:
        if preferred_name:
            return f"Hello {preferred_name}! 👋\nNice to see you. How can I help you today?"
        return "Hello! 👋\nNice to see you. How can I help you today?"

    elif "hey" in clean_query:
        if preferred_name:
            return f"Hey {preferred_name}! 👋\nWhat can I help you with today?"
        return "Hey! 👋\nWhat can I help you with today?"

    elif "good morning" in clean_query:
        if preferred_name:
            return f"Good morning, {preferred_name}! 👋\nHow can I help you today?"
        return "Good morning! 👋\nHow can I help you today?"

    elif "good afternoon" in clean_query:
        if preferred_name:
            return f"Good afternoon, {preferred_name}! 👋\nHow can I help you today?"
        return "Good afternoon! 👋\nHow can I help you today?"

    elif "good evening" in clean_query:
        if preferred_name:
            return f"Good evening, {preferred_name}! 👋\nHow can I help you today?"
        return "Good evening! 👋\nHow can I help you today?"

    # Returning user variant if no specific variant matched
    if is_returning_user:
        if preferred_name:
            return f"Welcome back, {preferred_name}! 👋\nWhat would you like to work on today?"
        return "Welcome back! 👋\nWhat would you like to work on today?"

    # Standard 'hi' / default greeting
    if preferred_name:
        return f"Hi {preferred_name}! 👋\nHow can I help you today?"
    return "Hi! 👋 How can I help you today?"


def build_user_persona_instructions(
    user_name: Optional[str] = None,
    preferred_name: Optional[str] = None,
    is_returning_user: bool = False,
    saved_memory: Optional[str] = None
) -> str:
    """
    Constructs the dynamic persona and user identity block for the AI system prompt.
    """
    lines = [
        "=== AUTHENTICATED USER IDENTITY & PERSONALIZATION ===",
    ]

    if preferred_name or user_name:
        lines.append(f"- User Profile Full Name: {user_name or 'Not specified'}")
        lines.append(f"- User Preferred First Name: {preferred_name or 'Use profile name naturally'}")
        lines.append(f"- User Status: {'Returning user (has previous conversations/history)' if is_returning_user else 'Active user session'}")
        lines.append(
            "- Personalization Instructions:\n"
            f"  * Address this user naturally by their first/preferred name '{preferred_name or user_name}'.\n"
            "  * IMPORTANT RESTRICTION: Do NOT call the user 'Nani' unless the user has explicitly chosen Nani as their preferred name.\n"
            "  * Do NOT use their full name unless specifically appropriate (e.g. formal document preparation).\n"
            "  * Do NOT repeat their name in every response. Use it naturally and selectively, mainly in greetings, introductions, and personalized responses.\n"
            "  * Vary greetings naturally based on the user's greeting:\n"
            f"    - When user says 'hi': 'Hi {preferred_name or 'there'}! 👋\\nHow can I help you today?'\n"
            f"    - When user says 'hello': 'Hello {preferred_name or 'there'}! 👋\\nNice to see you. How can I help you today?'\n"
            f"    - When user says 'hey': 'Hey {preferred_name or 'there'}! 👋\\nWhat can I help you with today?'\n"
            f"    - When user returns: 'Welcome back, {preferred_name or 'there'}! 👋\\nWhat would you like to work on today?'"
        )
    else:
        lines.append("- User Profile Name: Not available (unauthenticated or name not set in profile).")
        lines.append(f"- User Status: {'Returning user' if is_returning_user else 'New user session'}")
        lines.append(
            "- Personalization Instructions:\n"
            "  * CRITICAL: Do NOT guess, assume, or invent a user name.\n"
            "  * Do NOT call the user 'Nani' or any other assumed nickname.\n"
            "  * Greet naturally without a name:\n"
            "    - When user says 'hi': 'Hi! 👋 How can I help you today?'\n"
            "    - When user says 'hello': 'Hello! 👋 Nice to see you. How can I help you today?'\n"
            "    - When user says 'hey': 'Hey! 👋 What can I help you with today?'\n"
            "    - When returning: 'Welcome back! 👋 What would you like to work on today?'\n"
            "  * Keep tone professional, friendly, clean, and natural."
        )

    if saved_memory and saved_memory.strip():
        lines.append(f"- User Saved Memory & Preferences:\n{saved_memory.strip()}")

    lines.append("=== END AUTHENTICATED USER IDENTITY ===")
    return "\n".join(lines)
