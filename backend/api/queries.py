import logging

from fastapi import APIRouter, HTTPException
from import_pipeline.answers import generate_lumi_answer
from llm_models.llm import LLMInvalidResponseException
from pydantic import BaseModel
from shared.api import LumiAnswer, LumiAnswerRequest
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
        # Parse dictionaries into Pydantic model instances
        # Pydantic automatically handles both camelCase (from frontend) and snake_case
        lumi_doc = LumiDoc(**request.doc)
        answer_request = LumiAnswerRequest(**request.request)

        logger.info(
            f"Generating answer for query: {answer_request.query[:50] if answer_request.query else 'N/A'}, "
            f"highlight: {'Yes' if answer_request.highlight else 'No'}, "
            f"image: {'Yes' if answer_request.image else 'No'}"
        )

        # Generate answer using existing pipeline
        lumi_answer: LumiAnswer = generate_lumi_answer(
            lumi_doc, answer_request, request.api_key
        )

        # Convert Pydantic model to camelCase dictionary for frontend
        result = lumi_answer.model_dump(by_alias=True)

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
