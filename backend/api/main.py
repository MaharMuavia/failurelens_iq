from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from backend.azure.config import load_azure_config
from backend.azure.grounding_adapter import GroundingAdapter
from backend.azure.openai_client import AzureOpenAIClient
from backend.core.orchestrator import Orchestrator
from backend.services.azure_foundry_iq_provider import AzureFoundryIQProvider
from backend.services.foundry_iq_local_adapter import FoundryIQLocalAdapter
from backend.services.knowledge_index import KnowledgeIndex
from backend.services.llm_reasoning_provider import LLMReasoningProvider
from backend.services.openai_client import OpenAIClient
from backend.services.foundry_openai_client import FoundryOpenAIClient
from backend.services.foundry_agent_client import FoundryAgentClient
from backend.services.report_service import ReportService
from backend.services.scoring_service import ScoringService
from backend.utils.data_loader import DataLoader

# Hardening Modules
from backend.core.config import settings
from backend.core.middleware import MaxBodySizeMiddleware, SecurityHeadersMiddleware
from backend.core.rate_limit import RateLimitMiddleware
from backend.core.logging import StructuredLoggingMiddleware, logger
from backend.services.experiment_store import ExperimentStore
from backend.services.demo_cache import DemoCache

# Routers
from backend.api.routes.health import router as health_router
from backend.api.routes.agents import router as agents_router
from backend.api.routes.experiments import router as experiments_router
from backend.api.routes.analysis import router as analysis_router
from backend.api.routes.demo import router as demo_router
from backend.api.routes.knowledge import router as knowledge_router
from backend.api.routes.manager import router as manager_router
from backend.api.routes.report import router as report_router
from backend.api.routes.readiness import router as readiness_router
from backend.api.routes.cost import router as cost_router
from backend.api.routes.iq_status import router as iq_status_router
from backend.api.routes.proof import router as proof_router


JUDGE_AGENTS = [
    {
        "name": "FailureClassifierAgent",
        "role": "Classifies failed ML experiments into repeatable failure categories.",
        "judging_purpose": "Shows why a reasoning agent is needed to resolve conflicting signals instead of tagging failures manually.",
        "input": "Experiment metrics, logs, validation strategy, failure observation, and known labels.",
        "output": "Failure category, triggered rules, conflict resolution, confidence, and audit trace.",
        "trace_fields": ["thought_type", "evidence", "confidence", "uncertainty", "next_action"],
    },
    {
        "name": "RootCauseAnalyzerAgent",
        "role": "Explains root cause, violated assumption, knowledge gap, and counter-evidence.",
        "judging_purpose": "Demonstrates safe, evidence-bound reasoning without exposing hidden chain-of-thought.",
        "input": "Failure category, experiment packet, local or Azure grounding, and planner context.",
        "output": "Root cause analysis, evidence strength, reflection notes, and human-review flag.",
        "trace_fields": ["thought_type", "evidence", "confidence", "uncertainty", "assumptions"],
    },
    {
        "name": "ExperimentHistorianAgent",
        "role": "Finds similar historical failed experiments and repeated team learning patterns.",
        "judging_purpose": "Turns failed experiments into reusable organizational memory.",
        "input": "Current experiment vector, historical experiment logs, and team context.",
        "output": "Similar historical experiments, repeated patterns, prior fixes, and team learning gap.",
        "trace_fields": ["thought_type", "evidence", "confidence", "uncertainty", "next_action"],
    },
    {
        "name": "PrescriptiveCoachAgent",
        "role": "Creates an evidence-bound remediation plan for the team.",
        "judging_purpose": "Connects diagnosis to concrete learning actions rather than generic advice.",
        "input": "Diagnosis, historical memory, certification mapping, team load, and playbook grounding.",
        "output": "3-day plan, 7-day plan, hands-on lab, manager note, and responsible AI note.",
        "trace_fields": ["thought_type", "evidence", "confidence", "uncertainty", "next_action"],
    },
    {
        "name": "CertificationEvaluatorAgent",
        "role": "Maps the failure to Microsoft skill domains and readiness questions.",
        "judging_purpose": "Makes the learning intervention measurable and certification aligned.",
        "input": "Failure category, knowledge gap, current certifications, and local/Azure grounding.",
        "output": "Recommended certification, learning path, assessment questions, and readiness confidence.",
        "trace_fields": ["thought_type", "evidence", "confidence", "uncertainty", "grounding_refs"],
    },
    {
        "name": "IntegrationManagerAgent",
        "role": "Builds the final executive report, grounding summary, and manager action view.",
        "judging_purpose": "Packages multi-agent reasoning into judge- and enterprise-ready evidence.",
        "input": "All agent outputs, confidence gate result, team insights, and grounding refs.",
        "output": "Executive summary, manager summary, audit-ready trace, and judge notes.",
        "trace_fields": ["agent_name", "role", "input_summary", "findings", "audit_entries"],
    },
]


def build_iq_provider(config: Any, grounding_adapter: GroundingAdapter, knowledge_index: KnowledgeIndex) -> Any:
    integrations = config.enabled_integrations
    if integrations.get("azure_ai_search"):
        return AzureFoundryIQProvider(grounding_adapter)
    return FoundryIQLocalAdapter()


# Global singletons to prevent repeated disk loading during app re-creations in tests
_GLOBAL_DATA_LOADER: DataLoader | None = None
_GLOBAL_KNOWLEDGE_INDEX: KnowledgeIndex | None = None
_GLOBAL_ORCHESTRATOR: Orchestrator | None = None
_STARTUP_DURATION_MS: float = 0.0
_STARTUP_LOADED: bool = False

def get_global_data_loader() -> DataLoader:
    global _GLOBAL_DATA_LOADER
    if _GLOBAL_DATA_LOADER is None:
        _GLOBAL_DATA_LOADER = DataLoader()
        _GLOBAL_DATA_LOADER.load_all()
    return _GLOBAL_DATA_LOADER

def get_global_knowledge_index() -> KnowledgeIndex:
    global _GLOBAL_KNOWLEDGE_INDEX
    if _GLOBAL_KNOWLEDGE_INDEX is None:
        _GLOBAL_KNOWLEDGE_INDEX = KnowledgeIndex(Path(settings.KNOWLEDGE_DIR))
    return _GLOBAL_KNOWLEDGE_INDEX

def init_startup_globals():
    global _STARTUP_DURATION_MS, _STARTUP_LOADED
    if _STARTUP_LOADED:
        return
    start = time.perf_counter()
    get_global_data_loader()
    get_global_knowledge_index()
    _STARTUP_DURATION_MS = round((time.perf_counter() - start) * 1000, 3)
    _STARTUP_LOADED = True


def create_app_state_for_tests() -> dict[str, Any]:
    init_startup_globals()
    data_loader = get_global_data_loader()
    knowledge_index = get_global_knowledge_index()
    azure_config = load_azure_config()
    grounding_adapter = GroundingAdapter(azure_config, data_loader, knowledge_index)
    iq_provider = build_iq_provider(azure_config, grounding_adapter, knowledge_index)
    scoring_service = ScoringService()
    openai_client = AzureOpenAIClient(azure_config)
    direct_openai_client = OpenAIClient()
    foundry_openai_client = FoundryOpenAIClient(
        base_url=settings.FOUNDRY_OPENAI_BASE_URL,
        api_key=settings.FOUNDRY_API_KEY,
        deployment=settings.FOUNDRY_MODEL_DEPLOYMENT,
    )
    foundry_agent_client = FoundryAgentClient(
        project_endpoint=settings.FOUNDRY_PROJECT_ENDPOINT,
        agent_name=settings.FOUNDRY_AGENT_NAME,
        agent_version=settings.FOUNDRY_AGENT_VERSION,
        api_key=settings.FOUNDRY_API_KEY,
    )
    llm_reasoning_provider = LLMReasoningProvider(
        azure_openai_client=openai_client,
        openai_client=direct_openai_client,
        foundry_openai_client=foundry_openai_client,
        foundry_agent_client=foundry_agent_client,
    )
    active_llm_provider = llm_reasoning_provider._select_client()[1]
    
    state = {
        "data_loader": data_loader,
        "knowledge_index": knowledge_index,
        "azure_config": azure_config,
        "grounding_adapter": grounding_adapter,
        "iq_provider": iq_provider,
        "scoring_service": scoring_service,
        "orchestrator": None,
        "report_service": ReportService(Path(settings.REPORT_OUTPUT_DIR)),
        "openai_client": openai_client,
        "direct_openai_client": direct_openai_client,
        "foundry_openai_client": foundry_openai_client,
        "foundry_agent_client": foundry_agent_client,
        "llm_reasoning_provider": llm_reasoning_provider,
        "model_provider": settings.MODEL_PROVIDER,
        "active_llm_provider": active_llm_provider,
        "experiment_store": ExperimentStore(data_loader),
        "demo_cache": DemoCache(),
        "uploaded_experiments": {}, # Mirror for backward compatibility
        "trace_timeline": {},
        "startup_loaded": _STARTUP_LOADED,
        "startup_duration_ms": _STARTUP_DURATION_MS,
        "settings": settings,
    }
    
    global _GLOBAL_ORCHESTRATOR
    if _GLOBAL_ORCHESTRATOR is None:
        _GLOBAL_ORCHESTRATOR = Orchestrator(state)
    state["orchestrator"] = _GLOBAL_ORCHESTRATOR
    # The orchestrator is a process-wide singleton, so on later create_app() calls its
    # iq_provider differs from the freshly-built one above. Share the orchestrator's
    # instance so health, iq_status, and demo metrics all read the same retrieval counter
    # that the agents actually incremented during a run.
    state["iq_provider"] = _GLOBAL_ORCHESTRATOR.iq_provider
    
    # Link back to maintain compatibility with test suites modifying app.state.uploaded_experiments directly
    state["uploaded_experiments"] = state["experiment_store"]._cache
    
    return state


def create_app() -> FastAPI:
    # Check if auth enabled but API_KEY missing (critical requirement 4)
    if settings.ENABLE_AUTH and not settings.API_KEY:
        raise ValueError("Authentication is enabled (ENABLE_AUTH=True), but API_KEY is not configured.")

    # Validate CORS in production
    cors_origins = settings.CORS_ORIGINS
    if settings.APP_MODE == "production":
        if settings.CORS_ALLOW_CREDENTIALS and ("*" in cors_origins or any(o == "*" for o in cors_origins)):
            raise ValueError("CORS configuration is unsafe: Wildcard '*' origins are not allowed with allow_credentials=True in production mode.")

    # Validate required credentials for production mode
    foundry_model_configured = bool(
        (settings.FOUNDRY_PROJECT_ENDPOINT or settings.FOUNDRY_OPENAI_BASE_URL)
        and settings.FOUNDRY_API_KEY
        and settings.FOUNDRY_MODEL_DEPLOYMENT
    )
    foundry_agent_configured = bool(
        settings.FOUNDRY_PROJECT_ENDPOINT
        and settings.FOUNDRY_AGENT_NAME
    )
    search_configured = bool(
        settings.AZURE_AI_SEARCH_ENDPOINT
        and settings.AZURE_AI_SEARCH_KEY
    )
    blob_configured = bool(
        settings.AZURE_STORAGE_CONNECTION_STRING
        and settings.AZURE_BLOB_CONTAINER
    )
    cosmos_configured = bool(
        settings.AZURE_COSMOS_ENDPOINT
        and settings.AZURE_COSMOS_KEY
        and settings.AZURE_COSMOS_DATABASE
        and settings.AZURE_COSMOS_CONTAINER
    )

    if settings.APP_MODE == "production":
        # Fail fast if required live Microsoft IQ credentials are missing (specifically search and model provider keys)
        if not search_configured:
            raise ValueError("Production mode requires Azure AI Search credentials (AZURE_AI_SEARCH_ENDPOINT and AZURE_AI_SEARCH_KEY).")
        
        if settings.MODEL_PROVIDER == "azure_openai":
            if not (settings.AZURE_OPENAI_ENDPOINT and settings.AZURE_OPENAI_API_KEY and settings.AZURE_OPENAI_DEPLOYMENT):
                raise ValueError("Azure OpenAI credentials are required when MODEL_PROVIDER is 'azure_openai'.")
        elif settings.MODEL_PROVIDER == "foundry_openai":
            if not foundry_model_configured:
                raise ValueError("Foundry OpenAI credentials (endpoint/base URL, api key, and deployment) are required when MODEL_PROVIDER is 'foundry_openai'.")
        elif settings.MODEL_PROVIDER == "foundry_agent":
            if not foundry_agent_configured:
                raise ValueError("Foundry Agent credentials (project endpoint and agent name) are required when MODEL_PROVIDER is 'foundry_agent'.")

    # Clear startup status logging
    active_reasoning = settings.MODEL_PROVIDER
    active_grounding = "azure_ai_search" if search_configured else "local_iq"
    
    logger.info("=== FailureLens IQ Startup Status ===")
    logger.info(f"Foundry model configured: {'Yes' if foundry_model_configured else 'No'}")
    logger.info(f"Foundry agent configured: {'Yes' if foundry_agent_configured else 'No'}")
    logger.info(f"Azure AI Search configured: {'Yes' if search_configured else 'No'}")
    logger.info(f"Blob configured: {'Yes' if blob_configured else 'No'}")
    logger.info(f"Cosmos configured: {'Yes' if cosmos_configured else 'No'}")
    logger.info(f"Active reasoning provider: {active_reasoning}")
    logger.info(f"Active IQ grounding provider: {active_grounding}")
    logger.info("=====================================")

    app = FastAPI(title="FailureLens IQ", version="1.0.0")

    # Add Middlewares (order matters: request flows from top to bottom, response from bottom to top)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(MaxBodySizeMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(StructuredLoggingMiddleware)

    # Initialize app state
    state = create_app_state_for_tests()
    for key, value in state.items():
        setattr(app.state, key, value)

    # Exception Handlers
    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "error": "invalid_experiment_payload",
                "details": exc.errors()
            }
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "http_error",
                "detail": exc.detail
            }
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "detail": "An unexpected error occurred. Please contact the administrator."
            }
        )

    # Register Routers
    app.include_router(health_router)
    app.include_router(readiness_router)
    app.include_router(cost_router)
    app.include_router(iq_status_router)
    app.include_router(agents_router)
    app.include_router(experiments_router)
    app.include_router(analysis_router)
    app.include_router(demo_router)
    app.include_router(knowledge_router)
    app.include_router(manager_router)
    app.include_router(report_router)
    from backend.api.routes.prompt_analysis import router as prompt_analysis_router
    app.include_router(prompt_analysis_router)
    app.include_router(proof_router)

    return app


app = create_app()
