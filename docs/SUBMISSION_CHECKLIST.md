# Submission Checklist

- Demo runs without Azure credentials using Foundry IQ Local Adapter Mode.
- `/iq/status` reports honest limitations about Azure quota.
- `/demo/run` returns foundry_iq_layer and grounding story.
- Upload endpoint accepts structured ExperimentLog JSON.
- Frontend shows Auth screens and Experiment upload panel in demo mode.
# Submission Checklist

This document tracks the readiness of FailureLens IQ for submission to the Microsoft Agents League Hackathon 2026.

## Non-Negotiable Compliance Items

- [x] **Foundry IQ Local Adapter:** Fully implemented and configured in `backend/services/foundry_iq_local_adapter.py`.
- [x] **No False Claims:** We do not claim live Azure or live Microsoft IQ in demo mode.
- [x] **OpenAI API Fallback:** Implemented and credential-gated via `backend/services/openai_client.py`.
- [x] **Honest Compliance Documentation:** Documented across all markdown files in `docs/`.
- [x] **No secrets committed:** Checked and verified. `.env` has no active secrets, only demo variables.
- [x] **Agent Traces:** Structured reasoning traces contain `citation_ids`, `evidence_used`, `confidence`, `uncertainty`, `next_action`, and `grounding_source`. No raw internal chain-of-thought is exposed.
- [x] **Frontend Visuals:** Sequentially animated agent graph, failure metric charts, evidence trails, and pipeline diagrams are fully interactive.
