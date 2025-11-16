import logging
from dataclasses import asdict

from fastapi import APIRouter, HTTPException
from import_pipeline.answers import generate_lumi_answer
from llm_models.llm import LLMInvalidResponseException
from pydantic import BaseModel
from shared.api import LumiAnswer, LumiAnswerRequest
from shared.json_utils import convert_keys
from shared.lumi_doc import LumiDoc

logger = logging.getLogger(__name__)
router = APIRouter()


class GetLumiResponseRequest(BaseModel):
    """Request for AI answer generation"""

    doc: dict  # LumiDoc as dictionary (from frontend JSON)
    request: dict  # LumiAnswerRequest as dictionary (from frontend JSON)
    api_key: str | None = None  # Optional API key override


@router.post("/answer")
async def get_lumi_response(request: GetLumiResponseRequest):
    """
    Generate AI answer to user query

    Supports:
    - Text queries: General questions about the paper
    - Text with highlights: Questions about specific highlighted passages
    - Image queries: Questions about figures/images in the paper
    """
    try:
        # Convert camelCase keys from frontend to snake_case for backend
        doc_dict = convert_keys(request.doc, "camel_to_snake")
        request_dict = convert_keys(request.request, "camel_to_snake")

        # Parse dictionaries into dataclass instances
        # Note: LumiDoc and LumiAnswerRequest dataclasses can be instantiated from dicts
        lumi_doc = LumiDoc(**doc_dict)
        answer_request = LumiAnswerRequest(**request_dict)

        logger.info(
            f"Generating answer for query: {answer_request.query[:50] if answer_request.query else 'N/A'}, "
            f"highlight: {'Yes' if answer_request.highlight else 'No'}, "
            f"image: {'Yes' if answer_request.image else 'No'}"
        )

        # Generate answer using existing pipeline
        lumi_answer: LumiAnswer = generate_lumi_answer(
            lumi_doc, answer_request, request.api_key
        )

        # Convert dataclass to dictionary
        result = asdict(lumi_answer)

        # Convert snake_case to camelCase for frontend
        result = convert_keys(result, "snake_to_camel")

        logger.info(f"Answer generated successfully: {lumi_answer.id}")
        return result

    except ValueError as e:
        # Validation errors (e.g., neither query nor highlight provided)
        logger.error(f"Invalid request: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e

    except LLMInvalidResponseException as e:
        # LLM service errors
        logger.error(f"LLM error: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to generate answer from LLM service"
        ) from e

    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error generating answer: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e
