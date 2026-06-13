id: responsible-ai-001
title: Responsible AI Checklist
source_type: responsible_ai
permission_scope: demo
tags: fairness, transparency, security
agent_usage_notes: All agents check their outputs against these rules. If a fairness disparity or privacy risk is found, the agents flag the run for human oversight.
content: |
  # Responsible AI Checklist
  
  We incorporate Microsoft’s **six responsible AI principles** into our review process [25†L53-L62]. Key checklist items:
  
  ## Fairness
  - Check model metrics across sensitive groups (gender, ethnicity, age) using a fairness dashboard [25†L75-L84].
  - Ensure similar predictions for similar profiles (e.g. similar minority F1 performance).
  
  ## Reliability & Safety
  - Verify the model handles unexpected inputs gracefully (test edge cases).
  - Use error analysis tools to find any data cohorts with unusually high error [25†L88-L97].
  
  ## Transparency & Interpretability
  - Use model interpretability (feature importance) and counterfactual analysis for key predictions [25†L99-L108].
  - Document how the model makes decisions (e.g. which features most influence output).
  
  ## Privacy & Security
  - Ensure no sensitive PII is used or logged. Encrypt data at rest/in transit.
  - Restrict access to datasets and models via Azure RBAC [25†L137-L146].
  
  ## Inclusiveness
  - Validate that the training data represents diverse populations.
  - Check for any subgroup entirely excluded (e.g. age or demographic not present).
  
  ## Human Oversight
  - Define thresholds for human review (e.g. if model confidence < 0.60 or if fairness alerts are raised).
  - Ensure a subject-matter expert reviews flagged cases before deployment.
  
  Each agent or pipeline stage cross-references this checklist. For example, if a classification failure is detected, the **ClassifierAgent** will verify fairness metrics; if issues arise, it suggests remedies like “collect more diverse data” or “introduce fairness constraints”. Citations and audit logs are generated for all Responsible AI checks [25†L53-L62].
