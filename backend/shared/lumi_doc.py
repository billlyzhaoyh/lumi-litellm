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
from typing import Optional

from pydantic import BaseModel

from shared.types import LUMI_MODEL_CONFIG, ArxivMetadata, LoadingStatus


class Position(BaseModel):
    """Position within a text span"""

    start_index: int
    end_index: int

    model_config = LUMI_MODEL_CONFIG


class Highlight(BaseModel):
    """Text highlight with color and position"""

    color: str
    span_id: str
    position: Position

    model_config = LUMI_MODEL_CONFIG


class Citation(BaseModel):
    """Citation reference to a span"""

    span_id: str
    position: Position

    model_config = LUMI_MODEL_CONFIG


class CitedContent(BaseModel):
    """Content with citations"""

    text: str
    citations: list[Citation]

    model_config = LUMI_MODEL_CONFIG


class Label(BaseModel):
    """Label with ID"""

    id: str
    label: str

    model_config = LUMI_MODEL_CONFIG


class LumiSummary(BaseModel):
    """Summary of a section, content, or span"""

    id: str
    summary: "LumiSpan"

    model_config = LUMI_MODEL_CONFIG


class LumiSummaries(BaseModel):
    """Collection of summaries for a document"""

    section_summaries: list[LumiSummary]
    content_summaries: list[LumiSummary]
    span_summaries: list[LumiSummary]
    abstract_excerpt_span_id: str | None = None

    model_config = LUMI_MODEL_CONFIG


class Heading(BaseModel):
    """Section heading"""

    heading_level: int
    text: str

    model_config = LUMI_MODEL_CONFIG


class ConceptContent(BaseModel):
    """Content for a concept (key-value pair)"""

    label: str
    value: str

    model_config = LUMI_MODEL_CONFIG


class LumiConcept(BaseModel):
    """A concept extracted from the document"""

    id: str
    name: str
    contents: list[ConceptContent]
    in_text_citations: list[Label]

    model_config = LUMI_MODEL_CONFIG


class LumiSection(BaseModel):
    """A section of the document"""

    id: str
    heading: Heading
    contents: list["LumiContent"]
    sub_sections: list["LumiSection"] | None = None

    model_config = LUMI_MODEL_CONFIG


class TextContent(BaseModel):
    """Text content with spans"""

    tag_name: str
    spans: list["LumiSpan"]

    model_config = LUMI_MODEL_CONFIG


class ImageContent(BaseModel):
    """Image content with metadata"""

    storage_path: str
    latex_path: str
    alt_text: str
    width: float
    height: float
    caption: Optional["LumiSpan"] = None

    model_config = LUMI_MODEL_CONFIG


class FigureContent(BaseModel):
    """Figure content with images and caption"""

    images: list[ImageContent]
    caption: Optional["LumiSpan"] = None

    model_config = LUMI_MODEL_CONFIG


class HtmlFigureContent(BaseModel):
    """HTML figure content"""

    html: str
    caption: Optional["LumiSpan"] = None

    model_config = LUMI_MODEL_CONFIG


class ListContent(BaseModel):
    """List content (ordered or unordered)"""

    list_items: list["ListItem"]
    is_ordered: bool

    model_config = LUMI_MODEL_CONFIG


class ListItem(BaseModel):
    """A list item with optional sub-list"""

    spans: list["LumiSpan"]
    subListContent: ListContent | None = None

    model_config = LUMI_MODEL_CONFIG


class LumiContent(BaseModel):
    """Content element in a document (text, image, figure, list, etc.)"""

    id: str
    text_content: TextContent | None = None
    image_content: ImageContent | None = None
    figure_content: FigureContent | None = None
    html_figure_content: HtmlFigureContent | None = None
    list_content: ListContent | None = None

    model_config = LUMI_MODEL_CONFIG


class LumiSpan(BaseModel):
    """A span of text with formatting tags"""

    id: str
    text: str
    inner_tags: list["InnerTag"]

    model_config = LUMI_MODEL_CONFIG


class InnerTagName(StrEnum):
    """Types of inner tags for text formatting"""

    BOLD = "b"
    ITALIC = "i"
    STRONG = "strong"
    EM = "em"
    UNDERLINE = "u"
    MATH = "math"
    MATH_DISPLAY = "math_display"
    REFERENCE = "ref"
    SPAN_REFERENCE = "spanref"
    CONCEPT = "concept"
    A = "a"
    CODE = "code"
    FOOTNOTE = "footnote"


class InnerTag(BaseModel):
    """An inner formatting tag within a span"""

    id: str
    tag_name: InnerTagName
    metadata: dict
    position: Position
    # These are additional recursive tags within the content of this inner tag.
    # This may happen if we have e.g. <b>[lumi-start-concept]...[lumi-end-concept]</b>
    children: list["InnerTag"]

    model_config = LUMI_MODEL_CONFIG


class LumiReference(BaseModel):
    """A reference/citation in the document"""

    id: str
    span: LumiSpan

    model_config = LUMI_MODEL_CONFIG


class LumiFootnote(BaseModel):
    """A footnote in the document"""

    id: str
    span: LumiSpan

    model_config = LUMI_MODEL_CONFIG


class LumiAbstract(BaseModel):
    """Abstract section of the document"""

    contents: list[LumiContent]

    model_config = LUMI_MODEL_CONFIG


class LumiDoc(BaseModel):
    """Complete Lumi document representation of a paper"""

    markdown: str
    sections: list[LumiSection]
    concepts: list[LumiConcept]
    abstract: LumiAbstract | None = None
    references: list[LumiReference] | None = None
    footnotes: list[LumiFootnote] | None = None
    summaries: LumiSummaries | None = None
    metadata: ArxivMetadata | None = None
    loading_status: LoadingStatus | None = LoadingStatus.UNSET
    loading_error: str | None = None

    model_config = LUMI_MODEL_CONFIG
