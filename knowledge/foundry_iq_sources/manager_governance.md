id: manager-governance-001
title: Manager Governance Playbook
source_type: manager_governance
permission_scope: demo
tags: governance, escalation, oversight
agent_usage_notes: The IntegrationManagerAgent references this playbook to determine when to trigger the human review/escalation pipeline and how to format the summary card for leadership.
content: |
  # Manager Governance Playbook
  
  ## Escalation Criteria
  When to escalate to a manager or governance team:
  - **Repeated Failures:** If the same failure mode recurs across multiple experiments or teams, involve a manager to address systemic issues and resource allocation.
  - **Responsible AI Concerns:** Any red alerts on fairness or safety (e.g. protected-class disparities, ethical risks) should be flagged immediately for governance review.
  - **Regulatory Impact:** If model outputs could affect compliance (HIPAA, GDPR, etc.), notify leadership to ensure legal oversight.
  - **Resource Requests:** If fixes require significant changes (e.g. new data collection, infrastructure), escalate for approval.
  
  ## Manager Summary Template
  For escalated cases, prepare a brief including:
  - **Business Impact:** Clearly state how the failure affects goals (e.g. revenue loss, safety risk).
  - **Technical Root Cause:** Summary of why it failed (using taxonomy terms).
  - **Confidence & Uncertainty:** Model’s confidence; any unknown factors.
  - **Evidence:** Key citations from knowledge sources (taxonomy category, similar experiment examples).
  - **Next Steps:** Proposed action plan (short-term fix and long-term improvements).
  - **Training/Gaps:** Identify missing skills or tools (map to certifications or workshops).
  
  By following this playbook, governance maintains visibility on high-impact issues. Managers ensure that technical teams have support and that lessons (e.g. policy changes, training) are implemented.
