import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.date_time_service import (
    is_datetime_query,
    build_temporal_context,
    get_live_time_snapshot,
    resolve_timezone
)

def run_tests():
    queries = [
        "What is today's date?",
        "What time is it now?",
        "What is the current date and time?",
        "What time is it in India?",
        "What time is it in New York?",
        "What will tomorrow's date be?",
        "What day is next Monday?",
        "Who is the CEO of Google?"
    ]

    for q in queries:
        detected = is_datetime_query(q)
        print(f"[{'DATETIME' if detected else 'OTHER'}] {q}")

    snap = get_live_time_snapshot("Asia/Kolkata")
    print("\n--- Live Snapshot (Asia/Kolkata) ---")
    print("Time:", snap["time_12h_short"])
    print("Date:", snap["date_full"])
    print("Tomorrow:", snap["relative_dates"]["tomorrow"])
    print("Next Monday:", snap["relative_dates"]["next_monday"])

    print("\n--- Context generation for 'What time is it in New York?' ---")
    ctx = build_temporal_context("What time is it in New York?", "Asia/Kolkata")
    print(ctx)

if __name__ == "__main__":
    run_tests()
