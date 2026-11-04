# ============================================================================
# LOKR AI - Worldwide Real-Time Date & Time Automated Test Suite
# ============================================================================

import sys
import os
import asyncio

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.date_time_service import (
    is_datetime_query,
    resolve_timezone,
    extract_all_target_locations,
    extract_target_location,
    is_time_difference_query,
    extract_time_difference_locations,
    calculate_time_difference,
    is_multi_timezone_country,
    get_country_multizone_snapshot,
    build_temporal_context
)
from app.services.ai_service import ai_service

def test_worldwide_timezone_resolution():
    print("=== TEST 1: Worldwide City & Country Timezone Resolution ===")
    test_locations = [
        ("Washington, D.C.", "America/New_York"),
        ("Hyderabad", "Asia/Kolkata"),
        ("London", "Europe/London"),
        ("Tokyo", "Asia/Tokyo"),
        ("Dubai", "Asia/Dubai"),
        ("Sydney", "Australia/Sydney"),
        ("California", "America/Los_Angeles"),
        ("Paris", "Europe/Paris"),
        ("Berlin", "Europe/Berlin"),
        ("Singapore", "Asia/Singapore"),
        ("Auckland", "Pacific/Auckland"),
        ("Johannesburg", "Africa/Johannesburg"),
        ("São Paulo", "America/Sao_Paulo"),
        ("Toronto", "America/Toronto"),
        ("Nairobi", "Africa/Nairobi"),
        ("Cairo", "Africa/Cairo"),
    ]

    all_passed = True
    for loc, exp_tz in test_locations:
        res = resolve_timezone(loc)
        passed = res.key == exp_tz
        if not passed:
            all_passed = False
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"[{status}] '{loc}' -> {res.key} (expected {exp_tz})")

    print(f"\nResolution Test: {'ALL PASSED ✅' if all_passed else 'SOME FAILED ❌'}\n")
    return all_passed

def test_location_extractions():
    print("=== TEST 2: Single and Multi-Location Extraction ===")
    queries = [
        ("What time is it in Washington, D.C.?", ["Washington, D.C."]),
        ("What time is it in India, USA, UK and Japan?", ["India", "USA", "UK", "Japan"]),
        ("Time in London, Paris, and Tokyo", ["London", "Paris", "Tokyo"]),
        ("What is the time in Dubai?", ["Dubai"]),
    ]

    all_passed = True
    for q, exp_locs in queries:
        actual = extract_all_target_locations(q)
        passed = actual == exp_locs
        if not passed:
            all_passed = False
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"[{status}] '{q}' -> {actual} (expected {exp_locs})")

    print(f"\nExtraction Test: {'ALL PASSED ✅' if all_passed else 'SOME FAILED ❌'}\n")
    return all_passed

def test_time_difference():
    print("=== TEST 3: Time Difference Detection & Calculation ===")
    diff_queries = [
        "What is the time difference between India and USA?",
        "What is the time difference between Hyderabad and London?",
        "How many hours is Tokyo ahead of New York?",
    ]

    all_passed = True
    for q in diff_queries:
        is_diff = is_time_difference_query(q)
        pair = extract_time_difference_locations(q)
        if is_diff and pair:
            loc1, loc2 = pair
            diff = calculate_time_difference(loc1, loc2)
            print(f"[✅ PASS] '{q}' -> {pair}")
            print(f"         Result: {diff['relation_text']}")
            print(f"         {loc1}: {diff['time1']} ({diff['tz1_abbr']}), {loc2}: {diff['time2']} ({diff['tz2_abbr']})")
        else:
            all_passed = False
            print(f"[❌ FAIL] '{q}' -> is_diff={is_diff}, pair={pair}")

    print(f"\nTime Difference Test: {'ALL PASSED ✅' if all_passed else 'SOME FAILED ❌'}\n")
    return all_passed

def test_multi_timezone_countries():
    print("=== TEST 4: Multi-Timezone Countries ===")
    countries = ["USA", "Australia", "Canada"]
    all_passed = True
    for c in countries:
        is_multi = is_multi_timezone_country(c)
        zones = get_country_multizone_snapshot(c)
        passed = is_multi and len(zones) >= 4
        if not passed:
            all_passed = False
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"[{status}] '{c}' -> multi={is_multi}, zones={len(zones)}")
        for z in zones[:2]:
            print(f"         - {z['label']}: {z['time_12h']} {z['tz_abbr']} ({z['utc_offset']})")

    print(f"\nMulti-Timezone Country Test: {'ALL PASSED ✅' if all_passed else 'SOME FAILED ❌'}\n")
    return all_passed

async def test_live_ai_responses():
    print("=== TEST 5: Live AI Response Synthesis & Exact Formatting ===")

    # Test 1: Washington, D.C. single location format
    q1 = "What time is it in Washington, D.C.?"
    ctx1 = build_temporal_context(q1, "Asia/Kolkata")
    prompt1 = ai_service.build_system_prompt(user_query=q1, client_timezone="Asia/Kolkata")
    resp1 = []
    async for chunk in ai_service.generate_chat_stream([{"role": "user", "content": q1}], prompt1):
        resp1.append(chunk)
    ans1 = "".join(resp1)
    print(f"\n[Prompt]: {q1}\n[Response]:\n{ans1}\n")

    # Test 2: Multi-location comparison table
    q2 = "What time is it in India, USA, UK and Japan?"
    prompt2 = ai_service.build_system_prompt(user_query=q2, client_timezone="Asia/Kolkata")
    resp2 = []
    async for chunk in ai_service.generate_chat_stream([{"role": "user", "content": q2}], prompt2):
        resp2.append(chunk)
    ans2 = "".join(resp2)
    print(f"\n[Prompt]: {q2}\n[Response]:\n{ans2}\n")

    # Verify key tokens
    has_wash = "Washington, D.C." in ans1
    has_table = "|" in ans2 and "India" in ans2 and "Japan" in ans2
    passed = has_wash and has_table
    print(f"Live AI Response Test: {'PASSED ✅' if passed else 'FAILED ❌'}\n")
    return passed

if __name__ == "__main__":
    t1 = test_worldwide_timezone_resolution()
    t2 = test_location_extractions()
    t3 = test_time_difference()
    t4 = test_multi_timezone_countries()
    t5 = asyncio.run(test_live_ai_responses())

    print("============================================================")
    print(f"ALL WORLDWIDE TIME TESTS: {'PASS ✅' if all([t1, t2, t3, t4, t5]) else 'SOME FAILED ❌'}")
    print("============================================================")
