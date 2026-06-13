from __future__ import annotations
import copy
from pathlib import Path
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field

from backend.core.config import settings
from backend.core.security import require_api_key
from backend.services.prompt_experiment_builder import PromptExperimentBuilder
from backend.services.interactive_report_service import InteractiveReportService
from backend.api.routes.demo import build_demo_response, maybe_upload_report

router = APIRouter()

class PromptAnalysisRequest(BaseModel):
    prompt: str
    team_id: str = "demo-team"
    use_foundry_model: bool = True
    generate_report: bool = True

@router.post("/prompt/analyze")
async def analyze_prompt(
    request: Request,
    payload: PromptAnalysisRequest,
    _auth: Any = Depends(require_api_key)
) -> dict[str, Any]:
    app_state = request.app.state
    
    # 1. Convert prompt to ExperimentLog using PromptExperimentBuilder
    builder = PromptExperimentBuilder()
    foundry_client = app_state.foundry_openai_client if payload.use_foundry_model else None
    
    try:
        exp, extract_meta = await builder.build(payload.prompt, foundry_openai_client=foundry_client)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to parse prompt to experiment log: {e}")
        
    # Save the generated experiment log to the store so historical search or other routes can find it
    await app_state.experiment_store.save_uploaded_experiment(exp)
    
    # 2. Run orchestrator
    ctx = await app_state.orchestrator.run(exp)
    
    # 3. Grounding retrieve (same as in /demo/run)
    refs = []
    refs.extend(await app_state.grounding_adapter.retrieve_experiment_context(exp.experiment_id))
    refs.extend(await app_state.grounding_adapter.retrieve_historical_failures(
        ctx.diagnosis.knowledge_gap if ctx.diagnosis else "ml failure", 
        top_k=5
    ))
    
    active_provider = type(app_state.iq_provider).__name__
    iq_retrieval_raw = await app_state.iq_provider.retrieve(
        f"{exp.experiment_id} evaluation methodology minority F1 remediation certification manager governance",
        top_k=5,
    )
    iq_retrieval = iq_retrieval_raw.model_dump(mode="json") if hasattr(iq_retrieval_raw, "model_dump") else iq_retrieval_raw
    grounding_summary = await app_state.grounding_adapter.build_grounding_summary(refs, active_provider)
    azure_summary = await app_state.openai_client.summarize_failure_report(ctx)
    store_result = await app_state.grounding_adapter.store_reasoning_trace(ctx.run_id, ctx.model_dump(mode="json"))
    
    report_path_md = app_state.report_service.generate(ctx)
    blob_upload = await maybe_upload_report(
        app_state.grounding_adapter.blob_client,
        ctx.experiment.experiment_id,
        report_path_md.read_text(encoding="utf-8"),
    )
    
    analysis_result = build_demo_response(ctx, grounding_summary, store_result, azure_summary, blob_upload, active_provider, iq_retrieval)
    
    # 4. Save the timeline trace info
    app_state.trace_timeline[ctx.run_id] = {
        "run_id": ctx.run_id,
        "experiment_id": ctx.experiment.experiment_id,
        "status": "completed",
        "timeline": [
            {
                "agent_name": trace.agent_name,
                "status": trace.status,
                "duration_ms": trace.duration_ms,
                "confidence_score": trace.confidence_score,
                "event_count": len(trace.reasoning_steps),
            }
            for trace in ctx.agent_trace
        ],
    }
    
    # 5. Generate interactive report if requested
    generated = False
    download_url = ""
    local_path = ""
    if payload.generate_report:
        report_service = InteractiveReportService(Path(settings.REPORT_OUTPUT_DIR))
        html_path = report_service.generate_html_report_file(ctx, payload.prompt, extract_meta, analysis_result)
        generated = True
        download_url = f"/report/{exp.experiment_id}/interactive"
        local_path = str(html_path.relative_to(Path.cwd()) if html_path.is_absolute() else html_path).replace("\\", "/")
        
    return {
        "prompt_id": exp.experiment_id,
        "original_prompt": payload.prompt,
        "generated_experiment": exp.model_dump(mode="json"),
        "analysis_result": analysis_result,
        "interactive_report": {
            "generated": generated,
            "format": "html",
            "download_url": download_url,
            "local_path": local_path
        },
        "prompt_extraction": extract_meta.get("prompt_extraction")
    }

@router.get("/report/{run_id}/interactive")
async def get_interactive_report(
    run_id: str,
    download: bool = Query(default=False),
    _auth: Any = Depends(require_api_key)
):
    if "/" in run_id or "\\" in run_id or run_id == "..":
        raise HTTPException(status_code=400, detail="Invalid run_id.")
        
    report_file = Path(settings.REPORT_OUTPUT_DIR) / f"{run_id}.html"
    if not report_file.exists():
        raise HTTPException(status_code=404, detail="Interactive report not found.")
        
    if download:
        return FileResponse(
            path=report_file,
            media_type="text/html",
            filename=f"{run_id}.html"
        )
        
    return HTMLResponse(
        content=report_file.read_text(encoding="utf-8"),
        status_code=200
    )
