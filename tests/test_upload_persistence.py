import json
from pathlib import Path
import httpx
import pytest

from backend.api.main import create_app
from backend.services.experiment_store import ExperimentStore
from backend.utils.data_loader import DataLoader


def uploaded_payload():
    payload = json.loads(Path("data/synthetic/ml_experiment_logs.json").read_text(encoding="utf-8"))[0]
    payload["experiment_id"] = "EXP-UPLOAD-PERSIST-1"
    payload["failure_observation"] = "Uploaded experiment failed because validation hid minority-class behavior."
    return payload


@pytest.mark.anyio
async def test_upload_experiment_retrieve_and_analyze():
    app = create_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Upload experiment
        upload_response = await client.post("/experiments/upload", json=uploaded_payload())
        assert upload_response.status_code == 200
        assert upload_response.json()["status"] == "stored"
        assert upload_response.json()["experiment_id"] == "EXP-UPLOAD-PERSIST-1"

        # 2. Retrieve uploaded experiment
        retrieve_response = await client.get("/experiments/EXP-UPLOAD-PERSIST-1")
        assert retrieve_response.status_code == 200
        assert retrieve_response.json()["failure_observation"].startswith("Uploaded experiment")

        # 3. Analyze uploaded experiment
        analysis_response = await client.post("/analysis/run", json={"experiment_id": "EXP-UPLOAD-PERSIST-1"})
        assert analysis_response.status_code == 200
        assert analysis_response.json()["experiment"]["experiment_id"] == "EXP-UPLOAD-PERSIST-1"


@pytest.mark.anyio
async def test_upload_experiment_survives_new_store_instance(tmp_path):
    # Setup temporary file path for store
    db_file = tmp_path / "uploaded_experiments.json"
    
    data_loader = DataLoader()
    data_loader.load_all()
    
    # Create first store instance and save
    store1 = ExperimentStore(data_loader, storage_path=db_file)
    exp = await store1.get_experiment("EXP-1001") # Get a base experiment
    
    # Clone and modify it, excluding computed fields to satisfy extra="forbid"
    exp_dump = exp.model_dump()
    for key in [
        "minority_pct", "minority_f1", "reported_metric", "metric_degradation_score",
        "has_error_logs", "has_drift_indicators", "has_leakage_signal", "has_bias_language"
    ]:
        exp_dump.pop(key, None)
        
    exp_dump["experiment_id"] = "EXP-SURVIVAL-TEST"
    uploaded_exp = exp.model_validate(exp_dump)
    
    await store1.save_uploaded_experiment(uploaded_exp)
    
    # Create new store instance pointing to same file path
    store2 = ExperimentStore(data_loader, storage_path=db_file)
    
    # Verify retrieval
    retrieved = await store2.get_experiment("EXP-SURVIVAL-TEST")
    assert retrieved.experiment_id == "EXP-SURVIVAL-TEST"
