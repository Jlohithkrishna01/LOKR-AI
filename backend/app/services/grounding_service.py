# ============================================================================
# LOKR AI - Grounding & Freshness Decision Engine
# ============================================================================

import re
from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple
from urllib.parse import urlparse

from app.services.date_time_service import is_datetime_query

# Stable general knowledge patterns (should NEVER trigger web search)
GENERAL_KNOWLEDGE_PATTERNS = [
    r"^(what is|explain|define|how does|how do|why is|what are)\s+(photosynthesis|mitosis|gravity|relativity|evolution|dna|rna|quantum|calculus|algebra|trigonometry|thermodynamics)\b",
    r"^(what is|explain|how does)\s+(python|javascript|typescript|c\+\+|java|rust|html|css|sql|docker|git|linux|tcp/ip|http|binary search|quicksort|merge sort|bubble sort|linked list|hash map|tree|graph algorithm|recursion)\b",
    r"^(write|code|create|implement|give me a)\s+(python|js|javascript|ts|code|function|class|algorithm|regex|sql query|script|component)\b",
    r"^(who wrote|who painted|who composed)\s+(hamlet|macbeth|mona lisa|odyssey|iliad|symphony)\b",
    r"^(what is the capital of|where is)\s+(france|germany|italy|spain|japan|canada|australia|egypt|brazil)\b",
    r"^(convert|calculate|solve|what is)\s+[0-9\+\-\*\/\^\(\)\.\s]+\b",
    r"\b(syntax of|example of|difference between abstract class and interface|difference between let and const|how to sort an array)\b",
]

# Mandatory freshness triggers
MANDATORY_FRESHNESS_PATTERNS = [
    # Explicit temporal cues
    r"\b(latest|current|today|now|recent|recently|this week|this month|this year|upcoming|newest|breaking)\b",
    r"\b(2025|2026|2027)\b",

    # Festivals and religious calendars (Must verify with Panchang/authoritative calendar)
    r"\b(diwali|deepavali|dhanteras|choti diwali|bhai dooj|govardhan puja)\b",
    r"\b(holi|holika dahan|rangwali holi|dhulandi)\b",
    r"\b(ugadi|gudi padwa|vishu|puthandu|baisakhi|bihu|pana sankranti)\b",
    r"\b(dussehra|dasara|vijayadashami|durga puja|navratri|navaratri|garba)\b",
    r"\b(ganesh chaturthi|vinayaka chavithi|ganesh visarjan)\b",
    r"\b(raksha bandhan|rakhi|janmashtami|krishna janmashtami|gokulashtami)\b",
    r"\b(eid|eid ul fitr|eid ul adha|bakrid|ramadan|ramzan|muharram|milad un nabi)\b",
    r"\b(christmas|good friday|easter|ash wednesday|pentecost|thanksgiving)\b",
    r"\b(pongal|makar sankranti|sankranti|lohri|chath puja|chhat)\b",
    r"\b(maha shivaratri|shivratri|guru nanak jayanti|gurpurab|buddha purnima|mahavir jayanti)\b",
    r"\b(when is|what date is|date of|muhurat|puja timing|tithi|panchang)\s+([a-zA-Z\s]+)\b",

    # Weather and environmental
    r"\b(weather|temperature|forecast|rain|rainfall|storm|cyclone|monsoon|aqi|air quality|pollution level)\b",

    # Sports scores, schedules, and standings
    r"\b(score|match score|live score|who won|who is winning|points table|standings|fixture|schedule|ipl|world cup|olympics|champions league|premier league|formula 1|f1|wimbledon)\b",

    # Financial, stocks, cryptos, and commodities
    r"\b(stock price|share price|crypto price|market cap|bitcoin price|btc price|ethereum price|eth price|gold price|silver price|petrol price|diesel price|inflation rate|interest rate|repo rate|nifty|sensex)\b",

    # Technology releases and versions
    r"\b(version|latest release|changelog|release notes|what's new in|new features in|firmware update)\s+(python|ios|android|windows|react|node|nextjs|tailwind|ubuntu|macos|gpt|claude|gemini)\b",
    r"\b(iphone [0-9]+|pixel [0-9]+|samsung galaxy s[0-9]+|macbook|rtx [0-9]+)\s+(price|release date|specs|features)\b",

    # Government rules, schemes, policies, announcements
    r"\b(government scheme|rules|guidelines|policy|circular|gazette|notification|subsidy|yojana|ration card|aadhaar|pan card|passport renewal|visa rules|traffic fine|tax slab|budget|gst rate)\b",

    # Examinations, admissions, recruitment, deadlines
    r"\b(exam date|admit card|hall ticket|application deadline|last date to apply|results declared|cutoff|answer key|upsc|jee|neet|gate|cat|ssc|ibps|cbse)\b",

    # Train, flight, and travel status
    r"\b(flight status|train status|train timing|pnr status|railway schedule|flight delay|metro timing)\b",

    # Current role holders and public figures
    r"\b(who is the (current|new|latest|present))\s+(prime minister|president|ceo|chief justice|governor|chief minister|captain|secretary)\b",
]

# High-authority domains categorized for domain boosting
AUTHORITATIVE_DOMAINS: Dict[str, int] = {
    # Official Cinema & Entertainment databases (+50)
    "imdb.com": 50, "rottentomatoes.com": 45, "themoviedb.org": 45,
    "afi.com": 45, "boxofficemojo.com": 40, "metacritic.com": 40,
    "variety.com": 40, "hollywoodreporter.com": 40, "deadline.com": 40,
    "filmcompanion.in": 40, "greatandhra.com": 35, "123telugu.com": 35,
    "idlebrain.com": 35, "bollywoodhungama.com": 35, "cinestaan.com": 35,
    "indiewire.com": 40, "empireonline.com": 35, "rogerebert.com": 40,
    "wikipedia.org": 40,

    # Government & official Indian/Global institutions (+50)
    "gov.in": 50, "nic.in": 50, "gov": 50, "gov.uk": 50, "europa.eu": 50,
    "rbi.org.in": 50, "isro.gov.in": 50, "upsc.gov.in": 50, "cbse.gov.in": 50,
    "incometax.gov.in": 50, "epfindia.gov.in": 50, "uidai.gov.in": 50,
    "mohfw.gov.in": 50, "who.int": 50, "un.org": 50, "nasa.gov": 50,

    # Primary festival & calendar authorities (+45)
    "drikpanchang.com": 45, "muhuratchoghadiya.com": 40, "prokerala.com": 35,
    "panchangam.com": 35, "timeanddate.com": 45,

    # Official documentation & vendor websites (+40)
    "python.org": 45, "docs.python.org": 45, "developer.mozilla.org": 45,
    "react.dev": 45, "nodejs.org": 45, "github.com": 40, "microsoft.com": 40,
    "apple.com": 40, "google.com": 40, "kernel.org": 45,

    # Recognized quality news organizations (+35)
    "reuters.com": 40, "apnews.com": 40, "bbc.com": 40, "bloomberg.com": 40,
    "thehindu.com": 35, "indianexpress.com": 35, "ndtv.com": 30,
    "timesofindia.indiatimes.com": 30, "hindustantimes.com": 30,
    "livemint.com": 35, "economictimes.indiatimes.com": 35,
    "moneycontrol.com": 35, "aljazeera.com": 35, "theguardian.com": 35,

    # Official sports authorities (+40)
    "icc-cricket.com": 45, "bcci.tv": 45, "fifa.com": 45, "olympics.com": 45,
    "espncricinfo.com": 40, "premierleague.com": 45,

    # Universities & research (+35)
    "edu": 35, "ac.in": 35, "ac.uk": 35,
    "wikipedia.org": 30, "britannica.com": 35,
}

# Domains to penalize or exclude (SEO spam / scraper farms)
LOW_QUALITY_DOMAINS = [
    "pinterest.com", "quora.com", "facebook.com", "instagram.com",
    "tiktok.com", "reddit.com", "tumblr.com", "answers.yahoo.com",
    "coursehero.com", "chegg.com"
]

@dataclass
class GroundingDecision:
    intent: str  # "DATETIME_CLOCK", "SEARCH_MANDATORY", "SEARCH_VERIFICATION", "GENERAL_KNOWLEDGE"
    should_search: bool
    optimized_query: str
    category: str
    target_location: Optional[str] = None
    target_year: Optional[str] = None

def extract_year_context(query: str) -> Optional[str]:
    """Finds explicit 4-digit years like 2025, 2026, 2027."""
    m = re.search(r"\b(202[4-9]|203[0-5])\b", query)
    return m.group(1) if m else None

def extract_festival_context(query: str) -> Optional[str]:
    """Detects and returns canonical festival name if present."""
    festivals = [
        "diwali", "deepavali", "dhanteras", "holi", "ugadi", "gudi padwa",
        "dussehra", "dasara", "durga puja", "navratri", "ganesh chaturthi",
        "raksha bandhan", "krishna janmashtami", "eid", "ramadan", "christmas",
        "pongal", "makar sankranti", "maha shivaratri", "baisakhi", "lohri"
    ]
    q_low = query.lower()
    for f in festivals:
        if f in q_low:
            return f.title()
    return None

# Curated set of widely-known global, Indian, and international actors/actresses/directors
KNOWN_ACTORS = {
    # Hollywood & Global Icons
    "robert downey jr", "robert downey jr.", "rdj", "tom cruise", "leonardo dicaprio",
    "brad pitt", "johnny depp", "keanu reeves", "christian bale", "cillian murphy",
    "christopher nolan", "quentin tarantino", "martin scorsese", "steven spielberg",
    "james cameron", "denzel washington", "morgan freeman", "tom hanks", "al pacino",
    "robert de niro", "harrison ford", "will smith", "matt damon", "hugh jackman",
    "ryan reynolds", "chris evans", "chris hemsworth", "mark ruffalo", "benedict cumberbatch",
    "tom hiddleston", "samuel l jackson", "paul rudd", "jeremy renner", "sebastian stan",
    "chadwick boseman", "michael b jordan", "don cheadle", "vin diesel", "dwayne johnson",
    "the rock", "jason statham", "sylvester stallone", "arnold schwarzenegger", "bruce willis",
    "jackie chan", "jet li", "meryl streep", "scarlett johansson", "emma stone",
    "anne hathaway", "cate blanchett", "kate winslet", "natalie portman", "margot robbie",
    "zendaya", "florence pugh", "timothee chalamet", "austin butler", "joaquin phoenix",
    "heath ledger", "anthony hopkins", "gary oldman", "daniel day-lewis", "matthew mcconaughey",

    # Indian Cinema: Telugu, Hindi, Tamil, Kannada, Malayalam
    "shah rukh khan", "srk", "salman khan", "aamir khan", "amitabh bachchan",
    "hrithik roshan", "ranbir kapoor", "ranveer singh", "ajay devgn", "akshay kumar",
    "prabhas", "mahesh babu", "allu arjun", "ram charan", "jr ntr", "ntr", "jr. ntr",
    "pawan kalyan", "chiranjeevi", "balakrishna", "venkatesh", "nagarjuna",
    "nani", "vijay deverakonda", "ravi teja", "adivi sesh", "siddhu jonnalagadda",
    "rajinikanth", "kamal haasan", "vijay", "thalapathy vijay", "ajith", "ajith kumar",
    "suriya", "vikram", "chiyaan vikram", "dhanush", "sivakarthikeyan", "karthi",
    "silambarasan", "simbu", "yash", "rishab shetty", "rakshit shetty", "sudeep",
    "kichcha sudeep", "darshan", "mammootty", "mohanlal", "dulquer salmaan",
    "fahadh faasil", "prithviraj", "prithviraj sukumaran", "tovino thomas", "nivin pauly",
    "samantha", "samantha ruth prabhu", "nayanthara", "trisha", "trisha krishnan",
    "anushka shetty", "tamannaah", "tamannaah bhatia", "rashmika mandanna", "keerthy suresh",
    "sai pallavi", "pooja hegde", "mrunal thakur", "deepika padukone", "alia bhatt",
    "katrina kaif", "kareena kapoor", "priyanka chopra", "aishwarya rai", "kangana ranaut",
    "kiara advani", "kriti sanon", "shraddha kapoor", "vidya balan", "tabu",
    "s. s. rajamouli", "rajamouli", "ss rajamouli", "prashanth neel", "sukumar",
    "trivikram", "lokesh kanagaraj", "mani ratnam", "shankar", "atlee",
    "sandeep reddy vanga", "vetrimaran", "anurag kashyap"
}

# Curated set of widely-known landmark movie titles
KNOWN_MOVIES = {
    # Indian Cinema Landmarks
    "rrr", "baahubali", "baahubali 2", "kgf", "kgf chapter 1", "kgf chapter 2",
    "pushpa", "pushpa 2", "kalki 2898 ad", "devara", "salaar", "jawan",
    "pathaan", "dangal", "pk", "3 idiots", "sholay", "lagaan", "stree", "stree 2",
    "animal", "kantara", "jailer", "leo", "vikram", "master", "kaithi", "don",
    "magadheera", "eega", "pokiri", "athadu", "businessman", "okkadu",
    "ala vaikunthapurramuloo", "sarileru neekevvaru", "bharat ane nenu", "srimanthudu",
    "dookudu", "arya", "arya 2", "desamuduru", "julayi", "race gurram",
    "sarrainodu", "duvvada jagannadham", "rangasthalam", "dhruva", "nannaku prematho",
    "janatha garage", "aravinda sametha", "temper", "simhadri", "yamadonga",
    "chatrapathi", "mirchi", "varsham", "darling", "mr perfect", "billa",
    "saaho", "radhe shyam", "adipurush", "jersey", "arjun reddy", "kabir singh",

    # Hollywood & World Cinema Landmarks
    "inception", "interstellar", "oppenheimer", "the dark knight", "dark knight",
    "the godfather", "pulp fiction", "fight club", "the matrix", "matrix",
    "goodfellas", "gladiator", "dune", "dune part two", "titanic", "avatar",
    "avatar the way of water", "parasite", "spirited away", "whiplash",
    "la la land", "joker", "iron man", "the avengers", "avengers", "avengers endgame",
    "infinity war", "spider-man", "spiderman", "batman", "superman", "top gun",
    "top gun maverick", "mission impossible", "john wick", "casablanca",
    "citizen kane", "psycho", "forrest gump", "schindler's list", "shawshank redemption"
}

def detect_cinema_query(query: str) -> Optional[Tuple[str, str, str]]:
    """
    Detects whether the prompt is about an actor filmography, movie profile, or cinema connection.
    Returns: (category, subcategory, target_entity) or None.
    """
    cleaned = query.strip()
    low = cleaned.lower()
    norm = re.sub(r"[^\w\s]", "", low).strip()

    # 1. Verification of user-provided movie list
    if re.search(r"\b(is this|check this|verify this)\b.*?\b(movie|film|filmography|list|cast)\b", low):
        return ("verify_list", "verify", cleaned)

    # 2. Connection: Who directed / Director of movie
    m_dir = re.search(r"\bwho\s+(?:is\s+the\s+director\s+of|directed)\s+([a-zA-Z0-9\s,.-]+?)(?:\s*\?|\s*$)", low)
    if m_dir:
        target = m_dir.group(1).strip()
        target = re.sub(r"^(the|this|that)\s+", "", target).strip()
        return ("movie_connection", "director", target.title())

    # 3. Connection: Who acted in / Cast of movie
    m_cast = re.search(r"\bwho\s+(?:acted\s+in|stars\s+in|is\s+in|is\s+the\s+cast\s+of)\s+([a-zA-Z0-9\s,.-]+?)(?:\s*\?|\s*$)", low)
    if m_cast:
        target = m_cast.group(1).strip()
        target = re.sub(r"^(the|this|that)\s+", "", target).strip()
        return ("movie_connection", "cast", target.title())

    # 4. Connection: Who played character in movie
    m_role = re.search(r"\bwho\s+played\s+([a-zA-Z\s]+?)\s+in\s+([a-zA-Z0-9\s,.-]+?)(?:\s*\?|\s*$)", low)
    if m_role:
        return ("movie_connection", "role", f"{m_role.group(1).strip()} in {m_role.group(2).strip()}")

    # 5. Connection: Actor movies directed by Director
    m_collab = re.search(r"\b([a-zA-Z\s,.-]+?)\s+movies\s+directed\s+by\s+([a-zA-Z\s,.-]+?)(?:\s*\?|\s*$)", low)
    if m_collab:
        return ("movie_connection", "collaboration", f"{m_collab.group(1).strip().title()} and {m_collab.group(2).strip().title()}")

    # 6. Connection: Movies directed by Director
    m_dir_movies = re.search(r"\bmovies\s+directed\s+by\s+([a-zA-Z\s,.-]+?)(?:\s*\?|\s*$)", low)
    if m_dir_movies:
        return ("movie_connection", "director_movies", m_dir_movies.group(1).strip().title())

    # 7. Explicit Actor filmography patterns
    m_act_movies = re.search(r"\b([a-zA-Z\s,.-]+?)\s+(?:movies|films|filmography|movie list|all movies|hit movies|upcoming movies)\b", low)
    if m_act_movies:
        name = m_act_movies.group(1).strip()
        name = re.sub(r"^(all|the|best|latest|upcoming|top|new)\s+", "", name, flags=re.IGNORECASE).strip()
        if len(name) >= 2:
            return ("filmography", "actor", name.title())

    m_movies_of = re.search(r"\b(?:movies|films|filmography|all movies|list of movies)\s+(?:of|by|for)\s+([a-zA-Z\s,.-]+?)(?:\s*\?|\s*$)", low)
    if m_movies_of:
        name = m_movies_of.group(1).strip()
        name = re.sub(r"^(the|actor|actress|hero)\s+", "", name, flags=re.IGNORECASE).strip()
        if len(name) >= 2:
            return ("filmography", "actor", name.title())

    # 8. Known Actor names directly
    if norm in KNOWN_ACTORS or low in KNOWN_ACTORS:
        return ("filmography", "actor", cleaned.title())

    # 9. Explicit Movie Name patterns (e.g. 'RRR movie', 'Inception film', 'tell me about RRR')
    m_mov_explicit = re.search(r"\b([a-zA-Z0-9\s]+?)\s+(?:movie|film|cinema)\b", low)
    if m_mov_explicit:
        m_name = m_mov_explicit.group(1).strip()
        m_name = re.sub(r"^(the|this|that|about|tell me about)\s+", "", m_name, flags=re.IGNORECASE).strip()
        if len(m_name) >= 2 and m_name not in ("any", "a", "good", "new", "upcoming", "latest"):
            return ("movie", "movie", m_name.upper() if len(m_name) <= 4 else m_name.title())

    # 10. Known Movie names directly
    if norm in KNOWN_MOVIES or low in KNOWN_MOVIES:
        return ("movie", "movie", cleaned.upper() if len(cleaned) <= 4 else cleaned.title())

    return None

def build_cinema_search_query(category: str, q_type: str, target: str, raw_query: str) -> str:
    """Builds a high-precision keyword query for filmography and cinema searches."""
    if category == "filmography":
        return f"{target} actor filmography movies list release year roles character director wikipedia imdb"
    elif category == "movie":
        return f"{target} film movie release year director cast characters writers music genre plot synopsis wikipedia imdb"
    elif category == "movie_connection":
        if q_type == "director":
            return f"{target} film director who directed release year cast crew wikipedia imdb"
        elif q_type == "cast":
            return f"{target} film cast actors who acted in characters roles wikipedia imdb"
        elif q_type == "role":
            return f"{target} movie character actor who played role wikipedia imdb"
        elif q_type == "collaboration":
            return f"{target} movies directed by list release year wikipedia imdb"
        elif q_type == "director_movies":
            return f"movies directed by {target} director filmography list release year wikipedia imdb"
        return f"{raw_query} movie cast director wikipedia imdb"
    elif category == "verify_list":
        clean_q = re.sub(r"\b(is this list of|is this list|check this list|verify this list|movies correct|correct\?*|list of)\b", "", raw_query, flags=re.I).strip(" :?,.")
        return f"{clean_q} film cast characters roles wikipedia imdb"
    return f"{raw_query} film movie cast director wikipedia imdb"

def classify_query_intent(query: str, client_timezone: str = "Asia/Kolkata") -> GroundingDecision:
    """
    Decides whether a query requires:
    1. Real-time runtime clock (DATETIME_CLOCK)
    2. Live web search grounding (SEARCH_MANDATORY / SEARCH_VERIFICATION)
    3. Stable general knowledge (GENERAL_KNOWLEDGE)
    """
    cleaned = query.strip()
    q_low = cleaned.lower()

    # Step 1: Real-time clock queries (Handled strictly by date_time_service, NO web search)
    if is_datetime_query(cleaned):
        return GroundingDecision(
            intent="DATETIME_CLOCK",
            should_search=False,
            optimized_query=cleaned,
            category="clock",
            target_location=None,
            target_year="2026"
        )

    # Step 1.5: Cinema, Actor Filmography, and Movie Queries (Mandatory Search & Grounding)
    cinema_match = detect_cinema_query(cleaned)
    if cinema_match:
        c_cat, c_type, c_target = cinema_match
        opt_cinema_query = build_cinema_search_query(c_cat, c_type, c_target, cleaned)
        return GroundingDecision(
            intent="SEARCH_MANDATORY",
            should_search=True,
            optimized_query=opt_cinema_query,
            category=c_cat,
            target_location=None,
            target_year=None
        )

    # Step 2: Check stable general knowledge patterns (Coding, math, science definitions)
    # Only if there are no explicit fresh cues like 'latest', 'today', '2026'
    has_fresh_cue = bool(re.search(r"\b(latest|today|current|now|recent|2026|this year|version)\b", q_low))
    if not has_fresh_cue:
        for p in GENERAL_KNOWLEDGE_PATTERNS:
            if re.search(p, q_low):
                return GroundingDecision(
                    intent="GENERAL_KNOWLEDGE",
                    should_search=False,
                    optimized_query=cleaned,
                    category="general",
                    target_location=None,
                    target_year=None
                )

    # Step 3: Check Festival / Religious Calendar Queries
    festival = extract_festival_context(cleaned)
    year = extract_year_context(cleaned) or "2026"
    if festival:
        # Build high-precision search query targeting official Panchang & calendar
        opt_query = f"{festival} {year} date India Drik Panchang calendar tithi"
        return GroundingDecision(
            intent="SEARCH_MANDATORY",
            should_search=True,
            optimized_query=opt_query,
            category="festival",
            target_location="India",
            target_year=year
        )

    # Step 4: Check Mandatory Freshness patterns
    for p in MANDATORY_FRESHNESS_PATTERNS:
        if re.search(p, q_low):
            opt_query = build_optimized_search_query(cleaned, client_timezone)
            category = "current_events"
            if re.search(r"\b(weather|temperature|forecast)\b", q_low):
                category = "weather"
            elif re.search(r"\b(stock|share|crypto|bitcoin|price)\b", q_low):
                category = "finance"
            elif re.search(r"\b(score|match|winner|ipl|world cup)\b", q_low):
                category = "sports"
            elif re.search(r"\b(scheme|yojana|guidelines|rules|tax|budget)\b", q_low):
                category = "government"
            elif re.search(r"\b(version|release|update)\b", q_low):
                category = "software"

            return GroundingDecision(
                intent="SEARCH_MANDATORY",
                should_search=True,
                optimized_query=opt_query,
                category=category,
                target_location=extract_location_hint(cleaned),
                target_year=year
            )

    # Step 5: Check if query contains specific entity verification cues
    # E.g. "Who is the CEO of X", "Did X win Y", specific release dates
    if re.search(r"\b(who is|who won|when did|is it true that|release date of|born in|net worth of)\b", q_low):
        return GroundingDecision(
            intent="SEARCH_VERIFICATION",
            should_search=True,
            optimized_query=build_optimized_search_query(cleaned, client_timezone),
            category="verification",
            target_location=None,
            target_year=year
        )

    # Default: General Knowledge
    return GroundingDecision(
        intent="GENERAL_KNOWLEDGE",
        should_search=False,
        optimized_query=cleaned,
        category="general",
        target_location=None,
        target_year=None
    )

def extract_location_hint(query: str) -> Optional[str]:
    """Finds location hints like 'in Mumbai', 'in Bengaluru', 'in London'."""
    m = re.search(r"\bin\s+([a-zA-Z\s]{3,20})(?:\s+today|\s+now|\s*\?|$)", query, re.IGNORECASE)
    return m.group(1).strip() if m else None

def build_optimized_search_query(query: str, client_timezone: str = "Asia/Kolkata") -> str:
    """Transforms colloquial user prompt into a high-density keyword query for search engines."""
    cleaned = query.strip()

    # Strip conversational prefixes
    prefixes = [
        r"^(can you\s+)?(please\s+)?(search the web for|search for|look up|find online|browse for|google)\s+",
        r"^(can you\s+)?(please\s+)?(tell me|give me|what can you tell me about)\s+(about\s+|the\s+)?",
        r"^(what is|who is|where is|when is|how is)\s+(the\s+|an?\s+)?",
    ]
    for p in prefixes:
        cleaned = re.sub(p, "", cleaned, flags=re.IGNORECASE).strip()

    # Strip conversational suffixes
    suffixes = [
        r"\s+(please|tell me|right now|currently|as of now)$",
    ]
    for p in suffixes:
        cleaned = re.sub(p, "", cleaned, flags=re.IGNORECASE).strip()

    # Handle weather: append location if missing
    if re.search(r"\bweather\b", cleaned, re.IGNORECASE) and not re.search(r"\b(in|at|for)\s+[a-zA-Z]+", cleaned):
        loc = "India" if "kolkata" in client_timezone.lower() else "current location"
        cleaned = f"current weather forecast {loc}"

    return cleaned if len(cleaned) >= 3 else query.strip()

def score_source_authority(source: Dict[str, str], query: str) -> int:
    """
    Computes an authority score (0 to 100) for a retrieved web source.
    Favors official government, documentation, recognized news, and official panchang sites.
    """
    url = source.get("url", "").lower()
    title = source.get("title", "").lower()
    snippet = source.get("snippet", "").lower()

    score = 10  # Base score

    try:
        domain = urlparse(url).netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
    except Exception:
        domain = ""

    # Penalize low-quality / content farms
    for low in LOW_QUALITY_DOMAINS:
        if low in domain:
            return 0

    # Boost by domain authority match
    for auth_key, weight in AUTHORITATIVE_DOMAINS.items():
        if auth_key in domain:
            score += weight
            break

    # Relevance boosts
    q_words = [w.lower() for w in re.findall(r"\w{3,}", query) if w.lower() not in ("what", "when", "tell", "date", "with")]
    matches = sum(1 for w in q_words if w in title or w in snippet)
    score += min(matches * 8, 24)

    # HTTPS boost
    if url.startswith("https://"):
        score += 5

    # Penalize suspicious or thin snippets
    if len(snippet) < 30:
        score -= 15

    return max(score, 1)

def rank_and_deduplicate_sources(
    sources: List[Dict[str, str]],
    query: str,
    max_results: int = 5
) -> List[Dict[str, str]]:
    """Scores, re-ranks, and deduplicates sources so top authoritative references are selected."""
    scored = []
    seen_domains = set()

    for s in sources:
        url = s.get("url", "")
        if not url or not url.startswith("http"):
            continue

        try:
            domain = urlparse(url).netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:]
        except Exception:
            domain = url

        # Avoid 3+ results from the exact same domain
        domain_count = sum(1 for d in seen_domains if d == domain)
        if domain_count >= 2:
            continue

        score = score_source_authority(s, query)
        if score > 0:
            scored.append((score, s, domain))
            seen_domains.add(domain)

    # Sort descending by authority score
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored[:max_results]]
