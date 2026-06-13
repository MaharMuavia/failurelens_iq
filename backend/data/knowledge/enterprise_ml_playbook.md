# Enterprise ML Playbook

Standard operating procedures when a FailureLens IQ diagnosis is produced.

---

## 1. Immediate Fix
* Apply the specific recommended fixes from the analysis.
* Retrain the model with the fix applied.
* Compare retrained metrics against the original baseline.

## 2. Validation Protocol
* Switch from single-split to k-fold cross-validation (k >= 5).
* Ensure stratified splits for classification tasks.
* Verify no data leakage in the preprocessing pipeline.

## 3. Next Experiment Plan
* Design an ablation study isolating each variable.
* Use a hyperparameter search framework (Optuna, Ray Tune).
* Document all experiment variants in an experiment tracker (MLflow, W&B).

## 4. Production Risk Assessment
* Evaluate whether the failure pattern could recur in production.
* Assign a risk level (Low / Medium / High / Critical).
* Define rollback criteria before deploying any new model.

## 5. Team Learning Recommendation
* Map the failure to the Certification Rubric.
* Schedule a team knowledge-sharing session on the identified gap.
* Add the failure pattern to the team's internal failure-case library.
* Update onboarding material to prevent recurrence.
