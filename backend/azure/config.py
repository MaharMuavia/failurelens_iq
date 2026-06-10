from __future__ import annotations

import os
from dataclasses import dataclass


def _present(*names: str) -> bool:
    return all(bool(os.getenv(name, "").strip()) for name in names)


@dataclass(frozen=True)
class AzureConfig:
    app_mode: str = os.getenv("APP_MODE", "demo").strip().lower() or "demo"
    azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    azure_openai_deployment: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
    azure_ai_search_endpoint: str = os.getenv("AZURE_AI_SEARCH_ENDPOINT", "")
    azure_ai_search_key: str = os.getenv("AZURE_AI_SEARCH_KEY", "")
    azure_ai_search_index: str = os.getenv("AZURE_AI_SEARCH_INDEX", "")
    azure_storage_connection_string: str = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
    azure_blob_container: str = os.getenv("AZURE_BLOB_CONTAINER", "")
    azure_cosmos_endpoint: str = os.getenv("AZURE_COSMOS_ENDPOINT", "")
    azure_cosmos_key: str = os.getenv("AZURE_COSMOS_KEY", "")
    azure_cosmos_database: str = os.getenv("AZURE_COSMOS_DATABASE", "")
    azure_cosmos_container: str = os.getenv("AZURE_COSMOS_CONTAINER", "")

    @property
    def enabled_integrations(self) -> dict[str, bool]:
        return {
            "local_iq": True,
            "azure_openai": _present("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_DEPLOYMENT"),
            "azure_ai_search": _present("AZURE_AI_SEARCH_ENDPOINT", "AZURE_AI_SEARCH_KEY", "AZURE_AI_SEARCH_INDEX"),
            "azure_blob_storage": _present("AZURE_STORAGE_CONNECTION_STRING", "AZURE_BLOB_CONTAINER"),
            "azure_cosmos_db": _present("AZURE_COSMOS_ENDPOINT", "AZURE_COSMOS_KEY", "AZURE_COSMOS_DATABASE", "AZURE_COSMOS_CONTAINER"),
        }

    @property
    def is_demo(self) -> bool:
        return self.app_mode != "production"


def load_azure_config() -> AzureConfig:
    return AzureConfig()
