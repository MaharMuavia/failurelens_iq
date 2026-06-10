from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.azure.config import load_azure_config
from backend.azure.grounding_adapter import GroundingAdapter
from backend.core.orchestrator import Orchestrator
from backend.models.enums import RetrievalMode
from backend.models.schemas import ExperimentLog
from backend.services.knowledge_index import KnowledgeIndex
from backend.services.local_iq_provider import LocalIQProvider
from backend.services.report_service import ReportService
from backend.services.scoring_service import ScoringService
from backend.utils.data_loader import DataLoader


class AnalysisOptions(BaseModel):
    include_reasoning_trace: bool = True
    include_grounding: bool = True
    include_certification: bool = True


class AnalysisRunRequest(BaseModel):
    experiment_id: str
    options: AnalysisOptions = Field(default_factory=AnalysisOptions)


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


def create_app_state_for_tests() -> dict[str, Any]:
    data_loader = DataLoader()
    data_loader.load_all()
    knowledge_index = KnowledgeIndex(Path("knowledge/foundry_docs"))
    azure_config = load_azure_config()
    iq_provider = LocalIQProvider(knowledge_index)
    scoring_service = ScoringService()
    state = {
        "data_loader": data_loader,
        "knowledge_index": knowledge_index,
        "azure_config": azure_config,
        "grounding_adapter": GroundingAdapter(azure_config, data_loader, knowledge_index),
        "iq_provider": iq_provider,
        "scoring_service": scoring_service,
        "orchestrator": None,
        "report_service": ReportService(Path("reports")),
    }
    state["orchestrator"] = Orchestrator(state)
    return state


def create_app() -> FastAPI:
    app = FastAPI(title="FailureLens IQ", version="1.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    state = create_app_state_for_tests()
    for key, value in state.items():
        setattr(app.state, key, value)

    def loader() -> DataLoader:
        return app.state.data_loader

    def orchestrator() -> Orchestrator:
        return app.state.orchestrator

    async def analyze_experiment(experiment_id: str) -> Any:
        try:
            exp = loader().get_experiment(experiment_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return await orchestrator().run(exp)

    @app.get("/health")
    async def health() -> dict[str, object]:
        return {
            "status": "ok",
            "app_mode": app.state.azure_config.app_mode,
            "version": "1.0.0",
            "experiments_loaded": len(loader().experiments),
            "knowledge_chunks_indexed": len(app.state.knowledge_index.chunks),
            "enabled_integrations": app.state.azure_config.enabled_integrations,
            "demo_ready": True,
        }

    @app.get("/agents")
    async def agents() -> list[dict[str, Any]]:
        return JUDGE_AGENTS

    @app.get("/experiments")
    async def list_experiments(
        page: int = 1,
        limit: int = 25,
        team_id: str | None = None,
        outcome: str | None = None,
        failure_category: str | None = None,
    ) -> dict[str, Any]:
        items = loader().experiments
        if team_id:
            items = [item for item in items if item.team_id == team_id]
        if outcome:
            items = [item for item in items if item.outcome == outcome]
        if failure_category:
            items = [item for item in items if (item.failure_category_label or "") == failure_category]
        start = max(page - 1, 0) * limit
        page_items = items[start : start + limit]
        return {"total": len(items), "page": page, "limit": limit, "items": [item.model_dump(mode="json") for item in page_items]}

    @app.get("/experiments/{experiment_id}")
    async def get_experiment(experiment_id: str) -> dict[str, Any]:
        try:
            return loader().get_experiment(experiment_id).model_dump(mode="json")
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.post("/analysis/run/{experiment_id}")
    async def run_analysis(experiment_id: str) -> dict[str, Any]:
        ctx = await analyze_experiment(experiment_id)
        return ctx.model_dump(mode="json")

    @app.post("/analysis/run")
    async def run_analysis_body(payload: AnalysisRunRequest) -> dict[str, Any]:
        ctx = await analyze_experiment(payload.experiment_id)
        result = ctx.model_dump(mode="json")
        if payload.options.include_grounding:
            refs = await app.state.grounding_adapter.retrieve_experiment_context(payload.experiment_id)
            result["grounding_summary"] = await app.state.grounding_adapter.build_grounding_summary(refs)
        return result

    @app.post("/demo/run")
    async def run_demo() -> dict[str, Any]:
        ctx = await analyze_experiment("EXP-1001")
        refs = []
        refs.extend(await app.state.grounding_adapter.retrieve_experiment_context("EXP-1001"))
        refs.extend(await app.state.grounding_adapter.retrieve_historical_failures(ctx.diagnosis.knowledge_gap if ctx.diagnosis else "ml failure", top_k=5))
        grounding_summary = await app.state.grounding_adapter.build_grounding_summary(refs)
        store_result = await app.state.grounding_adapter.store_reasoning_trace(ctx.run_id, ctx.model_dump(mode="json"))
        return build_demo_response(ctx, grounding_summary, store_result)

    @app.post("/experiments/upload")
    async def upload_experiment(payload: ExperimentLog) -> dict[str, Any]:
        return {
            "status": "validated",
            "message": "Experiment JSON passed Pydantic validation. It can be submitted to /analysis/custom or /analysis/run after persistence is added.",
            "experiment": payload.model_dump(mode="json"),
        }

    @app.get("/analysis/stream/{experiment_id}")
    async def stream_analysis(experiment_id: str) -> StreamingResponse:
        try:
            exp = loader().get_experiment(experiment_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        queue: asyncio.Queue = asyncio.Queue()

        async def runner() -> None:
            await orchestrator().run(exp, queue)

        async def events():
            task = asyncio.create_task(runner())
            try:
                while True:
                    event = await queue.get()
                    yield f"data: {json.dumps(event)}\n\n"
                    if event["event"] in {"pipeline_completed", "pipeline_failed"}:
                        break
            finally:
                await task

        return StreamingResponse(events(), media_type="text/event-stream")

    @app.post("/analysis/custom")
    async def custom_analysis(payload: dict[str, Any]) -> dict[str, Any]:
        exp = ExperimentLog.model_validate(payload)
        ctx = await orchestrator().run(exp)
        return ctx.model_dump(mode="json")

    @app.get("/manager/team/{team_id}")
    async def manager_team(team_id: str) -> dict[str, Any]:
        experiments = loader().experiments_for_team(team_id)
        if not experiments:
            raise HTTPException(status_code=404, detail=f"Unknown team_id: {team_id}")
        ctx = await orchestrator().run(experiments[-1])
        return ctx.team_insights.model_dump(mode="json") if ctx.team_insights else {}

    @app.get("/manager/all")
    async def manager_all() -> dict[str, Any]:
        result = {}
        for team_id in sorted(loader().team_profiles):
            experiments = loader().experiments_for_team(team_id)
            ctx = await orchestrator().run(experiments[-1])
            result[team_id] = ctx.team_insights.model_dump(mode="json") if ctx.team_insights else {}
        return result

    @app.get("/knowledge/search")
    async def knowledge_search(
        q: str = Query(..., min_length=1),
        top_k: int = 3,
        cert_filter: str | None = None,
    ) -> dict[str, Any]:
        retrieval = await app.state.iq_provider.retrieve(q, top_k=top_k, cert_filter=cert_filter)
        return retrieval.model_dump(mode="json")

    @app.get("/knowledge/sources")
    async def knowledge_sources() -> list[dict[str, object]]:
        return app.state.knowledge_index.sources()

    @app.post("/report/{experiment_id}/generate")
    async def generate_report(experiment_id: str) -> dict[str, Any]:
        try:
            exp = loader().get_experiment(experiment_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        ctx = await orchestrator().run(exp)
        path = app.state.report_service.generate(ctx)
        return {"experiment_id": experiment_id, "path": str(path), "bytes": path.stat().st_size}

    @app.get("/report/{experiment_id}")
    async def get_report(experiment_id: str) -> dict[str, Any]:
        path = Path("reports") / f"{experiment_id}.md"
        if not path.exists():
            raise HTTPException(status_code=404, detail="Report has not been generated yet.")
        return {"experiment_id": experiment_id, "path": str(path), "content": path.read_text(encoding="utf-8")}

    return app


def build_demo_response(ctx: Any, grounding_summary: dict[str, Any], store_result: dict[str, Any]) -> dict[str, Any]:
    exp = ctx.experiment
    classification = ctx.classification.model_dump(mode="json") if ctx.classification else {}
    diagnosis = ctx.diagnosis.model_dump(mode="json") if ctx.diagnosis else {}
    historical = ctx.historical_memory.model_dump(mode="json") if ctx.historical_memory else {}
    remediation = ctx.remediation.model_dump(mode="json") if ctx.remediation else {}
    cert_ready = {
        "mapping": ctx.cert_mapping.model_dump(mode="json") if ctx.cert_mapping else {},
        "assessment": ctx.assessment.model_dump(mode="json") if ctx.assessment else {},
    }
    traces = [trace.model_dump(mode="json") for trace in ctx.agent_trace]
    return {
        "demo_title": "Customer churn model failed validation gate",
        "executive_summary": (
            f"{exp.experiment_id} failed because {diagnosis.get('root_cause', 'the root cause needs review')} "
            f"The agents classified it as {classification.get('failure_category', 'Unknown')} with overall confidence {ctx.overall_confidence:.2f}."
        ),
        "agent_workflow": [
            {
                "agent_name": trace["agent_name"],
                "role": trace["role"],
                "status": trace["status"],
                "confidence_score": trace["confidence_score"],
                "findings": trace["findings"][:2],
                "recommended_next_actions": trace["recommended_next_actions"],
            }
            for trace in traces
        ],
        "failure_classification": classification,
        "root_cause_analysis": diagnosis,
        "historical_memory": historical,
        "remediation_plan": remediation,
        "certification_readiness": cert_ready,
        "reasoning_timeline": traces,
        "grounding_summary": grounding_summary,
        "confidence_summary": {
            "overall_confidence": ctx.overall_confidence,
            "requires_human_review": ctx.requires_human_review,
            "gate_passed": ctx.gate_passed,
            "human_review_reason": ctx.human_review_reason,
        },
        "manager_summary": ctx.team_insights.model_dump(mode="json") if ctx.team_insights else {},
        "trace_storage": store_result,
        "judge_notes": {
            "why_agents_are_needed": "The workflow separates classification, diagnosis, historical memory, remediation, certification readiness, and manager synthesis so each step can expose evidence, uncertainty, and audit entries.",
            "where_microsoft_iq_is_used": grounding_summary.get("message", "Demo mode uses local grounding; Azure adapters activate only when credentials are configured."),
            "why_this_is_enterprise": "The response includes confidence gates, human-review flags, grounding citations, manager rollups, and trace storage boundaries for Azure Cosmos DB.",
        },
    }


app = create_app()
