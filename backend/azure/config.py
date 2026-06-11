from __future__ import annotations

import os
from dataclasses import dataclass


def _present(*names: str) -> bool:
    return all(bool(os.getenv(name, "").strip()) for name in names)


@dataclass(frozen=True)
class AzureConfig:
    app_mode: str = "demo"
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = ""
    azure_ai_search_endpoint: str = ""
    azure_ai_search_key: str = ""
    azure_ai_search_index: str = ""
    azure_storage_connection_string: str = ""
    azure_blob_container: str = ""
    azure_cosmos_endpoint: str = ""
    azure_cosmos_key: str = ""
    azure_cosmos_database: str = ""
    azure_cosmos_container: str = ""

    @property
    def enabled_integrations(self) -> dict[str, bool]:
        return {
            "local_iq": True,
            "azure_openai": bool(self.azure_openai_endpoint and self.azure_openai_api_key and self.azure_openai_deployment),
            "azure_ai_search": bool(self.azure_ai_search_endpoint and self.azure_ai_search_key and self.azure_ai_search_index),
            "azure_blob_storage": bool(self.azure_storage_connection_string and self.azure_blob_container),
            "azure_cosmos_db": bool(self.azure_cosmos_endpoint and self.azure_cosmos_key and self.azure_cosmos_database and self.azure_cosmos_container),
        }

    @property
    def is_demo(self) -> bool:
        return self.app_mode != "production"


def load_azure_config() -> AzureConfig:
    from backend.core.config import settings
    return AzureConfig(
        app_mode=settings.APP_MODE,
        azure_openai_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        azure_openai_api_key=settings.AZURE_OPENAI_API_KEY,
        azure_openai_deployment=settings.AZURE_OPENAI_DEPLOYMENT,
        azure_ai_search_endpoint=settings.AZURE_AI_SEARCH_ENDPOINT,
        azure_ai_search_key=settings.AZURE_AI_SEARCH_KEY,
        azure_ai_search_index=settings.AZURE_AI_SEARCH_INDEX,
        azure_storage_connection_string=settings.AZURE_STORAGE_CONNECTION_STRING,
        azure_blob_container=settings.AZURE_BLOB_CONTAINER,
        azure_cosmos_endpoint=settings.AZURE_COSMOS_ENDPOINT,
        azure_cosmos_key=settings.AZURE_COSMOS_KEY,
        azure_cosmos_database=settings.AZURE_COSMOS_DATABASE,
        azure_cosmos_container=settings.AZURE_COSMOS_CONTAINER,
    )
