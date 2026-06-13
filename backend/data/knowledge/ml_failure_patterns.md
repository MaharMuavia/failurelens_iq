# ML Failure Patterns Knowledge Base

This document catalogues common machine-learning experiment failure patterns.
FailureLens IQ references this file for IQ-grounding during analysis.

---

## Overfitting
* **Symptoms:** Training accuracy much higher than validation/test.
* **Root causes:** Excessive model complexity, insufficient data, no regularization.
* **Indicators:** Large train-val gap (>= 15 pp), low bias high variance.

## Underfitting
* **Symptoms:** Both training and validation accuracy are low (< 65%).
* **Root causes:** Model too simple, insufficient features, bad hyperparameters.
* **Indicators:** Low accuracy across all splits, high bias.

## Data Leakage
* **Symptoms:** Unrealistically high train + val accuracy but poor test/production.
* **Root causes:** Target information leaks into features (e.g. timestamp, future data).
* **Indicators:** Near-perfect val score, dramatic test drop, suspiciously informative features.

## Class Imbalance
* **Symptoms:** High overall accuracy masks poor minority-class recall.
* **Root causes:** Skewed class distribution, no resampling, wrong metric.
* **Indicators:** Good accuracy but recall/F1 < 0.3 on minority class, confusion-matrix skew.

## Metric Mismatch
* **Symptoms:** Accuracy looks fine but business outcomes are poor.
* **Root causes:** Using accuracy when precision/recall/F1/AUC matters more.
* **Indicators:** Business KPIs diverge from model KPIs.

## Non-Representative Split
* **Symptoms:** Performance varies drastically across folds or deployment.
* **Root causes:** Random split on grouped/time-series data, sample-selection bias.
* **Indicators:** Large variance across CV folds, production performance drift.

## Feature Drift
* **Symptoms:** Model performs well at training time but degrades in production.
* **Root causes:** Distribution shift between training data and live data.
* **Indicators:** Feature distributions change over time, monitoring alerts fire.

## Label Noise
* **Symptoms:** Model struggles to converge or generalize despite adequate data.
* **Root causes:** Noisy or inconsistent labels from human annotators.
* **Indicators:** High loss variance, disagreement between annotators > 10%.
