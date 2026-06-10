# Pitch

## 2-Minute Script

FailureLens IQ is learning intelligence for failed ML experiments.

Most MLOps tools track successful runs, but the failed runs contain the lessons teams keep repeating. In this demo, a customer churn model failed its validation gate because headline accuracy hid weak minority-class performance.

FailureLens IQ sends the experiment through six reasoning agents. The classifier identifies the failure category. The root-cause analyzer explains the violated assumption with evidence and uncertainty. The historian finds similar failed runs so the team does not treat this as a one-off. The coach creates a remediation plan. The certification evaluator maps the gap to Microsoft skill readiness. The integration manager turns it into an executive and manager-ready report.

The important part is traceability. Every agent returns a judge-facing reasoning summary with evidence objects, confidence, uncertainty, assumptions, next action, grounding refs, and audit entries. Sparse evidence triggers human review instead of fabricated certainty.

For the hackathon, the app runs locally in demo mode using synthetic experiment data and local markdown grounding that simulates Microsoft IQ retrieval. The Azure production boundary is real and honest: Azure AI Search, Azure OpenAI, Blob Storage, and Cosmos DB adapters are present, and they activate only when credentials are configured.

The result is a practical enterprise workflow: failed experiments become reusable organizational memory, not buried postmortems.
