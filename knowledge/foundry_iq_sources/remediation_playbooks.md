id: remediation-playbooks-001
title: Remediation Playbooks
source_type: remediation_playbooks
permission_scope: demo
citation: knowledge/foundry_iq_sources/remediation_playbooks.md#remediation-playbooks-001
tags: ml_best_practices, troubleshooting, root_cause_mitigation
agent_usage_notes: The PrescriptiveCoachAgent retrieves these playbooks to formulate 3-day and 7-day technical remediation plans.
content: |
  # Remediation Playbooks
  
  For each failure, we prescribe action steps and timelines (3-day, 7-day plans) using best practices:
  
  ## Evaluation Metrics & Class Imbalance
  - *Check metrics:* Prefer F1-score or weighted metrics over accuracy on imbalanced data [32†L223-L230].
  - *Resample or reweight:* Use class weights or over/under-sampling to balance the training set [32†L203-L212][32†L223-L230].
  - *Validation:* Switch to stratified or time-based cross-validation.
  
  ## Data Leakage
  - *Review features:* Ensure no data from the future is included. Drop any feature that contains post-event information [33†L9-L16].
  - *Re-evaluate model:* Retrain without leaking features and compare. High original accuracy (e.g. ≈95%) is a red flag [33†L9-L16].
  
  ## Data Drift
  - *Monitor continuously:* Set up data drift monitors (Azure ML Model Monitor) on key features [37†L103-L105].
  - *Retrain model:* If drift is detected (feature means or distributions change), retrain the model with up-to-date data [37†L103-L105][43†L123-L131].
  - *Alert and analyze:* Drill into drifting features to identify root causes (e.g. sensor change or seasonal trends) [43†L123-L131].
  
  ## Overfitting
  - *Regularize & simplify:* Apply L1/L2 regularization, reduce model complexity (prune tree depth, layers) [32†L141-L149][32†L151-L158].
  - *More data:* Collect more training data or use data augmentation.
  - *Cross-validation:* Use k-fold cross-validation to detect overfitting early [32†L158-L166].
  
  ## Noisy Data / Labels
  - *Clean data:* Identify and correct mislabeled examples.
  - *Outlier detection:* Remove or treat extreme outliers.
  - *Quality gates:* Add data validation steps in pipeline.
  
  ## Fairness and Bias
  - *Assess fairness:* Use Azure ML’s Responsible AI dashboard to compute fairness metrics across groups [25†L75-L84].
  - *Mitigation:* If bias is found, try balancing the training data, add fairness constraints, or use model explanations to adjust features.
  
  ## Other (Governance)
  - *Code review:* Perform peer review of the code and features.
  - *Documentation:* Document assumptions, known limitations, and remediation actions.
  
  Each playbook outlines immediate checks (hours), short-term fixes (days), and long-term improvements (weeks) tailored to the failure. Agents use these steps to suggest next actions in an automated root-cause analysis.
