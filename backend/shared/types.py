# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================


from enum import StrEnum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


def _camel_case_alias_generator(field_name: str) -> str:
    """Convert snake_case to camelCase for API serialization"""
    return "".join(
        word.capitalize() if i > 0 else word
        for i, word in enumerate(field_name.split("_"))
    )


# Reusable model config for all Lumi models
LUMI_MODEL_CONFIG = ConfigDict(
    alias_generator=_camel_case_alias_generator,
    populate_by_name=True,  # Allow both snake_case and camelCase
    json_schema_extra={"by_alias": True},  # Serialize using camelCase by default
)


class LoadingStatus(StrEnum):
    """
    An enumeration to represent various loading states while importing a LumiDoc.
    """

    UNSET = "UNSET"
    WAITING = "WAITING"  # Importing paper into LumiDoc
    SUMMARIZING = "SUMMARIZING"  # Loading summaries after paper is imported
    SUCCESS = "SUCCESS"
    ERROR_DOCUMENT_LOAD = "ERROR_DOCUMENT_LOAD"
    ERROR_DOCUMENT_LOAD_INVALID_RESPONSE = "ERROR_DOCUMENT_LOAD_INVALID_RESPONSE"
    ERROR_DOCUMENT_LOAD_QUOTA_EXCEEDED = "ERROR_DOCUMENT_LOAD_QUOTA_EXCEEDED"
    ERROR_SUMMARIZING = "ERROR_SUMMARIZING"
    ERROR_SUMMARIZING_QUOTA_EXCEEDED = "ERROR_SUMMARIZING_QUOTA_EXCEEDED"
    ERROR_SUMMARIZING_INVALID_RESPONSE = "ERROR_SUMMARIZING_INVALID_RESPONSE"
    TIMEOUT = "TIMEOUT"


# Kept in sync with shared/lumi_doc.ts
class FeaturedImage(BaseModel):
    """Class for featured image."""

    image_storage_path: str

    model_config = LUMI_MODEL_CONFIG


class MetadataCollectionItem(BaseModel):
    """Class for metadata collection item."""

    metadata: "ArxivMetadata"
    featured_image: Optional["FeaturedImage"] = None

    model_config = LUMI_MODEL_CONFIG


class ThrottleCollectionItem(BaseModel):
    """Class for throttle collection item."""

    timestamp: Any  # Firestore timestamp created with firestore_v1.SERVER_TIMESTAMP
    succeeded: bool

    model_config = LUMI_MODEL_CONFIG


class ArxivMetadata(BaseModel):
    """Class for paper metadata from arxiv."""

    paper_id: str
    version: str
    authors: list[str]
    title: str
    summary: str  # the paper abstract
    updated_timestamp: str
    published_timestamp: str

    model_config = LUMI_MODEL_CONFIG


class ImageMetadata(BaseModel):
    """Class for image metadata."""

    storage_path: str
    width: float
    height: float

    model_config = LUMI_MODEL_CONFIG


class TableMetadata(BaseModel):
    """Class for image metadata."""

    html_string: str
    page_number: int
    accuracy: float

    model_config = LUMI_MODEL_CONFIG
