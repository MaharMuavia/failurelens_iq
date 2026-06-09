from enum import Enum


class FailureCategory(str, Enum):
    DATA_LEAKAGE = "Data Leakage Failure"
    RESPONSIBLE_AI = "Responsible AI / Bias Failure"
    DEPLOYMENT_DRIFT = "Deployment / Drift Failure"
    EVALUATION_METHODOLOGY = "Evaluation Methodology Failure"
    FEATURE_ENGINEERING = "Feature Engineering Failure"
    DATA_QUALITY = "Data Quality Failure"
    UNKNOWN = "Unknown"


class AgentName(str, Enum):
    PLANNER = "Planner"
    INTAKE = "IntakeAgent"
    CLASSIFIER = "ClassifierAgent"
    DIAGNOSTIC = "DiagnosticAgent"
    CONFIDENCE_GATE = "ConfidenceGate"
    CERT_MAPPER = "CertMapperAgent"
    REMEDIATION = "RemediationAgent"
    ASSESSMENT = "AssessmentAgent"
    MANAGER = "ManagerAgent"


class AgentStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


class EvidenceStrength(str, Enum):
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    INSUFFICIENT = "insufficient"


class VulnerabilityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"


class PlanType(str, Enum):
    MICRO = "micro-learning"
    BALANCED = "balanced"
    IMMERSIVE = "immersive"


class RetrievalMode(str, Enum):
    LOCAL = "local_iq_simulation"
    AZURE = "azure_foundry_iq"
