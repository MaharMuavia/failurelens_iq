from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

from backend.agents.assessment_agent import AssessmentAgent
from backend.agents.cert_mapper_agent import CertMapperAgent
from backend.agents.classifier_agent import ClassifierAgent
from backend.agents.diagnostic_agent import DiagnosticAgent
from backend.agents.historian_agent import ExperimentHistorianAgent
from backend.agents.intake_agent import IntakeAgent
from backend.agents.manager_agent import ManagerAgent
from backend.agents.remediation_agent import RemediationAgent
from backend.core.confidence_gate import ConfidenceGate
from backend.core.planner import Planner
from backend.models.enums import AgentName
from backend.models.schemas import AgentContext, ExperimentLog
from backend.services.knowledge_index import KnowledgeIndex
from backend.services.local_iq_provider import LocalIQProvider
from backend.services.scoring_service import ScoringService
from backend.utils.data_loader import DataLoader


class Orchestrator:
    def __init__(self, app_state: Any | None = None) -> None:
        state = app_state or {}
        getter = state.get if isinstance(state, dict) else lambda key, default=None: getattr(state, key, default)
        self.data_loader: DataLoader = getter("data_loader") or DataLoader()
        if not self.data_loader.experiments:
            self.data_loader.load_all()
        self.knowledge_index: KnowledgeIndex = getter("knowledge_index") or KnowledgeIndex(Path("knowledge/foundry_docs"))
        self.iq_provider: LocalIQProvider = getter("iq_provider") or LocalIQProvider(self.knowledge_index)
        self.scoring_service: ScoringService = getter("scoring_service") or ScoringService()
        self.planner = Planner()
        self.gate = ConfidenceGate()
        deps = {"iq_provider": self.iq_provider, "scoring_service": self.scoring_service, "data_loader": self.data_loader}
        self.intake = IntakeAgent(**deps)
        self.classifier = ClassifierAgent(**deps)
        self.diagnostic = DiagnosticAgent(**deps)
        self.historian = ExperimentHistorianAgent(**deps)
        self.cert_mapper = CertMapperAgent(**deps)
        self.remediation = RemediationAgent(**deps)
        self.assessment = AssessmentAgent(**deps)
        self.manager = ManagerAgent(**deps)

    async def run(self, experiment: ExperimentLog, emitter: asyncio.Queue | None = None) -> AgentContext:
        started = perf_counter()
        ctx = AgentContext(experiment=experiment, responsible_ai_flagged=experiment.has_bias_language)
        try:
            ctx.planner_context = await self.planner.plan(experiment, self.data_loader.experiments, self.data_loader)
            await self._emit(emitter, "pipeline_started", ctx, AgentName.PLANNER.value, {"hypothesis": ctx.planner_context.hypothesis.model_dump(mode="json")})
            for agent in [self.intake, self.classifier, self.diagnostic, self.historian]:
                await self._run_agent(agent, ctx, emitter)
            passed, reason = self.gate.evaluate(ctx)
            await self._emit(emitter, "confidence_gate", ctx, AgentName.CONFIDENCE_GATE.value, {"passed": passed, "reason": reason})
            if passed:
                for agent in [self.cert_mapper, self.remediation, self.assessment, self.manager]:
                    await self._run_agent(agent, ctx, emitter)
            else:
                for agent in [self.cert_mapper, self.remediation, self.assessment]:
                    trace = agent.skip_trace(ctx, reason or "Confidence gate halted downstream learning actions.")
                    await self._emit(emitter, "agent_skipped", ctx, agent.name.value, trace.model_dump(mode="json"))
                await self._run_agent(self.manager, ctx, emitter)
            confidences = [
                value
                for value in [
                    ctx.classification.confidence if ctx.classification else None,
                    ctx.diagnosis.confidence if ctx.diagnosis else None,
                    ctx.cert_mapping.confidence if ctx.cert_mapping else None,
                    ctx.remediation.confidence if ctx.remediation else None,
                    ctx.assessment.confidence if ctx.assessment else None,
                ]
                if value is not None
            ]
            ctx.overall_confidence = round(sum(confidences) / len(confidences), 4) if confidences else 0.0
            ctx.completed_at = datetime.now(timezone.utc)
            ctx.total_duration_ms = round((perf_counter() - started) * 1000, 3)
            await self._emit(emitter, "pipeline_completed", ctx, None, {"overall_confidence": ctx.overall_confidence, "agent_trace": len(ctx.agent_trace)})
            return ctx
        except Exception as exc:
            await self._emit(emitter, "pipeline_failed", ctx, None, {"error": str(exc)})
            raise

    async def _run_agent(self, agent: Any, ctx: AgentContext, emitter: asyncio.Queue | None) -> None:
        await self._emit(emitter, "agent_started", ctx, agent.name.value, {})
        before = len(ctx.agent_trace)
        await agent.run(ctx)
        trace = ctx.agent_trace[-1] if len(ctx.agent_trace) > before else None
        if trace:
            for step in trace.reasoning_steps:
                await self._emit(emitter, "agent_reasoning", ctx, agent.name.value, step.model_dump(mode="json"))
            await self._emit(emitter, "agent_completed", ctx, agent.name.value, trace.model_dump(mode="json"))

    async def _emit(self, emitter: asyncio.Queue | None, event: str, ctx: AgentContext, agent: str | None, data: dict[str, Any]) -> None:
        if emitter is None:
            return
        await emitter.put(
            {
                "event": event,
                "run_id": ctx.run_id,
                "agent": agent,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": data,
            }
        )
