from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from backend.models.schemas import ExperimentLog
from backend.utils.data_loader import DataLoader
from backend.core.config import settings

class ExperimentStore:
    def __init__(self, data_loader: DataLoader, storage_path: Path | None = None) -> None:
        self.data_loader = data_loader
        self.storage_path = storage_path or Path(settings.UPLOAD_STORE_PATH)
        self._cache: dict[str, ExperimentLog] = {}
        self._load_local_uploads()

    def _load_local_uploads(self) -> None:
        if self.storage_path.exists():
            try:
                data = json.loads(self.storage_path.read_text(encoding="utf-8"))
                for key, val in data.items():
                    for k in [
                        "minority_pct", "minority_f1", "reported_metric", "metric_degradation_score",
                        "has_error_logs", "has_drift_indicators", "has_leakage_signal", "has_bias_language"
                    ]:
                        val.pop(k, None)
                    self._cache[key] = ExperimentLog.model_validate(val)
            except Exception:
                pass

    def _save_local_uploads(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        temp_dir = self.storage_path.parent
        fd, temp_path_str = tempfile.mkstemp(dir=temp_dir, prefix="upload_exp_", suffix=".json")
        try:
            with os.fdopen(fd, 'w', encoding="utf-8") as tmp:
                json_data = {}
                for k, v in self._cache.items():
                    dumped = v.model_dump(mode="json")
                    for key in [
                        "minority_pct", "minority_f1", "reported_metric", "metric_degradation_score",
                        "has_error_logs", "has_drift_indicators", "has_leakage_signal", "has_bias_language"
                    ]:
                        dumped.pop(key, None)
                    json_data[k] = dumped
                json.dump(json_data, tmp, indent=2)
            os.replace(temp_path_str, self.storage_path)
        except Exception:
            if os.path.exists(temp_path_str):
                os.remove(temp_path_str)
            raise

    async def list_experiments(
        self,
        limit: int = 25,
        team_id: str | None = None,
        outcome: str | None = None,
        failure_category: str | None = None,
    ) -> list[ExperimentLog]:
        all_exps = list(self._cache.values()) + self.data_loader.experiments
        
        seen = set()
        deduped = []
        for exp in all_exps:
            if exp.experiment_id not in seen:
                seen.add(exp.experiment_id)
                deduped.append(exp)

        if team_id:
            deduped = [e for e in deduped if e.team_id == team_id]
        if outcome:
            deduped = [e for e in deduped if e.outcome == outcome]
        if failure_category:
            deduped = [e for e in deduped if (e.failure_category_label or "") == failure_category]

        return deduped[:limit]

    async def get_experiment(self, experiment_id: str) -> ExperimentLog:
        if experiment_id in self._cache:
            return self._cache[experiment_id]
        return self.data_loader.get_experiment(experiment_id)

    async def save_uploaded_experiment(self, experiment: ExperimentLog) -> None:
        self._cache[experiment.experiment_id] = experiment
        self._save_local_uploads()

    async def delete_uploaded_experiment(self, experiment_id: str) -> None:
        if experiment_id in self._cache:
            del self._cache[experiment_id]
            self._save_local_uploads()
