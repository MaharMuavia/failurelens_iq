from __future__ import annotations

import os
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Eagerly load the .env file if it exists
load_dotenv()

class Settings(BaseModel):
    # App Settings
    APP_MODE: str = Field(default="demo")
    IQ_PROVIDER: str = Field(default="local")
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    DEBUG: bool = Field(default=False)
    LOG_LEVEL: str = Field(default="INFO")
    
    # CORS Settings
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:5173", "http://localhost:3000"])
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True)
    CORS_ALLOW_METHODS: list[str] = Field(default_factory=lambda: ["*"])
    CORS_ALLOW_HEADERS: list[str] = Field(default_factory=lambda: ["*"])
    
    # Auth Settings
    ENABLE_AUTH: bool = Field(default=False)
    API_KEY: str = Field(default="")
    
    # Limit Settings
    MAX_UPLOAD_BYTES: int = Field(default=1048576) # 1 MB
    REQUEST_TIMEOUT_SECONDS: int = Field(default=30)
    RATE_LIMIT_ENABLED: bool = Field(default=True)
    RATE_LIMIT_PER_MINUTE: int = Field(default=60)
    DEMO_CACHE_TTL_SECONDS: int = Field(default=300)
    
    # Paths Settings
    REPORT_OUTPUT_DIR: str = Field(default="reports")
    KNOWLEDGE_DIR: str = Field(default="knowledge/foundry_docs")
    UPLOAD_STORE_PATH: str = Field(default="data/uploads/uploaded_experiments.json")
    
    # Azure Settings
    AZURE_OPENAI_ENDPOINT: str = Field(default="")
    AZURE_OPENAI_API_KEY: str = Field(default="")
    AZURE_OPENAI_DEPLOYMENT: str = Field(default="")
    AZURE_AI_SEARCH_ENDPOINT: str = Field(default="")
    AZURE_AI_SEARCH_KEY: str = Field(default="")
    AZURE_AI_SEARCH_INDEX: str = Field(default="")
    AZURE_STORAGE_CONNECTION_STRING: str = Field(default="")
    AZURE_BLOB_CONTAINER: str = Field(default="")
    AZURE_COSMOS_ENDPOINT: str = Field(default="")
    AZURE_COSMOS_KEY: str = Field(default="")
    AZURE_COSMOS_DATABASE: str = Field(default="")
    AZURE_COSMOS_CONTAINER: str = Field(default="")

    @classmethod
    def load_from_env(cls) -> Settings:
        cors_str = os.getenv("CORS_ORIGINS", "")
        if cors_str:
            cors_origins = [orig.strip() for orig in cors_str.split(",") if orig.strip()]
        else:
            cors_origins = ["http://localhost:5173", "http://localhost:3000"]
            
        def get_bool_env(name: str, default: bool) -> bool:
            val = os.getenv(name)
            if val is None:
                return default
            return val.lower() in ("true", "1", "yes")

        def get_int_env(name: str, default: int) -> int:
            val = os.getenv(name)
            if val is None:
                return default
            try:
                return int(val)
            except ValueError:
                return default

        return cls(
            APP_MODE=os.getenv("APP_MODE", "demo").strip().lower() or "demo",
            IQ_PROVIDER=os.getenv("IQ_PROVIDER", "local").strip().lower() or "local",
            HOST=os.getenv("HOST", "0.0.0.0").strip(),
            PORT=get_int_env("PORT", 8000),
            DEBUG=get_bool_env("DEBUG", False),
            LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO").strip(),
            CORS_ORIGINS=cors_origins,
            CORS_ALLOW_CREDENTIALS=get_bool_env("CORS_CREDENTIALS", get_bool_env("CORS_ALLOW_CREDENTIALS", True)),
            CORS_ALLOW_METHODS=[m.strip() for m in os.getenv("CORS_METHODS", "*").split(",") if m.strip()],
            CORS_ALLOW_HEADERS=[h.strip() for h in os.getenv("CORS_HEADERS", "*").split(",") if h.strip()],
            ENABLE_AUTH=get_bool_env("ENABLE_AUTH", False),
            API_KEY=os.getenv("API_KEY", "").strip(),
            MAX_UPLOAD_BYTES=get_int_env("MAX_UPLOAD_BYTES", 1048576),
            REQUEST_TIMEOUT_SECONDS=get_int_env("REQUEST_TIMEOUT_SECONDS", 30),
            RATE_LIMIT_ENABLED=get_bool_env("RATE_LIMIT_ENABLED", True),
            RATE_LIMIT_PER_MINUTE=get_int_env("RATE_LIMIT_PER_MINUTE", 60),
            DEMO_CACHE_TTL_SECONDS=get_int_env("DEMO_CACHE_TTL_SECONDS", 300),
            REPORT_OUTPUT_DIR=os.getenv("REPORT_OUTPUT_DIR", "reports").strip(),
            KNOWLEDGE_DIR=os.getenv("KNOWLEDGE_DIR", "knowledge/foundry_docs").strip(),
            UPLOAD_STORE_PATH=os.getenv("UPLOAD_STORE_PATH", "data/uploads/uploaded_experiments.json").strip(),
            AZURE_OPENAI_ENDPOINT=os.getenv("AZURE_OPENAI_ENDPOINT", "").strip(),
            AZURE_OPENAI_API_KEY=os.getenv("AZURE_OPENAI_API_KEY", "").strip(),
            AZURE_OPENAI_DEPLOYMENT=os.getenv("AZURE_OPENAI_DEPLOYMENT", "").strip(),
            AZURE_AI_SEARCH_ENDPOINT=os.getenv("AZURE_AI_SEARCH_ENDPOINT", "").strip().rstrip("/"),
            AZURE_AI_SEARCH_KEY=os.getenv("AZURE_AI_SEARCH_KEY", "").strip(),
            AZURE_AI_SEARCH_INDEX=os.getenv("AZURE_AI_SEARCH_INDEX", "").strip(),
            AZURE_STORAGE_CONNECTION_STRING=os.getenv("AZURE_STORAGE_CONNECTION_STRING", "").strip(),
            AZURE_BLOB_CONTAINER=os.getenv("AZURE_BLOB_CONTAINER", "").strip(),
            AZURE_COSMOS_ENDPOINT=os.getenv("AZURE_COSMOS_ENDPOINT", "").strip(),
            AZURE_COSMOS_KEY=os.getenv("AZURE_COSMOS_KEY", "").strip(),
            AZURE_COSMOS_DATABASE=os.getenv("AZURE_COSMOS_DATABASE", "").strip(),
            AZURE_COSMOS_CONTAINER=os.getenv("AZURE_COSMOS_CONTAINER", "").strip(),
        )

# Singleton configuration settings instance
settings = Settings.load_from_env()
