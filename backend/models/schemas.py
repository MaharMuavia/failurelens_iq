from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator, model_validator

from backend.models.enums import (
    AgentName,
    AgentStatus,
    EvidenceStrength,
    FailureCategory,
    PlanType,
    RetrievalMode,
    VulnerabilityLevel,
)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class ExperimentLog(StrictModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True, protected_namespaces=())
    experiment_id: str = Field(..., max_length=100)
    team_id: str = Field(..., max_length=100)
    project_name: str = Field(..., max_length=200)
    role: str = Field(..., max_length=100)
    model_type: str = Field(..., max_length=100)
    dataset_name: str = Field(..., max_length=200)
    pipeline_stage: str = Field(..., max_length=100)
    target: str = Field(..., max_length=100)
    validation_strategy: str = Field(..., max_length=200)
    class_balance: str = Field(..., max_length=100)
    preprocessing_steps: list[str] = Field(default_factory=list)
    feature_set: list[str] = Field(default_factory=list)
    metrics: dict[str, float] = Field(default_factory=dict)
    baseline_metrics: dict[str, float] = Field(default_factory=dict)
    error_logs: list[str] = Field(default_factory=list)
    drift_indicators: list[str] = Field(default_factory=list)
    data_quality_signals: list[str] = Field(default_factory=list)
    training_config: dict[str, Any] = Field(default_factory=dict)
    deployment_context: dict[str, Any] = Field(default_factory=dict)
    failure_symptoms: list[str] = Field(default_factory=list)
    failure_observation: str = Field(..., max_length=5000)
    suspected_leakage_columns: list[str] = Field(default_factory=list)
    engineer_notes: str = Field(default="", max_length=5000)
    current_certifications: list[str] = Field(default_factory=list)
    outcome: str = Field(..., max_length=50)
    failure_category_label: str | None = Field(default=None, max_length=100)
    timestamp: datetime

    @field_validator("outcome")
    @classmethod
    def validate_outcome(cls, value: str) -> str:
        allowed = {"failure", "success", "partial", "unknown"}
        if value not in allowed:
            raise ValueError(f"outcome must be one of {sorted(allowed)}")
        return value

    @field_validator("metrics", "baseline_metrics")
    @classmethod
    def validate_numeric_metrics(cls, value: dict[str, float]) -> dict[str, float]:
        for key, metric in value.items():
            if not isinstance(metric, (int, float)):
                raise ValueError(f"{key} must be numeric")
            value[key] = float(metric)
        return value

    @computed_field
    @property
    def minority_pct(self) -> float:
        try:
            parts = [float(part.strip()) for part in self.class_balance.split("/")]
        except ValueError:
            return 0.0
        return min(parts) if parts else 0.0

    @computed_field
    @property
    def minority_f1(self) -> float:
        return float(self.metrics.get("minority_f1") or self.metrics.get("f1_minority") or 0.0)

    @computed_field
    @property
    def reported_metric(self) -> str:
        if "accuracy" in self.metrics:
            return "accuracy"
        return next(iter(self.metrics), "")

    @computed_field
    @property
    def metric_degradation_score(self) -> float:
        degradations: list[float] = []
        for key, baseline in self.baseline_metrics.items():
            if key not in self.metrics or baseline <= 0:
                continue
            degradations.append((baseline - self.metrics[key]) / baseline)
        return clamp(max(degradations, default=0.0))

    @computed_field
    @property
    def has_error_logs(self) -> bool:
        return bool(self.error_logs)

    @computed_field
    @property
    def has_drift_indicators(self) -> bool:
        return bool(self.drift_indicators)

    @computed_field
    @property
    def has_leakage_signal(self) -> bool:
        text = f"{self.failure_observation} {self.engineer_notes}".lower()
        return bool(self.suspected_leakage_columns) or "leakage" in text

    @computed_field
    @property
    def has_bias_language(self) -> bool:
        text = f"{self.failure_observation} {self.engineer_notes}".lower()
        terms = ["bias", "fairness", "protected", "demographic", "disparate", "discrimination"]
        return any(term in text for term in terms)


class KnowledgeHit(StrictModel):
    source_file: str
    section_title: str
    relevance_score: float
    excerpt: str
    matched_terms: list[str]
    citation: str
    retrieval_mode: RetrievalMode = RetrievalMode.LOCAL

    @field_validator("relevance_score")
    @classmethod
    def unit_score(cls, value: float) -> float:
        if not 0.0 <= value <= 1.0:
            raise ValueError("score must be 0.0-1.0")
        return value

    @field_validator("excerpt")
    @classmethod
    def short_excerpt(cls, value: str) -> str:
        return value[:400]


class RetrievalResult(StrictModel):
    query: str
    hits: list[KnowledgeHit] = Field(default_factory=list)
    top_relevance: float = 0.0
    retrieval_mode: RetrievalMode = RetrievalMode.LOCAL
    retrieved_at: datetime = Field(default_factory=now_utc)

    @model_validator(mode="after")
    def sync_top_relevance(self) -> RetrievalResult:
        expected = self.hits[0].relevance_score if self.hits else 0.0
        object.__setattr__(self, "top_relevance", expected)
        return self


class IQSearchResult(StrictModel):
    source: str
    source_file: str
    section_heading: str
    excerpt: str
    relevance_score: float
    matched_terms: list[str] = Field(default_factory=list)
    citation: str
    grounding_confidence: float


class GroundingResult(StrictModel):
    claim: str
    supported: bool
    grounding_confidence: float
    supporting_evidence: list[str] = Field(default_factory=list)
    source: str = "foundry_iq_local_adapter"


class CertSkillMapping(StrictModel):
    failure_category: str
    cert_code: str
    skill_domain: str
    source: str
    grounding_confidence: float
    relevant_excerpt: str


class IQGrounding(StrictModel):
    sources_consulted: list[str] = Field(default_factory=list)
    grounding_confidence: float = 0.0
    relevant_excerpts: list[str] = Field(default_factory=list)
    iq_layer: str = "foundry_iq"
    retrieval_method: str = "none"


class SimilarExperiment(StrictModel):
    experiment_id: str
    team_id: str
    similarity_score: float
    shared_signals: list[str]
    outcome_note: str
    days_ago: int


class FailureHypothesis(StrictModel):
    suspected_category: FailureCategory = FailureCategory.UNKNOWN
    alternative_categories: list[FailureCategory] = Field(default_factory=list)
    hypothesis_statement: str = "No hypothesis has been created yet."
    key_signals: list[str] = Field(default_factory=list)
    confidence_estimate: float = 0.0


class ExecutionPlan(StrictModel):
    planned_agents: list[AgentName] = Field(default_factory=list)
    dynamic_threshold: float = 0.45
    requires_human_review_flag: bool = False
    data_completeness: float = 0.0
    planning_reasoning: list[str] = Field(default_factory=list)
    similar_experiments: list[SimilarExperiment] = Field(default_factory=list)
    team_skill_context: dict[str, Any] = Field(default_factory=dict)


class PlannerContext(StrictModel):
    hypothesis: FailureHypothesis = Field(default_factory=FailureHypothesis)
    plan: ExecutionPlan = Field(default_factory=ExecutionPlan)
    planned_at: datetime = Field(default_factory=now_utc)


class EvidenceRef(StrictModel):
    source_type: Literal[
        "experiment_metric",
        "experiment_log",
        "historical_experiment",
        "local_demo_grounding",
        "azure_ai_search",
        "azure_blob_artifact",
        "cosmos_trace",
    ]
    source_id: str
    field_path: str
    value: Any
    interpretation: str
    confidence: float


class GroundingRef(StrictModel):
    source_type: Literal[
        "local_demo_grounding",
        "azure_ai_search",
        "azure_blob_artifact",
        "cosmos_trace",
    ]
    source_id: str
    title: str
    excerpt: str
    citation: str
    confidence: float = 0.0
    url: str | None = None
    source_system: str | None = None
    retrieved_at: datetime | None = None
    chunk_id: str | None = None
    iq_layer: str | None = None
    retrieval_system: str | None = None
    grounding_mode: Literal["demo", "production"] | None = None


class ReasoningStep(StrictModel):
    step_number: int
    thought_type: Literal[
        "observation",
        "hypothesis",
        "evidence_check",
        "inference",
        "counter_evidence",
        "uncertainty_check",
        "decision",
        "next_action",
    ] = "inference"
    description: str
    evidence: list[EvidenceRef] = Field(default_factory=list)
    finding: str
    confidence: float = 0.0
    evidence_fields: list[str] = Field(default_factory=list)
    confidence_delta: float = 0.0
    uncertainty: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    next_action: str | None = None


class AuditEntry(StrictModel):
    agent: AgentName
    action: str
    input_summary: str
    output_summary: str
    timestamp: datetime = Field(default_factory=now_utc)
    duration_ms: float = 0.0


class AgentTraceEntry(StrictModel):
    agent: AgentName
    agent_name: str = ""
    role: str = ""
    input_summary: str = ""
    status: AgentStatus = AgentStatus.PENDING
    started_at: datetime = Field(default_factory=now_utc)
    completed_at: datetime | None = None
    duration_ms: float | None = None
    reasoning_steps: list[ReasoningStep] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)
    uncertainty: list[str] = Field(default_factory=list)
    key_evidence: list[str] = Field(default_factory=list)
    counter_evidence: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    confidence_score: float = 0.0
    confidence_factors: dict[str, float] = Field(default_factory=dict)
    grounding_citations: list[str] = Field(default_factory=list)
    grounding_citation_ids: list[str] = Field(default_factory=list)
    grounding_refs: list[str] = Field(default_factory=list)
    iq_grounding: IQGrounding = Field(default_factory=IQGrounding)
    recommended_next_actions: list[str] = Field(default_factory=list)
    citation_ids: list[str] = Field(default_factory=list)
    evidence_used: list[str] = Field(default_factory=list)
    next_action: list[str] = Field(default_factory=list)
    grounding_source: str = ""
    audit_entries: list[AuditEntry] = Field(default_factory=list)
    skip_reason: str | None = None
    parent_trace_id: str | None = None
    trace_id: str = Field(default_factory=lambda: str(uuid4()))


class HistoricalMemoryResult(StrictModel):
    similar_historical_experiments: list[SimilarExperiment] = Field(default_factory=list)
    repeated_patterns: list[str] = Field(default_factory=list)
    prior_fixes: list[str] = Field(default_factory=list)
    team_learning_gap: str = "No repeated learning gap has been identified yet."
    confidence: float = 0.0


class IntakeResult(StrictModel):
    completeness_score: float = 0.0
    missing_critical_fields: list[str] = Field(default_factory=list)
    detected_signals: list[str] = Field(default_factory=list)
    team_profile: dict[str, Any] = Field(default_factory=dict)
    work_context: dict[str, Any] = Field(default_factory=dict)
    validation_warnings: list[str] = Field(default_factory=list)
    confidence: float = 0.0


class RuleEvaluation(StrictModel):
    rule_name: str
    priority: int
    triggered: bool
    evidence: list[str] = Field(default_factory=list)
    confidence_contribution: float = 0.0


class ClassificationResult(StrictModel):
    failure_category: FailureCategory = FailureCategory.UNKNOWN
    rules_evaluated: list[RuleEvaluation] = Field(default_factory=list)
    conflicting_categories: list[FailureCategory] = Field(default_factory=list)
    conflict_resolution: str = "No classification has been evaluated yet."
    confidence: float = 0.0
    grounding_citations: list[str] = Field(default_factory=list)

    @field_validator("rules_evaluated")
    @classmethod
    def six_rules(cls, value: list[RuleEvaluation]) -> list[RuleEvaluation]:
        if value and len(value) != 6:
            raise ValueError("rules_evaluated must contain exactly 6 entries")
        return value


class DiagnosisResult(StrictModel):
    root_cause: str = "Diagnosis has not run yet."
    violated_assumption: str = "No violated assumption has been identified yet."
    knowledge_gap: str = "No knowledge gap has been identified yet."
    evidence: list[str] = Field(default_factory=list)
    counter_evidence: list[str] = Field(default_factory=list)
    hypothesis_conflict: bool = False
    reflection_notes: list[str] = Field(default_factory=list)
    iq_retrieval: RetrievalResult = Field(default_factory=lambda: RetrievalResult(query=""))
    confidence: float = 0.0
    evidence_strength: EvidenceStrength = EvidenceStrength.INSUFFICIENT
    requires_human_review: bool = False


class CertMappingResult(StrictModel):
    recommended_cert: str
    cert_code: str
    skill_domain: str
    already_held: bool = False
    fallback_cert: str | None = None
    fallback_reason: str | None = None
    learning_path: list[str] = Field(default_factory=list)
    fallback_used: bool = False
    grounding: list[str] = Field(default_factory=list)
    confidence: float = 0.0


class RemediationResult(StrictModel):
    plan_type: PlanType
    three_day_plan: list[str]
    seven_day_plan: list[str]
    hands_on_lab: str
    experiment_connection: str
    manager_note: str
    responsible_ai_note: str | None = None
    grounding_citations: list[str] = Field(default_factory=list)
    confidence: float = 0.0

    @field_validator("three_day_plan")
    @classmethod
    def three_items(cls, value: list[str]) -> list[str]:
        if len(value) != 3:
            raise ValueError("three_day_plan must contain exactly 3 items")
        return value

    @field_validator("seven_day_plan")
    @classmethod
    def seven_items(cls, value: list[str]) -> list[str]:
        if len(value) != 7:
            raise ValueError("seven_day_plan must contain exactly 7 items")
        return value


class PracticeQuestion(StrictModel):
    question_type: str
    question: str
    options: list[str]
    correct_answer: str
    explanation: str
    distractor_reasoning: str
    difficulty: str
    citation: str
    skill_domain: str
    experiment_connection: str

    @model_validator(mode="after")
    def validate_question(self) -> PracticeQuestion:
        if len(self.options) != 4:
            raise ValueError("PracticeQuestion requires exactly 4 options")
        if self.correct_answer not in self.options:
            raise ValueError("correct_answer must be one of options")
        return self


class AssessmentResult(StrictModel):
    questions: list[PracticeQuestion]
    target_cert: str
    skill_gaps_assessed: list[str]
    confidence: float = 0.0

    @field_validator("questions")
    @classmethod
    def four_questions(cls, value: list[PracticeQuestion]) -> list[PracticeQuestion]:
        if len(value) != 4:
            raise ValueError("AssessmentResult requires exactly 4 questions")
        return value


class TrendPoint(StrictModel):
    date: str
    failure_count: int
    categories: list[FailureCategory]


class RankedGap(StrictModel):
    knowledge_gap: str
    frequency: int
    related_cert: str
    urgency: str


class TeamInsights(StrictModel):
    team_id: str
    failure_count: int = 0
    failure_rate: float = 0.0
    failure_heatmap: dict[str, int] = Field(default_factory=dict)
    trend_30_days: list[TrendPoint] = Field(default_factory=list)
    recurring_pattern_alert: str | None = None
    vulnerability_level: VulnerabilityLevel = VulnerabilityLevel.LOW
    top_knowledge_gaps: list[RankedGap] = Field(default_factory=list)
    cert_relevance_scores: dict[str, float] = Field(default_factory=dict)
    recommended_action: str = "Continue collecting evidence and reviewing recurring team process gaps."
    learning_velocity: str = "stagnant"
    sprint_adjusted_plan: str = "Use the next sprint review to inspect repeated experiment failure signals."


class AgentContext(StrictModel):
    run_id: str = Field(default_factory=lambda: str(uuid4()))
    experiment: ExperimentLog
    planner_context: PlannerContext | None = None
    intake_result: IntakeResult | None = None
    classification: ClassificationResult | None = None
    diagnosis: DiagnosisResult | None = None
    historical_memory: HistoricalMemoryResult | None = None
    cert_mapping: CertMappingResult | None = None
    remediation: RemediationResult | None = None
    assessment: AssessmentResult | None = None
    team_insights: TeamInsights | None = None
    agent_trace: list[AgentTraceEntry] = Field(default_factory=list)
    audit_trail: list[AuditEntry] = Field(default_factory=list)
    overall_confidence: float = 0.0
    requires_human_review: bool = False
    human_review_reason: str | None = None
    gate_passed: bool = True
    gate_halt_reason: str | None = None
    started_at: datetime = Field(default_factory=now_utc)
    completed_at: datetime | None = None
    total_duration_ms: float | None = None
    responsible_ai_flagged: bool = False
