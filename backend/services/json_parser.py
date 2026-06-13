from __future__ import annotations

import json
import re
from typing import Any, Dict
from pydantic import ValidationError
from backend.models.analysis import FailureAnalysisResponse, UncertaintyBlock, CertificationGap, IQGrounding, AgentMetadata, ReasoningStep
import logging

logger = logging.getLogger(__name__)

def clean_and_extract_json(text: str) -> dict | None:
    """
    Clean raw string from LLM by removing markdown code block fences and preamble,
    then extract the first JSON object.
    """
    if not text:
        return None
        
    cleaned = text.strip()
    
    # Remove ```json ... ``` markdown block wrapper
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()
        
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
        
    # If standard parse fails, search for the first '{' and corresponding outer '}'
    start_idx = cleaned.find("{")
    if start_idx == -1:
        return None
        
    depth = 0
    for i in range(start_idx, len(cleaned)):
        char = cleaned[i]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                potential_json = cleaned[start_idx:i+1]
                try:
                    return json.loads(potential_json)
                except json.JSONDecodeError:
                    return None
                    
    return None

def parse_and_validate_analysis(raw_text: str, call_mode: str, agent_name: str, model_deployment: str) -> FailureAnalysisResponse:
    """
    Parses LLM response text, extracts JSON, validates against FailureAnalysisResponse,
    and returns a valid Pydantic model response. If anything fails, returns a safe fallback.
    """
    logger.debug("Parsing raw model response of length %d", len(raw_text) if raw_text else 0)
    
    parsed_json = clean_and_extract_json(raw_text)
    
    if parsed_json is not None:
        try:
            # Overwrite or fill metadata
            if "agent_metadata" not in parsed_json or not isinstance(parsed_json["agent_metadata"], dict):
                parsed_json["agent_metadata"] = {}
            
            parsed_json["agent_metadata"].update({
                "call_mode": call_mode,
                "agent_name": agent_name,
                "model_deployment": model_deployment,
                "schema_version": "1.0"
            })
            
            return FailureAnalysisResponse.model_validate(parsed_json)
        except ValidationError as val_err:
            logger.error("JSON schema validation failed: %s. Raw text: %s", str(val_err), raw_text)
        except Exception as err:
            logger.exception("Unexpected validation error: %s", str(err))
    else:
        logger.error("Failed to extract any valid JSON object from raw response. Raw text: %s", raw_text)
        
    # Return a safe fallback response if parsing or validation failed
    return FailureAnalysisResponse(
        failure_type="Undetermined",
        severity="Medium",
        confidence_score=0,
        reasoning_trace=[
            ReasoningStep(
                step=1,
                observation="Failed to parse reasoning output from model.",
                interpretation="System was unable to decode the JSON reasoning block returned by the backend model client."
            )
        ],
        evidence_used=["System failure: JSON decoding error"],
        root_causes=["Response format violation or model timeout"],
        uncertainty=UncertaintyBlock(
            level="High",
            missing_information=["Missing complete structured model analysis output"],
            alternative_explanations=["Model returned invalid or truncated JSON content"]
        ),
        recommended_fixes=["Verify model deployment logs", "Check prompt instructions and retry experiment analysis"],
        next_experiment_plan=["Run analysis in mock mode to verify system health"],
        certification_gap=CertificationGap(
            skill_gap="System diagnostic integration",
            recommended_learning="Investigate structured output APIs (e.g. OpenAI JSON Mode / structured outputs)."
        ),
        iq_grounding=IQGrounding(
            knowledge_sources_used=[],
            matched_failure_patterns=[],
            grounding_confidence=0
        ),
        agent_metadata=AgentMetadata(
            call_mode=call_mode,
            agent_name=agent_name,
            model_deployment=model_deployment,
            schema_version="1.0"
        )
    )
