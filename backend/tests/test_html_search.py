import httpx
import re
import urllib.parse
from html.parser import HTMLParser

class DDGHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.results = []
        self._current_result = None
        self._in_a = False
        self._in_snippet = False
        self._buffer = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        c = attrs_dict.get("class", "")
        if tag == "div" and "result " in f"{c} ":
            self._current_result = {"title": "", "url": "", "snippet": ""}
        elif tag == "a" and "result__a" in c and self._current_result is not None:
            self._in_a = True
            href = attrs_dict.get("href", "")
            if "uddg=" in href:
                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                clean_url = parsed.get("uddg", [href])[0]
            else:
                clean_url = href
            self._current_result["url"] = clean_url
            self._buffer = []
        elif tag == "a" and "result__snippet" in c and self._current_result is not None:
            self._in_snippet = True
            self._buffer = []

    def handle_endtag(self, tag):
        if tag == "a":
            text = "".join(self._buffer).strip()
            if self._in_a and self._current_result is not None:
                self._current_result["title"] = text
                self._in_a = False
            elif self._in_snippet and self._current_result is not None:
                self._current_result["snippet"] = text
                self._in_snippet = False
            self._buffer = []
        elif tag == "div" and self._current_result is not None:
            if self._current_result.get("url") and self._current_result["url"].startswith("http"):
                self.results.append(self._current_result)
            self._current_result = None

    def handle_data(self, data):
        if self._in_a or self._in_snippet:
            self._buffer.append(data)

def search_ddg(query: str, max_results: int = 5):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    url = "https://html.duckduckgo.com/html/"
    try:
        with httpx.Client(timeout=10.0, follow_redirects=True, headers=headers) as client:
            resp = client.post(url, data={"q": query})
            if resp.status_code == 200:
                parser = DDGHTMLParser()
                parser.feed(resp.text)
                return parser.results[:max_results]
    except Exception as e:
        print("Search error:", e)
    return []

if __name__ == "__main__":
    queries = ["Diwali 2026 date", "Holi 2026 date India", "who is the prime minister of UK"]
    for q in queries:
        r = search_ddg(q, 3)
        print(f"Query '{q}': {len(r)} results")
        for item in r:
            print(" ->", item["title"][:50], "|", item["url"])
