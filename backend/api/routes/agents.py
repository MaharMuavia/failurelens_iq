from __future__ import annotations

from typing import Any
from fastapi import APIRouter

router = APIRouter()

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

@router.get("/agents")
async def agents() -> list[dict[str, Any]]:
    return JUDGE_AGENTS
