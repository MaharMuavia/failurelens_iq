# Demo Script

## 1. EXP-1001 Reasoning Trace

Run:

```bash
curl -X POST http://localhost:8000/analysis/run/EXP-1001
```

Show the planner hypothesis citing `class_balance=88/12`, `accuracy`, `minority_f1`, and `validation_strategy=holdout`. Then show all six classifier rules, the diagnostic reflection notes, and the evidence list.

## 2. EXP-2001 SSE Stream

Run:

```bash
curl -N http://localhost:8000/analysis/stream/EXP-2001
```

Point out `pipeline_started`, agent events, reasoning steps, `confidence_gate`, and `pipeline_completed`.

## 3. Knowledge Search

Run:

```bash
curl "http://localhost:8000/knowledge/search?q=imbalanced+classification+minority+f1"
curl "http://localhost:8000/knowledge/search?q=responsible+AI+fairness+protected+attribute"
```

Show that DP-100 and AI-102 style documents rank differently.

## 4. TEAM-B Manager Intelligence

Run:

```bash
curl http://localhost:8000/manager/team/TEAM-B
```

Show the recurring pattern alert for Responsible AI / Bias failures and the vulnerability level.

## 5. SPARSE-001 Human Review Safety

Run:

```bash
curl -X POST http://localhost:8000/analysis/run/SPARSE-001
```

Show `requires_human_review=true`, `gate_passed=false`, and root cause exactly: `Insufficient evidence to determine root cause with required confidence.`
