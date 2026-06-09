import asyncio

from backend.core.planner import Planner
from backend.models.enums import FailureCategory
from backend.utils.data_loader import DataLoader


def test_planner_detects_exp_1001_category():
    d = DataLoader()
    d.load_all()
    ctx = asyncio.run(Planner().plan(d.get_experiment("EXP-1001"), d.experiments, d))
    assert ctx.hypothesis.suspected_category == FailureCategory.EVALUATION_METHODOLOGY
    assert "class_balance" in ctx.hypothesis.hypothesis_statement


def test_planner_raises_threshold_for_sparse_001():
    d = DataLoader()
    d.load_all()
    ctx = asyncio.run(Planner().plan(d.get_experiment("SPARSE-001"), d.experiments, d))
    assert ctx.plan.dynamic_threshold == 0.55
    assert ctx.plan.requires_human_review_flag is True
