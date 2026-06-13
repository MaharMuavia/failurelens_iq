from pydantic import BaseModel, ConfigDict, Field
from typing import List

class ReasoningStep(BaseModel):
    step: int = Field(..., description="Step number in the reasoning chain")
    observation: str = Field(..., description="Factual metric or note observed from the experiment")
    interpretation: str = Field(..., description="Reasoning or interpretation of the observation")

class UncertaintyBlock(BaseModel):
    level: str = Field(..., description="Level of uncertainty (e.g., Low, Medium, High)")
    missing_information: List[str] = Field(default_factory=list, description="Information missing from logs/metrics")
    alternative_explanations: List[str] = Field(default_factory=list, description="Other possible explanations for symptoms")

class CertificationGap(BaseModel):
    skill_gap: str = Field("", description="Identified technical skill or certification gap")
    recommended_learning: str = Field("", description="Recommended learning resources or courses")

class IQGrounding(BaseModel):
    knowledge_sources_used: List[str] = Field(default_factory=list, description="Specific knowledge base documents or patterns referenced")
    matched_failure_patterns: List[str] = Field(default_factory=list, description="Matching failure patterns found in grounding sources")
    grounding_confidence: int = Field(0, ge=0, le=100, description="Confidence score for IQ grounding match")

class AgentMetadata(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    call_mode: str = Field(..., description="Foundry call mode (agent, model, or mock)")
    agent_name: str = Field("", description="Name of the saved Azure Foundry agent")
    model_deployment: str = Field("", description="Azure Foundry model deployment name")
    schema_version: str = Field("1.0", description="Version of the JSON response schema")

class FailureAnalysisResponse(BaseModel):
    failure_type: str = Field(..., description="Diagnosed failure type (e.g. Overfitting)")
    severity: str = Field(..., description="Severity of the failure (e.g. Critical, High, Medium, Low)")
    confidence_score: int = Field(..., ge=0, le=100, description="Reasoning agent confidence score")
    reasoning_trace: List[ReasoningStep] = Field(default_factory=list, description="Structured chain of thought reasoning trace")
    evidence_used: List[str] = Field(default_factory=list, description="List of metric-driven/contextual evidence points")
    root_causes: List[str] = Field(default_factory=list, description="Identified root causes of the failure")
    uncertainty: UncertaintyBlock = Field(..., description="Uncertainty assessment")
    recommended_fixes: List[str] = Field(default_factory=list, description="Recommended fixes for the current failure")
    next_experiment_plan: List[str] = Field(default_factory=list, description="Iterative experimental plan for the next sprint")
    certification_gap: CertificationGap = Field(..., description="Identified skill gaps mapped to certifications")
    iq_grounding: IQGrounding = Field(..., description="Grounding info mapped to Microsoft IQ patterns")
    agent_metadata: AgentMetadata = Field(..., description="Metadata identifying the model/agent that produced the response")
    active_reasoning_provider: str = Field("deterministic_fallback", description="Provider actually used for root-cause reasoning")
    active_grounding_provider: str = Field("local_iq", description="Provider actually used for grounding in this response")
    proof_level: str = Field("local_foundry_iq_adapter", description="Honest proof level for this analysis run")
    live_microsoft_iq: bool = Field(False, description="True only when this run returned Azure AI Search grounding refs")
    azure_ai_search_used_this_run: bool = Field(False, description="Whether Azure AI Search returned real refs for this run")
    foundry_model_used_this_run: bool = Field(False, description="Whether Azure/Foundry model reasoning completed for this run")
    warnings: List[str] = Field(default_factory=list, description="Honesty warnings and fallback notices")
