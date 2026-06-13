from fastapi import APIRouter, HTTPException, Depends, Request
from backend.models.experiment import ExperimentInput
from backend.models.analysis import FailureAnalysisResponse
from backend.services.failurelens_service import FailureLensService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
service = FailureLensService()

@router.post("/api/analyze", response_model=FailureAnalysisResponse)
async def analyze_experiment(request: Request, payload: ExperimentInput) -> FailureAnalysisResponse:
    """
    Analyzes a failed ML experiment using the configured Microsoft Foundry agent, model, or mock mode.
    """
    logger.info("Received analyze request for experiment_id: %s", payload.experiment.experiment_id)
    try:
        response = await service.analyze(request, payload)
        return response
    except Exception as e:
        logger.exception("Failed to run failure analysis: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Internal analysis failure: {e}")
