# FailureLens IQ - Architecture

## System Overview

FailureLens IQ is a multi-agent reasoning system for analyzing failed ML experiments. It diagnoses root causes, finds historical patterns, recommends fixes, and evaluates team maturity using structured reasoning traces and grounded knowledge retrieval.

```
User/Judge
  ↓
[FastAPI REST API]
  ↓
[Orchestration Service]
  ├→ [Planner] → Hypothesis formation
  ├→ [Intake Agent] → Data validation
  ├→ [Classifier Agent] → Failure categorization (6 rules)
  ├→ [Diagnostic Agent] → Root cause analysis + grounding
  ├→ [Confidence Gate] → Decision point
  ├→ [Cert Mapper Agent] → Learning path mapping
  ├→ [Remediation Agent] → Fix generation
  ├→ [Assessment Agent] → Team maturity scoring
  └→ [Manager Agent] → Team insights
  ↓
[Grounding Adapter]
  ├→ Demo Mode: Local JSON files
  └→ Production Mode: Azure AI Search/Cosmos
  ↓
[Enterprise Report]
  ├→ Executive Summary
  ├→ Engineer Action Plan
  ├→ Manager Insights
  ├→ Reasoning Timeline
  ├→ Certification Readiness
  └→ Audit Trail
```

## Core Capabilities

1. **Structured Reasoning Traces** - Every agent produces observations, hypotheses, evidence, and confidence scores
2. **Grounded Knowledge Retrieval** - Citations from local demo knowledge or Azure AI Search
3. **Confidence Gating** - Halts analysis when evidence insufficient (no fabrication)
4. **Enterprise Outputs** - Executive summaries, engineer action plans, certification readiness, audit trails
5. **Azure Integration Ready** - Demo mode works offline; production mode uses Azure AI Foundry services
6. **Multi-Stakeholder Reports** - Customized output for C-suite, engineers, managers, and training teams
