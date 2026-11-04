from ddgs import DDGS

queries = [
    "Diwali 2026 date",
    "latest python release version",
    "Tesla stock price",
    "Holi 2026 date",
    "who is the prime minister of UK"
]

with DDGS() as d:
    for q in queries:
        try:
            r = d.text(q, max_results=3, backend="duckduckgo,brave,startpage,wikipedia")
            print(f"Query '{q}': {len(r)} results")
            for item in r[:2]:
                print(" ->", item.get("title")[:60], "|", item.get("href"))
        except Exception as e:
            print(f"Query '{q}' ERROR: {e}")
