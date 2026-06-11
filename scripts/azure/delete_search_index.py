from __future__ import annotations

import httpx

from azure_env import require_search_env


def main() -> int:
    endpoint, key, index = require_search_env()
    url = f"{endpoint}/indexes/{index}?api-version=2023-11-01"
    response = httpx.delete(url, headers={"api-key": key}, timeout=30)
    if response.status_code in {200, 204}:
        print(f"Deleted Azure AI Search index: {index}")
        return 0
    if response.status_code == 404:
        print(f"Index not found: {index}")
        return 0
    print(response.text)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
