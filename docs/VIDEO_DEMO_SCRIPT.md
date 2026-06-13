# Video Demo Script (2 minutes)

Use the judge-facing script in the repository root `VIDEO_DEMO_SCRIPT.md` for a concise 2-minute walkthrough. The final submission includes a dedicated 2-minute script in the repo root.
# FailureLens IQ 2-Minute Video Demo Script

## 0:00-0:15 - The Problem (Slide / Dashboard Hero)
* "Failed ML experiments usually disappear after a bad metric. Teams repeat mistakes, and managers have zero visibility into why models fail or what skills the team is missing. High aggregate accuracy hides minority-class failure."

## 0:15-0:30 - The Solution (Show main page & click "Run Judge Demo")
* "FailureLens IQ turns failed experiments into valuable team memory. Let's click 'Run Judge Demo'. Watch the animated agent flow sequentially activate from Planner, through Foundry IQ Layer, Failure Classifier, Root Cause Analyzer, Historian, Coach, Cert Evaluator, and Integration Manager."

## 0:30-1:00 - Visualizing Failure & Agent Flow (Point to Metric Chart & Graph)
* "Behold the Failure Metric Chart. The 93% aggregate accuracy completely hid the 14% minority F1 collapse. Under the hood, the Planner triggered our agent pipeline. The Foundry IQ Layer retrieves grounded evidence. The Failure Classifier detects an evaluation methodology failure."

## 1:00-1:30 - Evidence & Reasoning (Show Evidence Trail & Root Cause Analyzer trace)
* "The Root Cause Analyzer uses our direct OpenAI reasoning fallback to explain the violated assumption with calibrated confidence and counter-evidence. Look at the IQ Evidence Trail: every citation includes the exact source file, relevance score, and permission scope. Our agents do not expose hidden chain-of-thought, keeping responses safe, auditable, and structured."

## 1:30-1:45 - Honest Microsoft IQ Layer (Show Foundry IQ Layer Panel)
* "FailureLens IQ implements Foundry IQ using Azure AI Search as the grounded retrieval layer. Because our subscription had 0 TPM quota, live Azure OpenAI was blocked. We do not fake live usage. Instead, we implement Foundry IQ Local Adapter Mode: a local, citation-based, permission-aware knowledge layer. It keeps the project fully runnable without Azure quota while preserving a direct adapter path to live Azure AI Search and Foundry IQ."

## 1:45-2:00 - Business Value (Show Manager Summary & Remediation)
* "Downstream, the Coach builds a 7-day remediation plan mapped to Microsoft certifications like DP-100. This is not just a classifier—it is an enterprise learning memory system. Thank you."
