import re
import uuid
import random
import urllib.parse
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import httpx
from ddgs import DDGS
from app.config import settings

logger = logging.getLogger("lumiq.image")

IMAGE_TRIGGER_PATTERNS = [
    r"\b(create|generate|make|draw|paint|render|produce)\s+(an?\s+|the\s+)?(image|picture|photo|painting|illustration|portrait|wallpaper|drawing|artwork|graphic|map)\b",
    r"\b(give|show|send|display|get)\s+(me\s+)?(an?\s+|the\s+)?(image|picture|photo|painting|illustration|wallpaper|map)\b",
    r"\b(image|picture|photo|illustration|drawing|artwork|map)\s+(of|for|into|showing|depicting)\b",
    r"\b(draw|paint)\s+(me\s+)?(an?\s+|the\s+)?\b",
    r"\b(visualize|illustrate)\b",
    r"\b(image|picture|photo|wallpaper|map)\b\s*$",
    r"^/image\b",
    r"^image:\b",
]

# Patterns for queries that require accurate, factual, official representations (like real maps, diagrams, flags)
FACTUAL_PATTERNS = [
    r"\b(map|atlas|geography|globe|continents?|territory|borders?)\b",
    r"\b(flag|coat of arms|emblem|symbol)\b",
    r"\b(diagram|blueprint|schematic|anatomy|periodic table)\b",
    r"\b(taj mahal|eiffel tower|statue of liberty|pyramids?|monument|qutub minar)\b",
]

def is_factual_image_request(query: str) -> bool:
    ql = query.lower()
    return any(re.search(p, ql) for p in FACTUAL_PATTERNS)

def should_generate_image(query: str, explicit_flag: Optional[bool] = None) -> bool:
    if explicit_flag is not None:
        return explicit_flag

    q_lower = query.lower().strip()
    for pattern in IMAGE_TRIGGER_PATTERNS:
        if re.search(pattern, q_lower):
            return True
    return False

def clean_image_prompt(query: str) -> str:
    cleaned = query.strip()
    # Strip leading slash commands or prefix labels
    cleaned = re.sub(r"^/(image|imagine|draw|create)\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^image:\s*", "", cleaned, flags=re.IGNORECASE)

    # Strip conversational lead-ins
    strip_patterns = [
        r"^(can you\s+)?(please\s+)?(create|generate|make|draw|paint|produce|render|give|show|send|display|get)\s+(me\s+)?(the\s+|an?\s+)?(image|picture|photo|painting|illustration|portrait|artwork|graphic)?\s*(of|into|showing|depicting|with|for)?\s*",
        r"^(can you\s+)?(please\s+)?(draw|paint|illustrate)\s+(me\s+)?(the\s+|an?\s+)?",
        r"^(give me\s+)?(the\s+|an?\s+)?(image|picture|photo)\s+(of|into|showing|for)?\s*",
    ]
    for pattern in strip_patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE).strip()

    # Strip trailing image phrases: "... image", "... picture", "... photo", "... wallpaper"
    cleaned = re.sub(r"\s+(image|picture|photo|painting|illustration|artwork|wallpaper|drawing)\s*$", "", cleaned, flags=re.IGNORECASE).strip()

    # Fallback if empty or generic
    if not cleaned or cleaned.lower() in ["in any image can create", "any image", "an image", "image", "picture", "photo"]:
        cleaned = "a stunning creative digital art masterpiece, highly detailed"

    return cleaned

def is_valid_image_bytes(content: bytes, min_size: int = 5000) -> bool:
    if len(content) < min_size:
        return False
    # Check JPEG, PNG, or WebP/GIF magic numbers
    if content[:3] == b"\xff\xd8\xff":  # JPEG
        return True
    if content[:4] == b"\x89PNG":      # PNG
        return True
    if content[:4] == b"RIFF" and b"WEBP" in content[:16]:  # WebP
        return True
    if content[:4] in (b"GIF8", b"GIF7"):  # GIF
        return True
    return False

async def fetch_authoritative_image(prompt: str) -> Optional[Tuple[bytes, str, str]]:
    """
    Fetches an authoritative, real, high-resolution image for maps, diagrams, landmarks, and flags.
    Returns (image_bytes, ext, source_url) if successful.
    """
    search_query = prompt
    p_lower = prompt.lower()
    if "map" in p_lower:
        if "india" in p_lower:
            search_query = "India official political map with states high resolution"
        else:
            search_query = f"{prompt} official map high resolution"
    else:
        search_query = f"{prompt} high resolution"

    try:
        with DDGS() as ddgs:
            results = list(ddgs.images(search_query, max_results=8))
    except Exception as e:
        logger.warning(f"[ImageService] DDGS search error for '{search_query}': {e}")
        return None

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
    }

    for r in results:
        img_url = r.get("image")
        if not img_url:
            continue
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(img_url, headers=headers)
                ctype = resp.headers.get("content-type", "")
                if resp.status_code == 200 and ctype.startswith("image/") and is_valid_image_bytes(resp.content, min_size=15000):
                    ext = ".jpg"
                    if "png" in ctype or resp.content[:4] == b"\x89PNG":
                        ext = ".png"
                    elif "webp" in ctype:
                        ext = ".webp"
                    logger.info(f"[ImageService] Found authoritative image for '{prompt}' ({len(resp.content)} bytes)")
                    return resp.content, ext, img_url
        except Exception:
            continue

    return None

async def generate_ai_image(prompt: str, width: int = 768, height: int = 768) -> Dict[str, Any]:
    cleaned_prompt = clean_image_prompt(prompt)
    if not cleaned_prompt:
        cleaned_prompt = "a beautiful digital art masterpiece"

    settings.GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    seed = random.randint(1000, 9999999)

    # 1. Check if the prompt asks for an authoritative, factual entity (e.g. Map of India, flag, diagram)
    if is_factual_image_request(cleaned_prompt):
        logger.info(f"[ImageService] Detected factual/map query for '{cleaned_prompt}', fetching authoritative image...")
        auth_data = await fetch_authoritative_image(cleaned_prompt)
        if auth_data:
            content, ext, source_url = auth_data
            filename = f"map_{uuid.uuid4().hex[:12]}_{seed}{ext}"
            save_path = settings.GENERATED_DIR / filename
            with open(save_path, "wb") as f:
                f.write(content)
            local_url = f"/uploads/generated/{filename}"
            return {
                "success": True,
                "image_url": local_url,
                "external_url": source_url,
                "prompt": cleaned_prompt,
                "enhanced_prompt": cleaned_prompt,
                "width": width,
                "height": height,
                "seed": seed,
                "is_factual": True,
            }

    # 2. For creative art or as fallback: use fast AI diffusion synthesis
    enhanced_prompt = cleaned_prompt
    if len(cleaned_prompt.split()) < 10:
        enhanced_prompt = f"{cleaned_prompt}, high quality, detailed, vibrant, masterpiece"

    encoded_prompt = urllib.parse.quote(enhanced_prompt)

    candidate_urls = [
        f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={seed}&model=turbo",
        f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={seed}",
    ]

    filename = f"gen_{uuid.uuid4().hex[:12]}_{seed}.jpg"
    save_path = settings.GENERATED_DIR / filename
    local_url = f"/uploads/generated/{filename}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
    }

    for target_url in candidate_urls:
        try:
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
                resp = await client.get(target_url, headers=headers)
                ctype = resp.headers.get("content-type", "")
                if resp.status_code == 200 and ctype.startswith("image/") and is_valid_image_bytes(resp.content, min_size=5000):
                    with open(save_path, "wb") as f:
                        f.write(resp.content)
                    logger.info(f"[ImageService] Successfully saved AI image to {save_path} ({len(resp.content)} bytes)")
                    return {
                        "success": True,
                        "image_url": local_url,
                        "external_url": target_url,
                        "prompt": cleaned_prompt,
                        "enhanced_prompt": enhanced_prompt,
                        "width": width,
                        "height": height,
                        "seed": seed,
                        "is_factual": False,
                    }
        except Exception as e:
            logger.warning(f"[ImageService] Attempt failed for {target_url}: {e}")
            continue

    # Fallback to direct external URL
    fallback_url = candidate_urls[0]
    return {
        "success": True,
        "image_url": fallback_url,
        "external_url": fallback_url,
        "prompt": cleaned_prompt,
        "enhanced_prompt": enhanced_prompt,
        "width": width,
        "height": height,
        "seed": seed,
        "is_factual": False,
    }
