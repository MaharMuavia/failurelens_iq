import asyncio
from pathlib import Path

from backend.core.orchestrator import Orchestrator
from backend.services.knowledge_index import KnowledgeIndex
from backend.utils.data_loader import DataLoader


def test_different_knowledge_queries_return_different_top_hits():
    index = KnowledgeIndex(Path("knowledge/foundry_docs"))
    result1 = index.search("imbalanced classification minority f1 stratified")
    result2 = index.search("responsible AI fairness protected attribute bias")
    assert result1[0].source_file != result2[0].source_file or result1[0].section_title != result2[0].section_title


def test_cert_mapper_maps_exp_1001_to_dp100():
    d = DataLoader()
    d.load_all()
    ctx = asyncio.run(Orchestrator().run(d.get_experiment("EXP-1001")))
    assert ctx.cert_mapping.cert_code == "DP-100"


def test_cert_mapper_maps_exp_2001_to_ai102():
    d = DataLoader()
    d.load_all()
    ctx = asyncio.run(Orchestrator().run(d.get_experiment("EXP-2001")))
    assert ctx.cert_mapping.cert_code == "AI-102"
