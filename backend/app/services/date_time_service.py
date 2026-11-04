# ============================================================================
# LOKR AI - High-Precision Worldwide Real-Time Date & Time Service
# ============================================================================

import re
import time
import zoneinfo
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List, Tuple
import dateutil.parser
import unicodedata

# Common Timezone Abbreviations to Full Descriptive Names
TZ_ABBR_FULL_NAMES: Dict[str, str] = {
    "EDT": "Eastern Daylight Time",
    "EST": "Eastern Standard Time",
    "CDT": "Central Daylight Time",
    "CST": "Central Standard Time",
    "MDT": "Mountain Daylight Time",
    "MST": "Mountain Standard Time",
    "PDT": "Pacific Daylight Time",
    "PST": "Pacific Standard Time",
    "AKDT": "Alaska Daylight Time",
    "AKST": "Alaska Standard Time",
    "HST": "Hawaii Standard Time",
    "HDT": "Hawaii-Aleutian Daylight Time",
    "IST": "India Standard Time",
    "BST": "British Summer Time",
    "GMT": "Greenwich Mean Time",
    "UTC": "Coordinated Universal Time",
    "JST": "Japan Standard Time",
    "AEDT": "Australian Eastern Daylight Time",
    "AEST": "Australian Eastern Standard Time",
    "ACDT": "Australian Central Daylight Time",
    "ACST": "Australian Central Standard Time",
    "AWST": "Australian Western Standard Time",
    "CEST": "Central European Summer Time",
    "CET": "Central European Time",
    "EEST": "Eastern European Summer Time",
    "EET": "Eastern European Time",
    "WET": "Western European Time",
    "WEST": "Western European Summer Time",
    "GST": "Gulf Standard Time",
    "AST": "Arabia Standard Time",
    "SGT": "Singapore Standard Time",
    "HKT": "Hong Kong Time",
    "KST": "Korea Standard Time",
    "CST_CN": "China Standard Time",
    "NZDT": "New Zealand Daylight Time",
    "NZST": "New Zealand Standard Time",
    "BRT": "Brasília Time",
    "BRST": "Brasília Summer Time",
    "ART": "Argentina Time",
    "SAST": "South Africa Standard Time",
    "EAT": "East Africa Time",
    "WAT": "West Africa Time",
    "CAT": "Central Africa Time",
    "WIB": "Western Indonesia Time",
    "WITA": "Central Indonesia Time",
    "WIT": "Eastern Indonesia Time",
    "PKT": "Pakistan Standard Time",
    "BST_BD": "Bangladesh Standard Time",
    "NPT": "Nepal Time",
    "ICT": "Indochina Time",
    "PHT": "Philippine Standard Time",
    "MSK": "Moscow Standard Time",
    "IDT": "Israel Daylight Time",
}

# Multi-timezone countries with their major geographic zones
MULTI_TIMEZONE_COUNTRIES: Dict[str, List[Tuple[str, str]]] = {
    "usa": [
        ("Eastern (Washington, D.C. / New York)", "America/New_York"),
        ("Central (Chicago / Dallas)", "America/Chicago"),
        ("Mountain (Denver / Phoenix)", "America/Denver"),
        ("Pacific (Los Angeles / Seattle)", "America/Los_Angeles"),
        ("Alaska (Anchorage)", "America/Anchorage"),
        ("Hawaii (Honolulu)", "Pacific/Honolulu"),
    ],
    "united states": [
        ("Eastern (Washington, D.C. / New York)", "America/New_York"),
        ("Central (Chicago / Dallas)", "America/Chicago"),
        ("Mountain (Denver / Phoenix)", "America/Denver"),
        ("Pacific (Los Angeles / Seattle)", "America/Los_Angeles"),
        ("Alaska (Anchorage)", "America/Anchorage"),
        ("Hawaii (Honolulu)", "Pacific/Honolulu"),
    ],
    "america": [
        ("Eastern (Washington, D.C. / New York)", "America/New_York"),
        ("Central (Chicago / Dallas)", "America/Chicago"),
        ("Mountain (Denver / Phoenix)", "America/Denver"),
        ("Pacific (Los Angeles / Seattle)", "America/Los_Angeles"),
        ("Alaska (Anchorage)", "America/Anchorage"),
        ("Hawaii (Honolulu)", "Pacific/Honolulu"),
    ],
    "us": [
        ("Eastern (Washington, D.C. / New York)", "America/New_York"),
        ("Central (Chicago / Dallas)", "America/Chicago"),
        ("Mountain (Denver / Phoenix)", "America/Denver"),
        ("Pacific (Los Angeles / Seattle)", "America/Los_Angeles"),
        ("Alaska (Anchorage)", "America/Anchorage"),
        ("Hawaii (Honolulu)", "Pacific/Honolulu"),
    ],
    "australia": [
        ("Eastern (Sydney / Melbourne / Canberra)", "Australia/Sydney"),
        ("Queensland (Brisbane - No DST)", "Australia/Brisbane"),
        ("Central (Adelaide)", "Australia/Adelaide"),
        ("Northern Territory (Darwin - No DST)", "Australia/Darwin"),
        ("Western (Perth)", "Australia/Perth"),
    ],
    "canada": [
        ("Eastern (Toronto / Ottawa / Montreal)", "America/Toronto"),
        ("Central (Winnipeg)", "America/Winnipeg"),
        ("Mountain (Calgary / Edmonton)", "America/Edmonton"),
        ("Pacific (Vancouver)", "America/Vancouver"),
        ("Atlantic (Halifax)", "America/Halifax"),
        ("Newfoundland (St. John's)", "America/St_Johns"),
    ],
    "russia": [
        ("Moscow (MSK - Capital)", "Europe/Moscow"),
        ("Samara (SAMT)", "Europe/Samara"),
        ("Yekaterinburg (YEKT)", "Asia/Yekaterinburg"),
        ("Omsk (OMST)", "Asia/Omsk"),
        ("Krasnoyarsk (KRAT)", "Asia/Krasnoyarsk"),
        ("Irkutsk (IRKT)", "Asia/Irkutsk"),
        ("Vladivostok (VLAT)", "Asia/Vladivostok"),
    ],
    "brazil": [
        ("Brasília / São Paulo / Rio (BRT)", "America/Sao_Paulo"),
        ("Amazon / Manaus (AMT)", "America/Manaus"),
        ("Acre / Rio Branco (ACT)", "America/Rio_Branco"),
        ("Fernando de Noronha (FNT)", "America/Noronha"),
    ],
    "mexico": [
        ("Central (Mexico City / Guadalajara)", "America/Mexico_City"),
        ("Mountain (Chihuahua)", "America/Chihuahua"),
        ("Pacific (Tijuana)", "America/Tijuana"),
    ],
    "indonesia": [
        ("Western (Jakarta / Sumatra - WIB)", "Asia/Jakarta"),
        ("Central (Bali / Makassar - WITA)", "Asia/Makassar"),
        ("Eastern (Jayapura / Maluku - WIT)", "Asia/Jayapura"),
    ],
}

# Comprehensive worldwide location-to-IANA timezone map
WORLDWIDE_LOCATION_TIMEZONE_MAP: Dict[str, str] = {
    # --- India ---
    "india": "Asia/Kolkata",
    "bharat": "Asia/Kolkata",
    "ist": "Asia/Kolkata",
    "delhi": "Asia/Kolkata",
    "new delhi": "Asia/Kolkata",
    "mumbai": "Asia/Kolkata",
    "bombay": "Asia/Kolkata",
    "kolkata": "Asia/Kolkata",
    "calcutta": "Asia/Kolkata",
    "bengaluru": "Asia/Kolkata",
    "bangalore": "Asia/Kolkata",
    "chennai": "Asia/Kolkata",
    "madras": "Asia/Kolkata",
    "hyderabad": "Asia/Kolkata",
    "pune": "Asia/Kolkata",
    "ahmedabad": "Asia/Kolkata",
    "jaipur": "Asia/Kolkata",
    "surat": "Asia/Kolkata",
    "lucknow": "Asia/Kolkata",
    "kanpur": "Asia/Kolkata",
    "nagpur": "Asia/Kolkata",
    "indore": "Asia/Kolkata",
    "thane": "Asia/Kolkata",
    "bhopal": "Asia/Kolkata",
    "visakhapatnam": "Asia/Kolkata",
    "patna": "Asia/Kolkata",
    "vadodara": "Asia/Kolkata",
    "ghaziabad": "Asia/Kolkata",
    "ludhiana": "Asia/Kolkata",
    "agra": "Asia/Kolkata",
    "nashik": "Asia/Kolkata",
    "ranchi": "Asia/Kolkata",
    "coimbatore": "Asia/Kolkata",
    "raipur": "Asia/Kolkata",
    "chandigarh": "Asia/Kolkata",
    "gurgaon": "Asia/Kolkata",
    "gurugram": "Asia/Kolkata",
    "noida": "Asia/Kolkata",
    "kochi": "Asia/Kolkata",
    "cochin": "Asia/Kolkata",
    "thiruvananthapuram": "Asia/Kolkata",
    "trivandrum": "Asia/Kolkata",
    "kerala": "Asia/Kolkata",
    "goa": "Asia/Kolkata",
    "jammu": "Asia/Kolkata",
    "srinagar": "Asia/Kolkata",
    "kashmir": "Asia/Kolkata",
    "guwahati": "Asia/Kolkata",
    "assam": "Asia/Kolkata",
    "bhubaneswar": "Asia/Kolkata",
    "odisha": "Asia/Kolkata",
    "orissa": "Asia/Kolkata",
    "amritsar": "Asia/Kolkata",
    "punjab": "Asia/Kolkata",
    "varanasi": "Asia/Kolkata",
    "banaras": "Asia/Kolkata",

    # --- United States (Cities & States) ---
    "usa": "America/New_York",
    "united states": "America/New_York",
    "america": "America/New_York",
    "us": "America/New_York",
    "washington dc": "America/New_York",
    "washington d c": "America/New_York",
    "washington, dc": "America/New_York",
    "washington, d.c.": "America/New_York",
    "washington d.c.": "America/New_York",
    "dc": "America/New_York",
    "washington": "America/New_York",
    "new york": "America/New_York",
    "new york city": "America/New_York",
    "nyc": "America/New_York",
    "ny": "America/New_York",
    "boston": "America/New_York",
    "massachusetts": "America/New_York",
    "miami": "America/New_York",
    "florida": "America/New_York",
    "orlando": "America/New_York",
    "tampa": "America/New_York",
    "atlanta": "America/New_York",
    "georgia": "America/New_York",
    "philadelphia": "America/New_York",
    "pennsylvania": "America/New_York",
    "pittsburgh": "America/New_York",
    "baltimore": "America/New_York",
    "maryland": "America/New_York",
    "virginia": "America/New_York",
    "charlotte": "America/New_York",
    "north carolina": "America/New_York",
    "detroit": "America/Detroit",
    "michigan": "America/Detroit",
    "eastern time": "America/New_York",
    "est": "America/New_York",
    "edt": "America/New_York",

    "chicago": "America/Chicago",
    "illinois": "America/Chicago",
    "houston": "America/Chicago",
    "dallas": "America/Chicago",
    "dallas fort worth": "America/Chicago",
    "austin": "America/Chicago",
    "san antonio": "America/Chicago",
    "texas": "America/Chicago",
    "minneapolis": "America/Chicago",
    "minnesota": "America/Chicago",
    "saint paul": "America/Chicago",
    "milwaukee": "America/Chicago",
    "wisconsin": "America/Chicago",
    "st louis": "America/Chicago",
    "missouri": "America/Chicago",
    "kansas city": "America/Chicago",
    "new orleans": "America/Chicago",
    "louisiana": "America/Chicago",
    "nashville": "America/Chicago",
    "memphis": "America/Chicago",
    "tennessee": "America/Chicago",
    "central time": "America/Chicago",
    "cst": "America/Chicago",
    "cdt": "America/Chicago",

    "denver": "America/Denver",
    "colorado": "America/Denver",
    "phoenix": "America/Phoenix",
    "arizona": "America/Phoenix",
    "salt lake city": "America/Denver",
    "utah": "America/Denver",
    "albuquerque": "America/Denver",
    "new mexico": "America/Denver",
    "mountain time": "America/Denver",
    "mst": "America/Denver",
    "mdt": "America/Denver",

    "los angeles": "America/Los_Angeles",
    "la": "America/Los_Angeles",
    "san francisco": "America/Los_Angeles",
    "sf": "America/Los_Angeles",
    "san diego": "America/Los_Angeles",
    "san jose": "America/Los_Angeles",
    "sacramento": "America/Los_Angeles",
    "california": "America/Los_Angeles",
    "seattle": "America/Los_Angeles",
    "washington state": "America/Los_Angeles",
    "portland": "America/Los_Angeles",
    "oregon": "America/Los_Angeles",
    "las vegas": "America/Los_Angeles",
    "nevada": "America/Los_Angeles",
    "pacific time": "America/Los_Angeles",
    "pst": "America/Los_Angeles",
    "pdt": "America/Los_Angeles",

    "anchorage": "America/Anchorage",
    "alaska": "America/Anchorage",
    "honolulu": "Pacific/Honolulu",
    "hawaii": "Pacific/Honolulu",

    # --- Canada ---
    "toronto": "America/Toronto",
    "ontario": "America/Toronto",
    "ottawa": "America/Toronto",
    "montreal": "America/Toronto",
    "quebec": "America/Toronto",
    "vancouver": "America/Vancouver",
    "british columbia": "America/Vancouver",
    "bc": "America/Vancouver",
    "victoria": "America/Vancouver",
    "calgary": "America/Edmonton",
    "edmonton": "America/Edmonton",
    "alberta": "America/Edmonton",
    "winnipeg": "America/Winnipeg",
    "manitoba": "America/Winnipeg",
    "halifax": "America/Halifax",
    "nova scotia": "America/Halifax",
    "st johns": "America/St_Johns",
    "newfoundland": "America/St_Johns",

    # --- United Kingdom & Ireland ---
    "london": "Europe/London",
    "uk": "Europe/London",
    "united kingdom": "Europe/London",
    "england": "Europe/London",
    "great britain": "Europe/London",
    "britain": "Europe/London",
    "birmingham": "Europe/London",
    "manchester": "Europe/London",
    "leeds": "Europe/London",
    "liverpool": "Europe/London",
    "bristol": "Europe/London",
    "newcastle": "Europe/London",
    "sheffield": "Europe/London",
    "edinburgh": "Europe/London",
    "glasgow": "Europe/London",
    "scotland": "Europe/London",
    "cardiff": "Europe/London",
    "wales": "Europe/London",
    "belfast": "Europe/London",
    "northern ireland": "Europe/London",
    "dublin": "Europe/Dublin",
    "ireland": "Europe/Dublin",
    "cork": "Europe/Dublin",
    "gmt": "Europe/London",
    "bst": "Europe/London",

    # --- Western & Central Europe ---
    "paris": "Europe/Paris",
    "france": "Europe/Paris",
    "lyon": "Europe/Paris",
    "marseille": "Europe/Paris",
    "berlin": "Europe/Berlin",
    "germany": "Europe/Berlin",
    "munich": "Europe/Berlin",
    "frankfurt": "Europe/Berlin",
    "hamburg": "Europe/Berlin",
    "cologne": "Europe/Berlin",
    "rome": "Europe/Rome",
    "italy": "Europe/Rome",
    "milan": "Europe/Rome",
    "naples": "Europe/Rome",
    "turin": "Europe/Rome",
    "florence": "Europe/Rome",
    "venice": "Europe/Rome",
    "madrid": "Europe/Madrid",
    "spain": "Europe/Madrid",
    "barcelona": "Europe/Madrid",
    "valencia": "Europe/Madrid",
    "seville": "Europe/Madrid",
    "amsterdam": "Europe/Amsterdam",
    "netherlands": "Europe/Amsterdam",
    "holland": "Europe/Amsterdam",
    "rotterdam": "Europe/Amsterdam",
    "hague": "Europe/Amsterdam",
    "brussels": "Europe/Brussels",
    "belgium": "Europe/Brussels",
    "antwerp": "Europe/Brussels",
    "vienna": "Europe/Vienna",
    "austria": "Europe/Vienna",
    "salzburg": "Europe/Vienna",
    "zurich": "Europe/Zurich",
    "switzerland": "Europe/Zurich",
    "geneva": "Europe/Zurich",
    "bern": "Europe/Zurich",
    "stockholm": "Europe/Stockholm",
    "sweden": "Europe/Stockholm",
    "gothenburg": "Europe/Stockholm",
    "oslo": "Europe/Oslo",
    "norway": "Europe/Oslo",
    "bergen": "Europe/Oslo",
    "copenhagen": "Europe/Copenhagen",
    "denmark": "Europe/Copenhagen",
    "helsinki": "Europe/Helsinki",
    "finland": "Europe/Helsinki",
    "warsaw": "Europe/Warsaw",
    "poland": "Europe/Warsaw",
    "krakow": "Europe/Warsaw",
    "prague": "Europe/Prague",
    "czech republic": "Europe/Prague",
    "czechia": "Europe/Prague",
    "budapest": "Europe/Budapest",
    "hungary": "Europe/Budapest",
    "bucharest": "Europe/Bucharest",
    "romania": "Europe/Bucharest",
    "athens": "Europe/Athens",
    "greece": "Europe/Athens",
    "lisbon": "Europe/Lisbon",
    "portugal": "Europe/Lisbon",
    "porto": "Europe/Lisbon",
    "istanbul": "Europe/Istanbul",
    "turkey": "Europe/Istanbul",
    "turkiye": "Europe/Istanbul",
    "ankara": "Europe/Istanbul",
    "kyiv": "Europe/Kyiv",
    "kiev": "Europe/Kyiv",
    "ukraine": "Europe/Kyiv",
    "moscow": "Europe/Moscow",
    "russia": "Europe/Moscow",
    "saint petersburg": "Europe/Moscow",
    "st petersburg": "Europe/Moscow",
    "belgrade": "Europe/Belgrade",
    "serbia": "Europe/Belgrade",
    "zagreb": "Europe/Zagreb",
    "croatia": "Europe/Zagreb",
    "sofia": "Europe/Sofia",
    "bulgaria": "Europe/Sofia",
    "bratislava": "Europe/Bratislava",
    "slovakia": "Europe/Bratislava",
    "ljubljana": "Europe/Ljubljana",
    "slovenia": "Europe/Ljubljana",
    "reykjavik": "Atlantic/Reykjavik",
    "iceland": "Atlantic/Reykjavik",

    # --- Middle East ---
    "dubai": "Asia/Dubai",
    "uae": "Asia/Dubai",
    "united arab emirates": "Asia/Dubai",
    "abu dhabi": "Asia/Dubai",
    "sharjah": "Asia/Dubai",
    "riyadh": "Asia/Riyadh",
    "saudi arabia": "Asia/Riyadh",
    "saudi": "Asia/Riyadh",
    "jeddah": "Asia/Riyadh",
    "mecca": "Asia/Riyadh",
    "makkah": "Asia/Riyadh",
    "medina": "Asia/Riyadh",
    "doha": "Asia/Qatar",
    "qatar": "Asia/Qatar",
    "kuwait": "Asia/Kuwait",
    "kuwait city": "Asia/Kuwait",
    "muscat": "Asia/Muscat",
    "oman": "Asia/Muscat",
    "manama": "Asia/Bahrain",
    "bahrain": "Asia/Bahrain",
    "cairo": "Africa/Cairo",
    "egypt": "Africa/Cairo",
    "alexandria": "Africa/Cairo",
    "tel aviv": "Asia/Jerusalem",
    "jerusalem": "Asia/Jerusalem",
    "israel": "Asia/Jerusalem",
    "amman": "Asia/Amman",
    "jordan": "Asia/Amman",
    "beirut": "Asia/Beirut",
    "lebanon": "Asia/Beirut",
    "baghdad": "Asia/Baghdad",
    "iraq": "Asia/Baghdad",
    "tehran": "Asia/Tehran",
    "iran": "Asia/Tehran",

    # --- East & Southeast Asia ---
    "tokyo": "Asia/Tokyo",
    "japan": "Asia/Tokyo",
    "osaka": "Asia/Tokyo",
    "kyoto": "Asia/Tokyo",
    "yokohama": "Asia/Tokyo",
    "nagoya": "Asia/Tokyo",
    "sapporo": "Asia/Tokyo",
    "jst": "Asia/Tokyo",
    "seoul": "Asia/Seoul",
    "south korea": "Asia/Seoul",
    "korea": "Asia/Seoul",
    "busan": "Asia/Seoul",
    "beijing": "Asia/Shanghai",
    "china": "Asia/Shanghai",
    "shanghai": "Asia/Shanghai",
    "guangzhou": "Asia/Shanghai",
    "shenzhen": "Asia/Shanghai",
    "chengdu": "Asia/Shanghai",
    "hong kong": "Asia/Hong_Kong",
    "hk": "Asia/Hong_Kong",
    "taipei": "Asia/Taipei",
    "taiwan": "Asia/Taipei",
    "singapore": "Asia/Singapore",
    "sg": "Asia/Singapore",
    "bangkok": "Asia/Bangkok",
    "thailand": "Asia/Bangkok",
    "phuket": "Asia/Bangkok",
    "chiang mai": "Asia/Bangkok",
    "kuala lumpur": "Asia/Kuala_Lumpur",
    "malaysia": "Asia/Kuala_Lumpur",
    "penang": "Asia/Kuala_Lumpur",
    "jakarta": "Asia/Jakarta",
    "indonesia": "Asia/Jakarta",
    "bali": "Asia/Makassar",
    "denpasar": "Asia/Makassar",
    "manila": "Asia/Manila",
    "philippines": "Asia/Manila",
    "cebu": "Asia/Manila",
    "hanoi": "Asia/Ho_Chi_Minh",
    "vietnam": "Asia/Ho_Chi_Minh",
    "ho chi minh": "Asia/Ho_Chi_Minh",
    "ho chi minh city": "Asia/Ho_Chi_Minh",
    "saigon": "Asia/Ho_Chi_Minh",
    "phnom penh": "Asia/Phnom_Penh",
    "cambodia": "Asia/Phnom_Penh",
    "vientiane": "Asia/Vientiane",
    "laos": "Asia/Vientiane",
    "yangon": "Asia/Yangon",
    "myanmar": "Asia/Yangon",
    "burma": "Asia/Yangon",

    # --- South Asia ---
    "karachi": "Asia/Karachi",
    "pakistan": "Asia/Karachi",
    "lahore": "Asia/Karachi",
    "islamabad": "Asia/Karachi",
    "dhaka": "Asia/Dhaka",
    "bangladesh": "Asia/Dhaka",
    "colombo": "Asia/Colombo",
    "sri lanka": "Asia/Colombo",
    "kathmandu": "Asia/Kathmandu",
    "nepal": "Asia/Kathmandu",
    "thimphu": "Asia/Thimphu",
    "bhutan": "Asia/Thimphu",
    "male": "Indian/Maldives",
    "maldives": "Indian/Maldives",

    # --- Australia & Oceania ---
    "sydney": "Australia/Sydney",
    "australia": "Australia/Sydney",
    "melbourne": "Australia/Melbourne",
    "canberra": "Australia/Sydney",
    "brisbane": "Australia/Brisbane",
    "queensland": "Australia/Brisbane",
    "perth": "Australia/Perth",
    "western australia": "Australia/Perth",
    "adelaide": "Australia/Adelaide",
    "south australia": "Australia/Adelaide",
    "darwin": "Australia/Darwin",
    "hobart": "Australia/Hobart",
    "tasmania": "Australia/Hobart",
    "gold coast": "Australia/Brisbane",
    "auckland": "Pacific/Auckland",
    "new zealand": "Pacific/Auckland",
    "nz": "Pacific/Auckland",
    "wellington": "Pacific/Auckland",
    "christchurch": "Pacific/Auckland",
    "fiji": "Pacific/Fiji",
    "suva": "Pacific/Fiji",
    "port moresby": "Pacific/Port_Moresby",
    "papua new guinea": "Pacific/Port_Moresby",

    # --- Latin America & Caribbean ---
    "mexico city": "America/Mexico_City",
    "mexico": "America/Mexico_City",
    "guadalajara": "America/Mexico_City",
    "monterrey": "America/Monterrey",
    "tijuana": "America/Tijuana",
    "cancun": "America/Cancun",
    "sao paulo": "America/Sao_Paulo",
    "brazil": "America/Sao_Paulo",
    "rio de janeiro": "America/Sao_Paulo",
    "rio": "America/Sao_Paulo",
    "brasilia": "America/Sao_Paulo",
    "buenos aires": "America/Argentina/Buenos_Aires",
    "argentina": "America/Argentina/Buenos_Aires",
    "santiago": "America/Santiago",
    "chile": "America/Santiago",
    "bogota": "America/Bogota",
    "colombia": "America/Bogota",
    "medellin": "America/Bogota",
    "lima": "America/Lima",
    "peru": "America/Lima",
    "caracas": "America/Caracas",
    "venezuela": "America/Caracas",
    "quito": "America/Guayaquil",
    "ecuador": "America/Guayaquil",
    "montevideo": "America/Montevideo",
    "uruguay": "America/Montevideo",
    "asuncion": "America/Asuncion",
    "paraguay": "America/Asuncion",
    "la paz": "America/La_Paz",
    "bolivia": "America/La_Paz",
    "panama": "America/Panama",
    "panama city": "America/Panama",
    "san jose": "America/Costa_Rica",
    "costa rica": "America/Costa_Rica",
    "havana": "America/Havana",
    "cuba": "America/Havana",
    "san juan": "America/Puerto_Rico",
    "puerto rico": "America/Puerto_Rico",
    "kingston": "America/Jamaica",
    "jamaica": "America/Jamaica",

    # --- Africa ---
    "johannesburg": "Africa/Johannesburg",
    "south africa": "Africa/Johannesburg",
    "cape town": "Africa/Johannesburg",
    "durban": "Africa/Johannesburg",
    "pretoria": "Africa/Johannesburg",
    "nairobi": "Africa/Nairobi",
    "kenya": "Africa/Nairobi",
    "mombasa": "Africa/Nairobi",
    "lagos": "Africa/Lagos",
    "nigeria": "Africa/Lagos",
    "abuja": "Africa/Lagos",
    "casablanca": "Africa/Casablanca",
    "morocco": "Africa/Casablanca",
    "rabat": "Africa/Casablanca",
    "accra": "Africa/Accra",
    "ghana": "Africa/Accra",
    "addis ababa": "Africa/Addis_Ababa",
    "ethiopia": "Africa/Addis_Ababa",
    "algiers": "Africa/Algiers",
    "algeria": "Africa/Algiers",
    "tunis": "Africa/Tunis",
    "tunisia": "Africa/Tunis",
    "dakar": "Africa/Dakar",
    "senegal": "Africa/Dakar",
    "luanda": "Africa/Luanda",
    "angola": "Africa/Luanda",
    "kinshasa": "Africa/Kinshasa",
    "congo": "Africa/Kinshasa",
    "dar es salaam": "Africa/Dar_es_Salaam",
    "tanzania": "Africa/Dar_es_Salaam",
    "kampala": "Africa/Kampala",
    "uganda": "Africa/Kampala",
    "kigali": "Africa/Kigali",
    "rwanda": "Africa/Kigali",
}

# Regex patterns to detect when a prompt is asking about date or time
DATETIME_QUERY_PATTERNS = [
    r"\bwhat\s+(?:is\s+)?(?:the\s+)?time(?:\s+is\s+it)?(?:\s+now)?\b",
    r"\bcurrent\s+time\b",
    r"\btime\s+now\b",
    r"\bwhat\s+time\b",
    r"\btell\s+me\s+the\s+time\b",
    r"\bwhat\s+(?:is\s+)?today'?s\s+date\b",
    r"\bwhat\s+date\s+is\s+today\b",
    r"\bwhat\s+day\s+is\s+(?:it\s+)?today\b",
    r"\btoday'?s\s+date\b",
    r"\bcurrent\s+date\b",
    r"\bdate\s+today\b",
    r"\bcurrent\s+date\s+and\s+time\b",
    r"\bdate\s+and\s+time\s+now\b",
    r"\btime\s+in\s+([a-zA-Z\s,.-]+)\b",
    r"\bwhat\s+time\s+is\s+it\s+in\s+([a-zA-Z\s,.-]+)\b",
    r"\bwhat\s+is\s+the\s+time\s+in\s+([a-zA-Z\s,.-]+)\b",
    r"\btime\s+difference\b",
    r"\bdifference\s+in\s+time\b",
    r"\bhow\s+many\s+hours\s+(?:difference|ahead|behind)\b",
    r"\bwhat\s+will\s+tomorrow'?s\s+date\s+be\b",
    r"\bwhat\s+is\s+tomorrow'?s\s+date\b",
    r"\btomorrow'?s\s+date\b",
    r"\byesterday'?s\s+date\b",
    r"\bwhat\s+was\s+yesterday'?s\s+date\b",
    r"\bwhat\s+day\s+is\s+next\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
    r"\bwhat\s+date\s+is\s+next\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
    r"\bwhat\s+day\s+was\s+last\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
    r"\bwhat\s+date\s+was\s+last\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
    r"\bhow\s+many\s+days\s+(?:until|remaining|left)\b",
    r"\bdays\s+between\b",
    r"\bday\s+of\s+the\s+week\s+for\b",
    r"\bwhat\s+day\s+of\s+the\s+week\s+(?:was|is|will\s+be)\b",
    r"\bwhat\s+time\s+is\s+it\s+in\s+my\s+country\b",
    r"\btime\s+in\s+my\s+country\b",
]

def is_datetime_query(query: str) -> bool:
    """Returns True if user is querying current date, time, timezone, or calendar calculations."""
    q = query.strip().lower()
    for pattern in DATETIME_QUERY_PATTERNS:
        if re.search(pattern, q):
            return True
    return False

def format_utc_offset(offset_str: str) -> str:
    """Formats raw '%z' offset (e.g. '-0400', '+0530') into clean 'UTC-4', 'UTC+5:30', or 'UTC'."""
    if not offset_str:
        return "UTC"
    sign = "UTC-" if offset_str.startswith("-") else "UTC+"
    hours = int(offset_str[1:3])
    mins = int(offset_str[3:5])
    if mins == 0:
        return f"{sign}{hours}"
    return f"{sign}{hours}:{mins:02d}"

def get_descriptive_timezone_name(tz_abbr: str, tz_key: str) -> str:
    """Returns the full human-readable timezone name (e.g. 'Eastern Daylight Time (EDT)')."""
    if tz_abbr in TZ_ABBR_FULL_NAMES:
        return f"{TZ_ABBR_FULL_NAMES[tz_abbr]} ({tz_abbr})"
    clean_city = tz_key.split("/")[-1].replace("_", " ")
    return f"{clean_city} Time ({tz_abbr})"

def normalize_location_name(text: str) -> str:
    """Normalizes accents, diacritics, and punctuation (e.g. 'São Paulo' -> 'sao paulo')."""
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_str = nfkd.encode("ASCII", "ignore").decode("utf-8")
    cleaned = re.sub(r"[^\w\s]", "", ascii_str.lower()).strip()
    return re.sub(r"\s+", " ", cleaned)

def resolve_timezone(tz_name_or_location: Optional[str]) -> zoneinfo.ZoneInfo:
    """
    Safely resolves any city name, country name, US state, or IANA key to a valid ZoneInfo instance.
    Defaults to 'Asia/Kolkata' if unrecognized.
    """
    default_tz = "Asia/Kolkata"
    if not tz_name_or_location or not tz_name_or_location.strip():
        return zoneinfo.ZoneInfo(default_tz)

    raw = tz_name_or_location.strip().lower()
    cleaned = normalize_location_name(raw)

    # 1. Exact match in dictionary
    if raw in WORLDWIDE_LOCATION_TIMEZONE_MAP:
        try:
            return zoneinfo.ZoneInfo(WORLDWIDE_LOCATION_TIMEZONE_MAP[raw])
        except Exception:
            pass

    if cleaned in WORLDWIDE_LOCATION_TIMEZONE_MAP:
        try:
            return zoneinfo.ZoneInfo(WORLDWIDE_LOCATION_TIMEZONE_MAP[cleaned])
        except Exception:
            pass

    # 2. Try raw string as direct IANA key
    try:
        return zoneinfo.ZoneInfo(tz_name_or_location.strip())
    except Exception:
        pass

    # 3. Try matching against available IANA timezones by suffix or exact match
    search_key = cleaned.replace(" ", "_")
    for tz_key in zoneinfo.available_timezones():
        key_low = tz_key.lower()
        if key_low.endswith(f"/{search_key}") or key_low == search_key:
            try:
                return zoneinfo.ZoneInfo(tz_key)
            except Exception:
                pass

    return zoneinfo.ZoneInfo(default_tz)

def is_multi_timezone_country(location: str) -> bool:
    """Returns True if the location is a nation with multiple official time zones."""
    clean = re.sub(r"[^\w\s]", "", location.lower()).strip()
    return clean in MULTI_TIMEZONE_COUNTRIES

def get_country_multizone_snapshot(country_name: str) -> List[Dict[str, Any]]:
    """Returns a list of live temporal snapshots for each major timezone in a multi-timezone country."""
    clean = re.sub(r"[^\w\s]", "", country_name.lower()).strip()
    zones = MULTI_TIMEZONE_COUNTRIES.get(clean, [])
    results = []
    for label, tz_key in zones:
        try:
            tz = zoneinfo.ZoneInfo(tz_key)
            now = datetime.now(tz)
            abbr = now.strftime("%Z")
            offset = format_utc_offset(now.strftime("%z"))
            results.append({
                "label": label,
                "timezone_key": tz_key,
                "time_12h": now.strftime("%I:%M %p").lstrip("0"),
                "date": now.strftime("%A, %B %d, %Y"),
                "day": now.strftime("%A"),
                "tz_abbr": abbr,
                "tz_full": get_descriptive_timezone_name(abbr, tz_key),
                "utc_offset": offset
            })
        except Exception:
            pass
    return results

def is_time_difference_query(query: str) -> bool:
    """Detects if query is asking for the time difference between two locations."""
    q = query.lower()
    return bool(
        re.search(r"\btime\s+difference\b", q) or
        re.search(r"\bdifference\s+in\s+time\b", q) or
        re.search(r"\bhow\s+many\s+hours\b.*?\b(ahead|behind|difference|apart)\b", q) or
        re.search(r"\b(ahead\s+of|behind)\b.*?\b(time|hours)\b", q)
    )

def extract_time_difference_locations(query: str) -> Optional[Tuple[str, str]]:
    """Extracts the two target locations from a time difference question."""
    patterns = [
        r"\b(?:between|of)\s+([a-zA-Z\s,.-]+?)\s+(?:and|vs|to)\s+([a-zA-Z\s,.-]+?)(?:\s*\?|\s*$)",
        r"\bhow\s+many\s+hours\s+(?:is|ahead|behind)?\s*([a-zA-Z\s,.-]+?)\s+(?:ahead\s+of|behind|from|compared\s+to)\s+([a-zA-Z\s,.-]+?)(?:\s*\?|\s*$)",
    ]
    for p in patterns:
        m = re.search(p, query, re.IGNORECASE)
        if m:
            loc1 = m.group(1).strip()
            loc2 = m.group(2).strip()
            for w in ['right now', 'today', 'please', 'now', 'currently', 'the']:
                loc1 = re.sub(rf"\b{w}\b", "", loc1, flags=re.IGNORECASE).strip()
                loc2 = re.sub(rf"\b{w}\b", "", loc2, flags=re.IGNORECASE).strip()
            loc1 = re.sub(r"[\s.,;:?!]+$", "", loc1).strip()
            loc2 = re.sub(r"[\s.,;:?!]+$", "", loc2).strip()
            if loc1 and loc2 and len(loc1) >= 2 and len(loc2) >= 2:
                return (loc1, loc2)
    return None

def calculate_time_difference(loc1_name: str, loc2_name: str) -> Dict[str, Any]:
    """
    Computes exact, millisecond-accurate time difference between two global locations
    taking into account live daylight saving time (DST).
    """
    tz1 = resolve_timezone(loc1_name)
    tz2 = resolve_timezone(loc2_name)
    now1 = datetime.now(tz1)
    now2 = datetime.now(tz2)

    offset1_sec = now1.utcoffset().total_seconds()
    offset2_sec = now2.utcoffset().total_seconds()
    diff_sec = offset1_sec - offset2_sec

    diff_hours = int(abs(diff_sec) // 3600)
    diff_mins = int((abs(diff_sec) % 3600) // 60)

    if diff_mins > 0:
        time_diff_text = f"{diff_hours} hours and {diff_mins} minutes"
    elif diff_hours == 1:
        time_diff_text = "1 hour"
    else:
        time_diff_text = f"{diff_hours} hours"

    name1_display = "Washington, D.C." if loc1_name.lower() in ("washington dc", "washington d c", "washington, d.c.") else loc1_name.title()
    name2_display = "Washington, D.C." if loc2_name.lower() in ("washington dc", "washington d c", "washington, d.c.") else loc2_name.title()

    if diff_sec > 0:
        relation_text = f"{name1_display} is **{time_diff_text} ahead** of {name2_display}."
    elif diff_sec < 0:
        relation_text = f"{name1_display} is **{time_diff_text} behind** {name2_display}."
    else:
        relation_text = f"{name1_display} and {name2_display} are in the **same time zone**."

    # Multi-zone country breakdown if either location is a nation with multiple timezones
    multi_zone_note = ""
    target_multi = None
    if is_multi_timezone_country(loc2_name):
        target_multi = loc2_name
    elif is_multi_timezone_country(loc1_name):
        target_multi = loc1_name

    if target_multi and target_multi.lower() in ("usa", "america", "united states", "us"):
        multi_zone_note = (
            f"\n*Note*: The United States spans multiple time zones. With reference to {name1_display}:\n"
            f"- Eastern Time (Washington, D.C. / New York): {relation_text}\n"
            f"- Central Time (Chicago / Dallas): {diff_hours + (1 if diff_sec > 0 else -1)} hours {diff_mins} mins difference\n"
            f"- Mountain Time (Denver / Phoenix): {diff_hours + (2 if diff_sec > 0 else -2)} hours {diff_mins} mins difference\n"
            f"- Pacific Time (Los Angeles / Seattle): {diff_hours + (3 if diff_sec > 0 else -3)} hours {diff_mins} mins difference\n"
        )

    return {
        "loc1": name1_display,
        "loc2": name2_display,
        "tz1_key": tz1.key,
        "tz2_key": tz2.key,
        "time1": now1.strftime("%I:%M %p").lstrip("0"),
        "date1": now1.strftime("%A, %B %d, %Y"),
        "tz1_abbr": now1.strftime("%Z"),
        "offset1": format_utc_offset(now1.strftime("%z")),
        "time2": now2.strftime("%I:%M %p").lstrip("0"),
        "date2": now2.strftime("%A, %B %d, %Y"),
        "tz2_abbr": now2.strftime("%Z"),
        "offset2": format_utc_offset(now2.strftime("%z")),
        "diff_hours": diff_hours,
        "diff_mins": diff_mins,
        "time_diff_text": time_diff_text,
        "relation_text": relation_text,
        "multi_zone_note": multi_zone_note,
    }

def extract_all_target_locations(query: str) -> List[str]:
    """
    Extracts all requested cities/countries from a prompt.
    E.g. 'What time is it in India, USA, UK and Japan?' -> ['India', 'USA', 'UK', 'Japan']
    """
    pattern = r"\b(?:time\s+in|what\s+time\s+is\s+it\s+in|current\s+time\s+in)\s+([a-zA-Z\s,.-]+?)(?:\s*\?|\s*$|\s+now|\s+currently|\s+today)"
    m = re.search(pattern, query, re.IGNORECASE)
    if not m:
        pattern2 = r"\bin\s+([a-zA-Z\s,.-]+?)(?:\s*\?|\s*$)"
        m = re.search(pattern2, query, re.IGNORECASE)

    if not m:
        return []

    raw = m.group(1).strip()
    # Protect 'Washington, D.C.' and 'Washington DC' from comma splitting
    raw = re.sub(r"\bwashington,\s*d\.?c\.?\b", "___WASH_DC___", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\bwashington\s+d\.?c\.?\b", "___WASH_DC___", raw, flags=re.IGNORECASE)

    tokens = re.split(r",|\band\b|&", raw, flags=re.IGNORECASE)
    results = []
    seen = set()
    for tok in tokens:
        clean = tok.strip()
        if "___WASH_DC___" in clean:
            clean = "Washington, D.C."
        else:
            clean = re.sub(r"^the\s+", "", clean, flags=re.IGNORECASE).strip()
            clean = re.sub(r"[\s.,;:?!]+$", "", clean).strip()

        if len(clean) >= 2 and clean.lower() not in ("my country", "world", "city", "now", "today", "here"):
            if clean.lower() not in seen:
                seen.add(clean.lower())
                results.append(clean)
    return results

def extract_target_location(query: str) -> Optional[str]:
    """Extracts single target city or country from queries like 'time in London'."""
    locs = extract_all_target_locations(query)
    return locs[0] if locs else None

def calculate_next_weekday(current_dt: datetime, target_weekday_name: str) -> datetime:
    """Calculates the datetime of the upcoming specified weekday (0=Monday, 6=Sunday)."""
    weekdays = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6
    }
    target_num = weekdays.get(target_weekday_name.lower().strip(), 0)
    current_num = current_dt.weekday()
    days_ahead = target_num - current_num
    if days_ahead <= 0:
        days_ahead += 7
    return current_dt + timedelta(days=days_ahead)

def calculate_last_weekday(current_dt: datetime, target_weekday_name: str) -> datetime:
    """Calculates the datetime of the most recent past specified weekday."""
    weekdays = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6
    }
    target_num = weekdays.get(target_weekday_name.lower().strip(), 0)
    current_num = current_dt.weekday()
    days_behind = current_num - target_num
    if days_behind <= 0:
        days_behind += 7
    return current_dt - timedelta(days=days_behind)

def get_live_time_snapshot(user_timezone: str = "Asia/Kolkata") -> Dict[str, Any]:
    """
    Generates a live, millisecond-accurate temporal snapshot at the moment of invocation.
    Includes UTC, local user time, relative dates, and major global clocks.
    """
    tz = resolve_timezone(user_timezone)
    now_utc = datetime.now(timezone.utc)
    now_local = datetime.now(tz)

    yesterday = now_local - timedelta(days=1)
    tomorrow = now_local + timedelta(days=1)
    day_after = now_local + timedelta(days=2)

    time_12h = now_local.strftime("%I:%M:%S %p").lstrip("0")
    time_12h_short = now_local.strftime("%I:%M %p").lstrip("0")
    date_str = now_local.strftime("%A, %B %d, %Y")
    day_name = now_local.strftime("%A")
    tz_abbr = now_local.strftime("%Z")
    formatted_offset = format_utc_offset(now_local.strftime("%z"))
    full_tz_name = get_descriptive_timezone_name(tz_abbr, tz.key)

    relative_dates = {
        "yesterday": yesterday.strftime("%A, %B %d, %Y"),
        "today": date_str,
        "tomorrow": tomorrow.strftime("%A, %B %d, %Y"),
        "day_after_tomorrow": day_after.strftime("%A, %B %d, %Y"),
        "next_monday": calculate_next_weekday(now_local, "monday").strftime("%A, %B %d, %Y"),
        "next_tuesday": calculate_next_weekday(now_local, "tuesday").strftime("%A, %B %d, %Y"),
        "next_wednesday": calculate_next_weekday(now_local, "wednesday").strftime("%A, %B %d, %Y"),
        "next_thursday": calculate_next_weekday(now_local, "thursday").strftime("%A, %B %d, %Y"),
        "next_friday": calculate_next_weekday(now_local, "friday").strftime("%A, %B %d, %Y"),
        "next_saturday": calculate_next_weekday(now_local, "saturday").strftime("%A, %B %d, %Y"),
        "next_sunday": calculate_next_weekday(now_local, "sunday").strftime("%A, %B %d, %Y"),
        "last_friday": calculate_last_weekday(now_local, "friday").strftime("%A, %B %d, %Y"),
        "last_monday": calculate_last_weekday(now_local, "monday").strftime("%A, %B %d, %Y"),
    }

    world_cities = [
        ("India (IST)", "Asia/Kolkata"),
        ("Washington, D.C. / New York (EDT/EST)", "America/New_York"),
        ("London (BST/GMT)", "Europe/London"),
        ("Tokyo (JST)", "Asia/Tokyo"),
        ("Dubai (GST)", "Asia/Dubai"),
        ("Singapore (SGT)", "Asia/Singapore"),
        ("Paris (CEST/CET)", "Europe/Paris"),
        ("Sydney (AEDT/AEST)", "Australia/Sydney"),
        ("Los Angeles (PDT/PST)", "America/Los_Angeles"),
    ]

    world_clocks = {}
    for city_label, city_tz in world_cities:
        city_now = datetime.now(zoneinfo.ZoneInfo(city_tz))
        c_time = city_now.strftime("%I:%M %p").lstrip("0")
        c_date = city_now.strftime("%A, %b %d, %Y")
        c_abbr = city_now.strftime("%Z")
        c_offset = format_utc_offset(city_now.strftime("%z"))
        world_clocks[city_label] = f"{c_time} {c_abbr} ({c_offset}) - {c_date}"

    return {
        "timestamp": time.time(),
        "utc_iso": now_utc.isoformat(),
        "timezone_name": str(tz.key),
        "timezone_abbr": tz_abbr,
        "timezone_full": full_tz_name,
        "timezone_offset": formatted_offset,
        "date_full": date_str,
        "day_of_week": day_name,
        "time_12h": time_12h,
        "time_12h_short": time_12h_short,
        "time_24h": now_local.strftime("%H:%M:%S"),
        "relative_dates": relative_dates,
        "world_clocks": world_clocks,
    }

def build_temporal_context(
    user_query: str,
    client_timezone: Optional[str] = "Asia/Kolkata"
) -> str:
    """
    Builds an authoritative real-time context string injected into the model's system prompt.
    Contains dynamically evaluated temporal truths evaluated at the exact millisecond of request execution.
    """
    effective_tz = client_timezone or "Asia/Kolkata"
    snapshot = get_live_time_snapshot(effective_tz)

    # Check if query is temporal or date/time related. If not, return compact clock header to save tokens.
    is_temporal = bool(
        is_time_difference_query(user_query) or
        re.search(r"\b(time|date|day|today|tomorrow|yesterday|now|clock|o'clock|timezone|gmt|utc|dst|diff|difference|calendar|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", user_query, re.IGNORECASE) or
        (len(extract_all_target_locations(user_query)) > 0 and re.search(r"\b(in|at|for|current|what|tell|time)\b", user_query, re.IGNORECASE))
    )

    if not is_temporal:
        return (
            f"=== REAL-TIME SERVER CLOCK ===\n"
            f"- Today's Date: {snapshot['date_full']}\n"
            f"- Current Time: {snapshot['time_12h_short']} ({snapshot['timezone_abbr']}, {snapshot['timezone_offset']})\n"
            f"- Day of the Week: {snapshot['day_of_week']}\n"
            f"- User Timezone: {snapshot['timezone_name']}\n"
            f"=== END SERVER CLOCK ==="
        )

    sections: List[str] = []

    # 1. TIME DIFFERENCE HANDLING
    if is_time_difference_query(user_query):
        pair = extract_time_difference_locations(user_query)
        if pair:
            loc1, loc2 = pair
            diff_data = calculate_time_difference(loc1, loc2)
            diff_block = (
                f"\n=== VERIFIED REAL-TIME TIME DIFFERENCE CALCULATION ===\n"
                f"- **Result**: {diff_data['relation_text']}\n"
                f"- **{diff_data['loc1']}**: {diff_data['time1']} ({diff_data['tz1_abbr']}, {diff_data['offset1']}) - {diff_data['date1']}\n"
                f"- **{diff_data['loc2']}**: {diff_data['time2']} ({diff_data['tz2_abbr']}, {diff_data['offset2']}) - {diff_data['date2']}\n"
                f"{diff_data['multi_zone_note']}\n"
                f"INSTRUCTION: Explain this exact calculation clearly to the user, highlighting which location is ahead or behind, and state both current local times and dates.\n"
                f"=== END TIME DIFFERENCE CALCULATION ===\n"
            )
            sections.append(diff_block)

    # 2. MULTI-LOCATION OR MULTI-TIMEZONE HANDLING
    all_locs = extract_all_target_locations(user_query)

    # A) Multi-location comparison table (e.g. 'What time is it in India, USA, UK and Japan?')
    if len(all_locs) >= 2:
        table_rows = []
        table_rows.append("| Location | Local Date | Local Time | Timezone |")
        table_rows.append("|---|---|---|---|")
        for loc in all_locs:
            clean_l = loc.lower()
            # If in multi-location table and country is USA, represent with Capital Washington, D.C. as requested
            if clean_l in ("usa", "america", "united states", "us"):
                tz = zoneinfo.ZoneInfo("America/New_York")
                dt = datetime.now(tz)
                t_str = dt.strftime("%I:%M %p").lstrip("0")
                d_str = dt.strftime("%A, %B %d, %Y")
                abbr = dt.strftime("%Z")
                offset = format_utc_offset(dt.strftime("%z"))
                table_rows.append(f"| Washington, D.C. | {d_str} | {t_str} | {abbr} ({offset}) |")
            elif clean_l == "uk" or clean_l == "united kingdom":
                tz = zoneinfo.ZoneInfo("Europe/London")
                dt = datetime.now(tz)
                t_str = dt.strftime("%I:%M %p").lstrip("0")
                d_str = dt.strftime("%A, %B %d, %Y")
                abbr = dt.strftime("%Z")
                offset = format_utc_offset(dt.strftime("%z"))
                table_rows.append(f"| London | {d_str} | {t_str} | {abbr} ({offset}) |")
            else:
                tz = resolve_timezone(loc)
                dt = datetime.now(tz)
                t_str = dt.strftime("%I:%M %p").lstrip("0")
                d_str = dt.strftime("%A, %B %d, %Y")
                abbr = dt.strftime("%Z")
                offset = format_utc_offset(dt.strftime("%z"))
                loc_disp = "Washington, D.C." if clean_l in ("washington dc", "washington d c", "washington, d.c.") else loc.title()
                table_rows.append(f"| {loc_disp} | {d_str} | {t_str} | {abbr} ({offset}) |")

        table_md = "\n".join(table_rows)
        multi_loc_block = (
            f"\n=== VERIFIED MULTI-LOCATION WORLD CLOCK TABLE ===\n"
            f"The user asked for multiple locations. Present this exact table in your response:\n\n"
            f"{table_md}\n\n"
            f"INSTRUCTION:\n"
            f"- Output the table clearly with columns `| Location | Local Date | Local Time | Timezone |`.\n"
            f"- Note any date boundary differences (e.g. if one location is on Sunday while others are on Saturday).\n"
            f"=== END MULTI-LOCATION TABLE ===\n"
        )
        sections.append(multi_loc_block)

    # B) Single country with multiple timezones (e.g. 'What time is it in the USA?', 'Time in Australia')
    elif len(all_locs) == 1 and is_multi_timezone_country(all_locs[0]):
        country = all_locs[0]
        zones = get_country_multizone_snapshot(country)
        table_rows = []
        table_rows.append(f"| Region / Timezone | Local Date | Local Time | Timezone | UTC Offset |")
        table_rows.append("|---|---|---|---|---|")
        for z in zones:
            table_rows.append(f"| {z['label']} | {z['date']} | {z['time_12h']} | {z['tz_abbr']} | {z['utc_offset']} |")
        table_md = "\n".join(table_rows)

        country_block = (
            f"\n=== MULTI-TIMEZONE COUNTRY BREAKDOWN: {country.upper()} ===\n"
            f"Note: {country.title()} spans multiple time zones. Present this breakdown:\n\n"
            f"{table_md}\n\n"
            f"INSTRUCTION: Clearly explain that {country.title()} has multiple time zones, and list the exact local times in each major zone.\n"
            f"=== END MULTI-TIMEZONE COUNTRY BREAKDOWN ===\n"
        )
        sections.append(country_block)

    # C) Single specific city or single-timezone country (e.g. 'What time is it in Washington, D.C.?')
    elif len(all_locs) == 1:
        loc = all_locs[0]
        tz = resolve_timezone(loc)
        target_now = datetime.now(tz)
        t_time = target_now.strftime("%I:%M %p").lstrip("0")
        t_time_sec = target_now.strftime("%I:%M:%S %p").lstrip("0")
        t_date = target_now.strftime("%A, %B %d, %Y")
        t_day = target_now.strftime("%A")
        t_abbr = target_now.strftime("%Z")
        t_offset = format_utc_offset(target_now.strftime("%z"))
        t_full_name = get_descriptive_timezone_name(t_abbr, tz.key)
        loc_disp = "Washington, D.C." if loc.lower() in ("washington dc", "washington d c", "washington, d.c.") else loc.title()

        single_loc_block = (
            f"\n=== SPECIFIC LOCATION REQUESTED: '{loc_disp}' ===\n"
            f"Present the response cleanly in this exact structure as requested by the user:\n\n"
            f"**{loc_disp}**  \n"
            f"{t_date}  \n"
            f"{t_time}  \n"
            f"{t_full_name}  \n"
            f"{t_offset}\n\n"
            f"Live details for verification:\n"
            f"- Current local time: {t_time}\n"
            f"- Date: {t_date}\n"
            f"- Day of the week: {t_day}\n"
            f"- Timezone abbreviation: {t_abbr}\n"
            f"- UTC offset: {t_offset}\n"
            f"- IANA Identifier: `{tz.key}`\n"
            f"=== END SPECIFIC LOCATION ===\n"
        )
        sections.append(single_loc_block)

    # 3. RELATIVE WEEKDAY / DATE CALCULATIONS
    weekday_match = re.search(r"\b(next|last)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", user_query, re.IGNORECASE)
    if weekday_match:
        direction = weekday_match.group(1).lower()
        w_day = weekday_match.group(2).lower()
        key = f"{direction}_{w_day}"
        if key in snapshot["relative_dates"]:
            calculated_date = snapshot["relative_dates"][key]
            sections.append(f"\n### CALCULATED DATE FOR '{direction.title()} {w_day.title()}':\n- **{calculated_date}**\n")

    # Major world clocks formatted list
    world_clock_lines = "\n".join(f"- {city}: {val}" for city, val in snapshot["world_clocks"].items())

    extra_content = "".join(sections)

    context = f"""
=== ACCURATE REAL-TIME SYSTEM CLOCK & TEMPORAL CONTEXT ===
This information is provided directly by the server's live runtime clock at the exact moment of this request.
Under NO circumstances should you claim that you do not have access to real-time date or time data.

- **Current Time (User Clock)**: {snapshot['time_12h_short']} ({snapshot['time_12h']} {snapshot['timezone_abbr']})
- **Current Date**: {snapshot['date_full']}
- **Day of the Week**: {snapshot['day_of_week']}
- **User Local Timezone**: {snapshot['timezone_name']} ({snapshot['timezone_full']}, {snapshot['timezone_offset']})
- **UTC Time**: {snapshot['utc_iso']}

### DYNAMIC CALENDAR ANCHORS (Evaluated live from the current clock):
- **Yesterday**: {snapshot['relative_dates']['yesterday']}
- **Today**: {snapshot['relative_dates']['today']}
- **Tomorrow**: {snapshot['relative_dates']['tomorrow']}
- **Day after tomorrow**: {snapshot['relative_dates']['day_after_tomorrow']}
- **Next Monday**: {snapshot['relative_dates']['next_monday']}
- **Next Friday**: {snapshot['relative_dates']['next_friday']}
- **Last Friday**: {snapshot['relative_dates']['last_friday']}
{extra_content}
### MAJOR GLOBAL LIVE CLOCKS (Current moment):
{world_clock_lines}

### INSTRUCTIONS FOR WORLDWIDE DATE & TIME QUESTIONS:
1. Always state the real-time time or date directly and clearly.
2. If the user asks for a specific city or country, provide the exact time and date for that location.
3. For single city questions like 'What time is it in Washington, D.C.?', format as:
   **[Location]**
   [Day of week], [Month] [Day], [Year]
   [Time] AM/PM
   [Timezone Full Name] ([Timezone Abbreviation])
   [UTC Offset]
4. For multi-location questions (e.g. 'What time is it in India, USA, UK and Japan?'), present the clean Markdown comparison table with columns `| Location | Local Date | Local Time | Timezone |`.
5. For multi-timezone countries (e.g. 'What time is it in the USA?'), present the major time zones table.
6. For time difference questions (e.g. 'What is the time difference between India and USA?'), state the exact difference in hours and minutes, which location is ahead/behind, and both current local times and dates.
7. Account for date boundaries (e.g. when it is Saturday in America and Sunday in Australia/Japan, state the respective local dates correctly).
8. NEVER output disclaimers like "I do not have access to real-time data" or "Please check your device's clock".
=== END REAL-TIME TEMPORAL CONTEXT ===
"""
    return context.strip()
