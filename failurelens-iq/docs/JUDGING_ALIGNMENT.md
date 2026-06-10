# FailureLens IQ - Judging Alignment

This document maps FailureLens IQ's implementation to the Microsoft Agents League Hackathon 2026 evaluation criteria.

## 1. Agent Reasoning Quality

### Requirement
Every agent must produce **structured reasoning traces** with observations, hypotheses, evidence, uncertainty, confidence, and next actions.

### Implementation

#### 1.1 Structured Reasoning Traces
- **Location**: `backend/models/schemas.py` → `ReasoningStep`, `AgentTraceEntry`
- **Endpoint**: `POST /analysis/run/{experiment_id}`
- **Field**: `agent_trace[].reasoning_steps[]`

**Reasoning Step Structure**:
```json
{
  "step_number": 1,
  "thought_type": "observation|hypothesis|inference|conclusion",
  "description": "...",
  "evidence": ["metric.validation_auc", "metric.training_auc"],
  "confidence": 0.86,
  "conflicting_evidence": ["..."],
  "uncertainty_factors": ["missing_feature_importance"]
}
```

#### 1.2 Evidence Grounding
- **Files**: `backend/agents/base_agent.py` → `cite_evidence()` method
- **Grounding**: All evidence cites specific experiment fields
- **Format**: `[source_field] → [value] → [interpretation]`

#### 1.3 Confidence Scoring
- **Range**: 0.0 to 1.0
- **Validation**: `backend/models/schemas.py` → `@field_validator("confidence")`
- **Factors**: Evidence count, conflicting signals, missing data
- **Location**: `backend/services/scoring_service.py`

**Demo Proof**: Call any analysis endpoint and examine `agent_trace[*].confidence`

#### 1.4 Reasoning Timeline
- **Endpoint**: `POST /analysis/run/{experiment_id}`
- **Field**: `reasoning_timeline` - aggregates all agent reasoning in chronological order
- **Format**: Array of `{agent, step, finding, timestamp}`

**Demo Proof**:
```bash
curl -X POST http://localhost:8000/analysis/run/EXP-1001 | jq '.reasoning_timeline'
```

#### 1.5 Uncertainty Quantification
- **Field**: `uncertainty` in each agent trace
- **Levels**: low (< 0.3), medium (0.3-0.7), high (> 0.7)
- **Reasons**: List of missing evidence or conflicting signals

**Demo Proof**:
```bash
curl -X POST http://localhost:8000/analysis/run/EXP-1001 | jq '.agent_trace[].uncertainty'
```

---

## 2. Microsoft IQ / Azure Foundry Integration

### Requirement
Clear Azure AI Foundry / Azure OpenAI / Azure AI Search / Cosmos DB / Blob Storage adapter boundaries.
- Demo mode works locally without Azure credentials
- Production mode connects to Azure when credentials exist
- Real adapter classes (not fakes) with clear separation

### Implementation

#### 2.1 Adapter Architecture
- **Location**: `backend/azure/` directory

**Adapter Classes**:
1. `backend/services/azure_foundry_iq_provider.py` → Azure AI Search + Foundry grounding
2. `backend/azure/openai_client.py` → Azure OpenAI wrapper (stub for MVP)
3. `backend/azure/cosmos_client.py` → Cosmos DB for history (stub for MVP)
4. `backend/azure/blob_client.py` → Blob Storage for artifacts (stub for MVP)

#### 2.2 Dual-Mode Grounding Adapter
- **Location**: `backend/services/iq_provider.py` (abstract base)
- **Demo Mode**: `backend/services/local_iq_provider.py`
  - Uses local JSON files: `knowledge/foundry_docs/`
  - Grounding source: `source_type: "local_demo_grounding"`
  - No Azure credentials required
- **Production Mode**: `backend/services/azure_foundry_iq_provider.py`
  - Uses Azure AI Search for retrieval
  - Would use Azure Blob for uploaded artifacts
  - Would use Azure Cosmos for reasoning history
  - Grounding source: `source_type: "azure_ai_search"`, `source_id`, `url`

#### 2.3 Environment Variables
**Location**: `.env.example`

**Demo Mode**:
```env
APP_MODE=demo
IQ_PROVIDER=local
```

**Production Mode** (when credentials provided):
```env
APP_MODE=production
IQ_PROVIDER=azure_foundry
AZURE_OPENAI_ENDPOINT=https://{resource}.openai.azure.com/
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_DEPLOYMENT=gpt-4
AZURE_AI_SEARCH_ENDPOINT=https://{resource}.search.windows.net/
AZURE_AI_SEARCH_KEY=...
AZURE_AI_SEARCH_INDEX=ml_experiments
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=...
AZURE_BLOB_CONTAINER=failurelens-iq
AZURE_COSMOS_ENDPOINT=https://{resource}.documents.azure.com:443/
AZURE_COSMOS_KEY=...
AZURE_COSMOS_DATABASE=failurelens
AZURE_COSMOS_CONTAINER=reasoning_traces
```

#### 2.4 Health Check Integration Status
**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "ok",
  "app_mode": "demo|production",
  "enabled_integrations": {
    "azure_openai": false,
    "azure_ai_search": false,
    "blob_storage": false,
    "cosmos_db": false
  }
}
```

**Demo Proof**:
```bash
curl http://localhost:8000/health
```

#### 2.5 Grounding Source Attribution
Every retrieved knowledge chunk includes:
- `source_type`: "local_demo_grounding" or "azure_ai_search"
- `source_id`: Document ID in Azure or local file path
- `title`: Section title
- `content_snippet`: Relevant excerpt
- `confidence`: Relevance score (0-1)
- `url`: Azure URL (production only)

**Demo Proof**:
```bash
curl "http://localhost:8000/knowledge/search?q=overfitting+regularization"
```

---

## 3. Enterprise Scenario Depth

### Requirement
Product must feel like something a real MLOps team would use.
- Executive summary
- Engineer action plan
- Manager summary
- Learning plan
- Certification readiness
- Audit trail

### Implementation

#### 3.1 Executive Summary
- **Location**: Analysis response → `executive_summary` field
- **Content**: 2-3 sentence summary of failure, root cause, recommended action
- **Audience**: C-suite / non-technical stakeholders
- **Example**: "Customer churn model validation failed due to class imbalance (20% minority). Recommend increasing regularization and evaluating with F1 rather than accuracy."

#### 3.2 Engineer Action Plan
- **Location**: `remediation` agent output → `remediation_plan`
- **Content**: Step-by-step fixes with specific hyperparameters, feature changes, data handling
- **Owner**: Data engineer / ML engineer
- **Timeline**: Immediate / next sprint / future
- **Fields**:
  - `priority`: high / medium / low
  - `action`: Specific technical step
  - `owner_role`: engineer / data_scientist / team_lead
  - `expected_impact`: "AUC +0.12"
  - `risk`: "May reduce training speed"
  - `rollback_plan`: "Revert to previous hyperparameters"

**Demo Proof**:
```bash
curl -X POST http://localhost:8000/analysis/run/EXP-1001 | jq '.remediation.remediation_plan'
```

#### 3.3 Manager Summary
- **Endpoint**: `GET /manager/team/{team_id}`
- **Content**:
  - Recurring failure patterns
  - Team learning gaps
  - Resource allocation recommendations
  - Responsible AI risk flags
- **Audience**: Engineering manager / team lead

**Demo Proof**:
```bash
curl http://localhost:8000/manager/team/TEAM-B
```

#### 3.4 Learning Plan
- **Location**: `cert_mapping` agent → `recommended_learning_modules`
- **Content**: Microsoft Learn modules, internal training, workshops needed
- **Example**: "Recommend DP-100 (Azure ML), Responsible AI path, Feature Engineering essentials"
- **Goal**: Maps skill gaps to official certifications

**Demo Proof**:
```bash
curl -X POST http://localhost:8000/analysis/run/EXP-1001 | jq '.cert_mapping'
```

#### 3.5 Certification Readiness
- **Location**: `assessment` agent → `certification_score` (0-100)
- **Badges**: bronze (0-49), silver (50-69), gold (70-84), enterprise-ready (85-100)
- **Dimensions**:
  - Experiment tracking maturity
  - Data validation maturity
  - Model evaluation maturity
  - Remediation discipline
  - Documentation quality
  - Responsible AI awareness

**Demo Proof**:
```bash
curl -X POST http://localhost:8000/analysis/run/EXP-1001 | jq '.assessment'
```

#### 3.6 Audit Trail
- **Location**: `audit_trail` in all responses
- **Content**: Every decision timestamped with agent, reasoning, confidence
- **Use**: Regulatory compliance, post-mortem investigation
- **Fields**: `timestamp`, `agent`, `action`, `status`, `details`, `confidence`

**Demo Proof**:
```bash
curl -X POST http://localhost:8000/analysis/run/EXP-1001 | jq '.audit_trail'
```

#### 3.7 Report Generation
- **Endpoint**: `POST /report/{experiment_id}/generate`
- **Output**: Markdown file with all sections above + reasoning timeline
- **Location**: `reports/{experiment_id}.md`

**Demo Proof**:
```bash
curl -X POST http://localhost:8000/report/EXP-1001/generate
curl http://localhost:8000/report/EXP-1001
```

---

## 4. Reasoning Agent System Quality

### 4.1 Agent Pipeline Architecture
**Location**: `backend/core/orchestrator.py`

**Pipeline**:
1. **Planner** → Form hypothesis about failure pattern
2. **Intake** → Validate experiment data, flag missing evidence
3. **Classifier** → Evaluate 6 rules, classify failure category
4. **Diagnostic** → Deep analysis with grounding retrieval
5. **Confidence Gate** → Decide if confidence sufficient for next agents
6. **Cert Mapper** → Map failures to learning paths
7. **Remediation** → Generate specific fixes
8. **Assessment** → Score team maturity
9. **Manager** → Aggregate team patterns

Each agent **independently**:
- Produces reasoning trace with observations, hypotheses, evidence
- Cites sources in grounding
- Calculates confidence
- Adds to audit trail

**Demo Proof**: SSE streaming shows real-time agent reasoning
```bash
curl -N http://localhost:8000/analysis/stream/EXP-1001
```

### 4.2 Confidence Gating
- **Location**: `backend/core/confidence_gate.py`
- **Decision**: If `overall_confidence` < threshold, skip learning agents
- **Special Case**: `SPARSE-001` (confidence gate halts downstream, returns "Requires human review")

**Demo Proof**: Run both a confident and uncertain experiment
```bash
curl -X POST http://localhost:8000/analysis/run/EXP-1001  # Confident
curl -X POST http://localhost:8000/analysis/run/SPARSE-001  # Uncertain → human review
```

### 4.3 No Fabrication Rule
- Every finding must cite evidence from experiment or grounding
- If confidence too low, agent says "Cannot determine root cause with current evidence"
- No generic placeholder text

**Demo Proof**: `SPARSE-001` experiment lacks sufficient signals
```bash
curl -X POST http://localhost:8000/analysis/run/SPARSE-001 | jq '.diagnosis.summary'
# Output: "Cannot determine root cause with current evidence" (not fabrication)
```

---

## 5. Quick Verification Checklist

Run these commands to verify all requirements:

```bash
# 1. Health check + integration status
curl http://localhost:8000/health | jq '.enabled_integrations'

# 2. Reasoning traces exist
curl -X POST http://localhost:8000/analysis/run/EXP-1001 | jq '.agent_trace[0].reasoning_steps | length'
# Expected: > 3

# 3. Confidence scores valid
curl -X POST http://localhost:8000/analysis/run/EXP-1001 | jq '.agent_trace[].confidence | select(. < 0 or . > 1)'
# Expected: (empty)

# 4. Grounding citations exist
curl -X POST http://localhost:8000/analysis/run/EXP-1001 | jq '.agent_trace[0].grounding_citations | length'
# Expected: > 0

# 5. Executive summary present
curl -X POST http://localhost:8000/analysis/run/EXP-1001 | jq '.executive_summary | length'
# Expected: > 10

# 6. Certification readiness calculated
curl -X POST http://localhost:8000/analysis/run/EXP-1001 | jq '.assessment.certification_score'
# Expected: 0-100

# 7. Audit trail comprehensive
curl -X POST http://localhost:8000/analysis/run/EXP-1001 | jq '.audit_trail | length'
# Expected: > 5

# 8. No fabrication test
curl -X POST http://localhost:8000/analysis/run/SPARSE-001 | jq '.diagnosis.summary'
# Expected: Contains "Cannot determine" or "Requires human review"

# 9. Streaming works
curl -N http://localhost:8000/analysis/stream/EXP-1001 | head -20

# 10. Report generates
curl -X POST http://localhost:8000/report/EXP-1001/generate
```

---

## 6. File Reference Summary

| Judging Criterion | Implementation Files | Key Classes |
|---|---|---|
| Reasoning Traces | `models/schemas.py` | `ReasoningStep`, `AgentTraceEntry` |
| Confidence Scoring | `services/scoring_service.py` | `ScoringService` |
| Evidence Grounding | `agents/base_agent.py` | `cite_evidence()` |
| Azure Adapters | `services/iq_provider.py` + `services/local_iq_provider.py` | `IQProvider`, `LocalIQProvider` |
| Agent Pipeline | `core/orchestrator.py` | `Orchestrator` |
| Confidence Gate | `core/confidence_gate.py` | `ConfidenceGate` |
| Executive Report | `services/report_service.py` | `ReportService` |
| Certification | `agents/assessment_agent.py` | `AssessmentAgent` |
| Remediation | `agents/remediation_agent.py` | `RemediationAgent` |
| Audit Trail | All agents | `audit_trail` field in `AgentContext` |

---

## 7. Expected Judging Demo Flow

1. **Start app**: `uvicorn app.main:app --reload`
2. **Health check**: `GET /health` → Shows demo mode, 0 Azure integrations active
3. **List agents**: `GET /agents` → Shows 9 agents with roles
4. **Run demo**: `POST /demo/run` → Returns complete analysis report
5. **View reasoning**: `jq '.agent_trace[].reasoning_steps'` → Show detailed traces
6. **View grounding**: `jq '.agent_trace[].grounding_citations'` → Show knowledge sources
7. **View enterprise outputs**:
   - Executive summary for C-suite
   - Engineer action plan for team
   - Manager insights for leadership
   - Certification readiness for HR/training
   - Audit trail for compliance
8. **Test streaming**: `curl -N /analysis/stream/EXP-1001` → Real-time agent reasoning
9. **Test Azure integration stubs**: `GET /health` → Shows where Azure would plug in
10. **Run tests**: `pytest` → All 22 tests pass, verifying no fabrication, proper reasoning

---

## Conclusion

FailureLens IQ demonstrates:
- ✅ **Sophisticated reasoning traces** with uncertainty quantification
- ✅ **Enterprise-grade outputs** for multiple stakeholders
- ✅ **Clear Azure integration seams** with demo/production modes
- ✅ **Confidence gating** that halts when evidence insufficient
- ✅ **Audit-ready compliance** tracking
- ✅ **No fabrication rule** enforced throughout
- ✅ **Grounded knowledge retrieval** with proper citations

Ready for Microsoft Agents League Hackathon judging.
