from __future__ import annotations

from backend.api.main import app
from backend.api.routes.analyze import router as analyze_router
import logging

logger = logging.getLogger(__name__)

# Include the new Microsoft Foundry Agent/Model calling endpoint
app.include_router(analyze_router)

logger.info("FailureLens IQ FastAPI backend initialized with Microsoft Foundry routing layer.")
