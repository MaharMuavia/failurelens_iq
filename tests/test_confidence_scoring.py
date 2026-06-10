from backend.services.scoring_service import ScoringInputs, ScoringService


def test_more_evidence_increases_confidence():
    service = ScoringService()
    low = service.compute(ScoringInputs(category_evidence=0.2, metric_degradation=0.1, iq_relevance=0.3))
    high = service.compute(ScoringInputs(category_evidence=0.8, metric_degradation=0.7, iq_relevance=0.7, evidence_coverage=0.8))
    assert high.confidence > low.confidence


def test_conflict_penalty_lowers_confidence():
    service = ScoringService()
    no_conflict = service.compute(ScoringInputs(category_evidence=0.8, evidence_coverage=0.8))
    with_conflict = service.compute(ScoringInputs(category_evidence=0.8, evidence_coverage=0.8, conflict_penalty=0.5))
    assert with_conflict.confidence < no_conflict.confidence
