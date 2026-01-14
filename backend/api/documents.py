import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict
from shared.lumi_doc import LumiDoc, LumiSection
from utils.surreal_utils import get_document_version

logger = logging.getLogger(__name__)
router = APIRouter()


class DocumentSectionsResponse(BaseModel):
    """Response model for document sections endpoint"""

    arxiv_id: str
    version: str
    sections: list[LumiSection]

    model_config = ConfigDict(
        alias_generator=lambda field_name: "".join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(field_name.split("_"))
        ),
        populate_by_name=True,
        json_schema_extra={"by_alias": True},
    )
    # Reusable model config for all Lumi models


@router.get(
    "/{arxiv_id}/{version}", response_model=LumiDoc, response_model_by_alias=True
)
async def get_document(arxiv_id: str, version: str) -> LumiDoc:
    """
    Get full LumiDoc for a paper version
    Returns: Complete document with sections, summaries, etc.
    """
    doc_version = await get_document_version(arxiv_id, version)

    if not doc_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    # Convert DocumentVersion to LumiDoc (extract just the document content fields)
    try:
        doc = LumiDoc(
            markdown=doc_version.markdown or "",
            sections=doc_version.sections or [],
            concepts=doc_version.concepts or [],
            abstract=doc_version.abstract,
            references=doc_version.references,
            footnotes=doc_version.footnotes,
            summaries=doc_version.summaries,
            metadata=doc_version.metadata,
            loading_status=doc_version.loading_status,
            loading_error=doc_version.loading_error,
        )
        return doc
    except Exception as e:
        logger.error(f"Error parsing document {arxiv_id} v{version}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing document: {str(e)}",
        ) from e


@router.get(
    "/{arxiv_id}/{version}/sections",
    response_model=DocumentSectionsResponse,
    response_model_by_alias=True,
)
async def get_document_sections(
    arxiv_id: str, version: str
) -> DocumentSectionsResponse:
    """
    Get only sections (lighter weight than full document)

    Useful for rendering table of contents
    """
    doc_version = await get_document_version(arxiv_id, version)

    if not doc_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    # Access sections from DocumentVersion model
    try:
        sections = doc_version.sections or []
        return DocumentSectionsResponse(
            arxiv_id=arxiv_id, version=version, sections=sections
        )
    except Exception as e:
        logger.error(f"Error parsing sections for {arxiv_id} v{version}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing sections: {str(e)}",
        ) from e
