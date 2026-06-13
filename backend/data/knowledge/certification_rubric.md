# FailureLens IQ – Certification Rubric

Maps ML failure modes to enterprise learning and certification gaps so
organizations can close skill deficits revealed by experiment failures.

---

## Model Evaluation
* **Gap indicator:** Incorrect or missing metric selection.
* **Learning path:** Cross-validation, stratified splits, proper metric interpretation.

## Cross-Validation
* **Gap indicator:** Single hold-out used instead of k-fold.
* **Learning path:** k-fold, stratified k-fold, time-series split, nested CV.

## Leakage Prevention
* **Gap indicator:** Features derived from target or future information.
* **Learning path:** Feature auditing, pipeline-aware preprocessing, temporal splits.

## Responsible AI
* **Gap indicator:** No fairness or bias analysis performed.
* **Learning path:** Fairness metrics, bias mitigation, model cards, RAI dashboards.

## Feature Engineering
* **Gap indicator:** Raw features used without transformation or selection.
* **Learning path:** Feature importance, PCA, mutual information, domain transforms.

## Hyperparameter Tuning
* **Gap indicator:** Default hyperparameters used without search.
* **Learning path:** Grid search, random search, Bayesian optimization, Optuna.

## Monitoring & MLOps
* **Gap indicator:** No production monitoring or drift detection.
* **Learning path:** Model monitoring, data drift alerts, CI/CD for ML, retraining strategies.
