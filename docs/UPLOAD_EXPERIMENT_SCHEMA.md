# Upload Experiment Schema

The `/experiments/upload` endpoint expects a structured ExperimentLog JSON with fields such as:

- `experiment_id`, `team_id`, `project_name`, `model_type`, `dataset_name`
- `pipeline_stage`, `validation_strategy`, `metrics`, `baseline_metrics`
- `failure_symptoms`, `failure_observation`, `engineer_notes`, `outcome`

See `docs/VIDEO_DEMO_SCRIPT.md` for a sample experiment used in the demo.
