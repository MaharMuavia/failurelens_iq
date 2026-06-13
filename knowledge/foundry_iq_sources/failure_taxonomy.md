id: failure-taxonomy-001
title: Failure Taxonomy
source_type: failure_taxonomy
permission_scope: demo
citation: knowledge/foundry_iq_sources/failure_taxonomy.md#failure-taxonomy-001
tags: ml_failure, root_cause_analysis, model_evaluation
agent_usage_notes: The FailureClassifierAgent uses this taxonomy to classify observed issues into standard Failure Categories based on signals and metrics.
content: |
  # Failure Taxonomy
  
  Machine learning systems can fail in **intentional** or **unintentional** ways [29†L1-L8]. Intentional failures (adversarial attacks, data poisoning) occur when an attacker subverts the system. Unintentional failures arise from design flaws or data issues [29†L1-L8]. We categorize common ML failure types for root-cause analysis:
  
  ## Evaluation Methodology Failure
  Metrics or validation strategies are inappropriate. For example, *“High accuracy, low minority-class F1”* indicates that class imbalance caused a misleading high accuracy [14†L310-L314]. Always use stratified splits and robust metrics (F1, weighted AUC) when classes are imbalanced [32†L203-L212][32†L223-L230].
  
  ## Data Quality and Drift
  Changes or errors in data over time degrade performance. *“Data drift”* means input data distributions have shifted (e.g. sensor replacement or seasonal trends) [43†L119-L127]. Broken sensors or missing data also cause drift. Continual data monitoring is needed [37†L103-L105][43†L123-L131].
  
  ## Data Leakage
  Model has access to features not available at prediction time. This often produces **abnormally high accuracy** (e.g. 95%+) [33†L9-L16]. Look for features derived from the label or future information. Remove or delay such features to fix leakage.
  
  ## Model and Pipeline Bugs
  Implementation errors (e.g. incorrect data splitting, feature encoding mistakes, missing hyperparameters) can cause failures or unstable models. Use rigorous code reviews and automated tests to catch these engineering issues.
  
  ## Overfitting / Underfitting
  Model is too complex or too simple. Overfitting yields high train accuracy but poor generalization; mitigated by more data, regularization, or cross-validation [32†L98-L107][32†L158-L166]. Underfitting means the model fails to capture patterns (low accuracy), requiring more features or a different algorithm.
  
  ## Responsible AI / Fairness Failures
  The model may perform well overall but *unfairly* on subgroups. Use fairness assessments and error analysis (Azure ML’s Responsible AI dashboard) to detect if any group (gender, ethnicity, etc.) has systematically higher error [25†L68-L77][25†L88-L96]. Include fairness constraints or additional data to address discovered bias.
  
  ## Deployment/Environment Mismatch
  Differences between training and production (e.g. missing data pipeline, hardware differences) can break models. Validate the entire end-to-end flow in a staging environment.
  
  Each failure type includes *signals* (e.g. high precision but low recall, rising data drift statistics) and *examples* in our taxonomy to guide analysis. Agents use this taxonomy to classify issues and suggest targeted fixes.
