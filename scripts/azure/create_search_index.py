from __future__ import annotations

import httpx

from azure_env import require_search_env


FIELDS = [
    {"name": "id", "type": "Edm.String", "key": True, "filterable": True, "retrievable": True},
    {"name": "title", "type": "Edm.String", "searchable": True, "retrievable": True},
    {"name": "content", "type": "Edm.String", "searchable": True, "retrievable": True},
    {"name": "source_type", "type": "Edm.String", "filterable": True, "retrievable": True},
    {"name": "source_id", "type": "Edm.String", "filterable": True, "retrievable": True},
    {"name": "citation", "type": "Edm.String", "retrievable": True},
    {"name": "url", "type": "Edm.String", "retrievable": True},
    {"name": "chunk_id", "type": "Edm.String", "filterable": True, "retrievable": True},
    {"name": "experiment_id", "type": "Edm.String", "filterable": True, "retrievable": True},
    {"name": "skill_domain", "type": "Edm.String", "filterable": True, "retrievable": True},
    {"name": "failure_category", "type": "Edm.String", "filterable": True, "retrievable": True},
    {"name": "permission_scope", "type": "Edm.String", "filterable": True, "retrievable": True},
    {"name": "tags", "type": "Collection(Edm.String)", "filterable": True, "retrievable": True},
]


def main() -> int:
    endpoint, key, index = require_search_env()
    url = f"{endpoint}/indexes/{index}?api-version=2023-11-01"
    body = {
        "name": index,
        "fields": FIELDS,
        "semantic": {
            "configurations": [
                {
                    "name": "default",
                    "prioritizedFields": {
                        "titleField": {"fieldName": "title"},
                        "prioritizedContentFields": [{"fieldName": "content"}],
                    },
                }
            ]
        },
    }
    response = httpx.put(url, headers={"api-key": key, "Content-Type": "application/json"}, json=body, timeout=30)
    if response.status_code >= 400:
        print(response.text)
        return 1
    print(f"Created or updated Azure AI Search index: {index}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
