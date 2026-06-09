from backend.core.similarity_engine import SimilarityEngine
from backend.utils.data_loader import DataLoader


def test_similarity_engine_finds_similar_experiments():
    d = DataLoader()
    d.load_all()
    target = d.get_experiment("EXP-1001")
    others = [exp for exp in d.experiments if exp.experiment_id != "EXP-1001"]
    results = SimilarityEngine().find_similar(target, others, top_k=3)
    assert results
    assert results[0].similarity_score > 0.50
    assert results[0].shared_signals
