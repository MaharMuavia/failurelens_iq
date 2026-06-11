from __future__ import annotations

import httpx

from azure_env import require_search_env


def main() -> int:
    endpoint, key, index = require_search_env()
    url = f"{endpoint}/indexes/{index}/docs/search?api-version=2023-11-01"
    body = {"search": "minority f1 validation leakage remediation DP-100", "top": 5}
    response = httpx.post(url, headers={"api-key": key, "Content-Type": "application/json"}, json=body, timeout=30)
    if response.status_code >= 400:
        print(response.text)
        return 1
    results = response.json().get("value", [])
    if not results:
        print("No Azure AI Search results returned.")
        return 1
    for item in results:
        print("-" * 60)
        print(f"title: {item.get('title')}")
        print(f"score: {item.get('@search.score')}")
        print(f"citation: {item.get('citation')}")
        print(str(item.get("content", ""))[:300])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
