# Foundry IQ Knowledge Sources

This document describes the six enterprise-grade knowledge sources integrated into FailureLens IQ. These sources are based on Microsoft best practices and are designed for grounding reasoning agents in local adapter mode or live Azure AI Search mode.

## Summary of Knowledge Sources

| File Name | Purpose | Key Metadata / Schema | Agent Usage |
| :--- | :--- | :--- | :--- |
| **`failure_taxonomy.md`** | Categorizes common ML failure modes and standard signals. | `id`, `title`, `source_type: failure_taxonomy`, `tags` | `ClassifierAgent` references this to tag the root-cause category of a failed run. |
| **`experiment_history.json`** | Contains 6 synthetic past experiment runs with failure metrics and logs. | `id`, `title`, `source_type: experiment_history`, `metrics`, `logs` | `RootCauseAnalyzerAgent` searches this for analogical reasoning and comparison. |
| **`remediation_playbooks.md`** | Actionable timelines and steps to mitigate diagnosed issues. | `id`, `title`, `source_type: remediation_playbooks`, `tags` | `PrescriptiveCoachAgent` uses it to formulate 3-day and 7-day technical action items. |
| **`microsoft_certification_mapping.md`** | Maps technical failures to Azure certifications and learning paths. | `id`, `title`, `source_type: certification_mapping`, `tags` | `CertificationEvaluatorAgent` recommends training modules (e.g. AI-900, AI-102) to bridge skill gaps. |
| **`responsible_ai_checklist.md`** | Policy checklists grounded in Microsoft's six RAI principles. | `id`, `title`, `source_type: responsible_ai`, `tags` | All agents consult this to ensure recommendation compliance and check for group fairness. |
| **`manager_governance.md`** | Defines escalation rules and a standard summary template for leadership. | `id`, `title`, `source_type: manager_governance`, `tags` | `IntegrationManagerAgent` uses it to compile executive summaries and escalate serious risks. |

---

## Detailed Agent Workflow Integration

### 1. Classification Phase (`ClassifierAgent`)
When an experiment fails (e.g. `EXP-1001`), the agent retrieves entries from `failure_taxonomy.md`. It evaluates the metrics (e.g., F1 minority vs. overall accuracy) against standard failure signals (such as "Evaluation Methodology Failure" or "Data Leakage") to label the root cause.

### 2. Diagnosis & Comparison Phase (`RootCauseAnalyzerAgent`)
Using the identified failure category, the agent retrieves historically failed experiments from `experiment_history.json`. By analyzing metric profiles (e.g. high train accuracy, low validation accuracy for overfitting) and preprocessing steps, it grounds its explanation in historical team experiences.

### 3. Mitigation Phase (`PrescriptiveCoachAgent` & `CertificationEvaluatorAgent`)
- The **PrescriptiveCoachAgent** retrieves steps from `remediation_playbooks.md` to construct a 3-day short-term fix plan and a 7-day long-term improvement plan.
- The **CertificationEvaluatorAgent** consults `microsoft_certification_mapping.md` to recommend relevant Azure learning paths (e.g., Azure AI Engineer - AI-102 or Azure AI Fundamentals - AI-900) to address the team's conceptual gaps.

### 4. Policy & Compliance Review (`ResponsibleAIAgent`)
Every recommendation is checked against the guidelines in `responsible_ai_checklist.md`. If sensitive demographic parameters are involved or subgroup performance falls below thresholds, a fairness warning is flagged.

### 5. Escalation & Reporting (`IntegrationManagerAgent`)
If the failure is repeated, indicates high regulatory risk, or involves severe fairness disparities, the agent uses `manager_governance.md` to raise a human-review flag and formats an executive summary for leadership.
