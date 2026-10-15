"""Validated controller/worker contracts. Unknown fields are always rejected."""
from __future__ import annotations

from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

Id = Annotated[str, Field(pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}$")]
Digest = Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
ToolName = Literal["read_input", "discover_capabilities", "write_unit", "build_artifact", "render_preview", "technical_qa"]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)


class InputReference(Contract):
    id: Id
    path: str = Field(min_length=1, max_length=1024)
    sha256: Digest
    role: Literal["brief", "reference", "editable_source"]


class DesignUnit(Contract):
    id: Id
    kind: Literal["slide", "artboard", "graphic", "page", "spread", "composition", "glyph"]
    width: int = Field(ge=64, le=4096)
    height: int = Field(ge=64, le=4096)
    instruction: str = Field(min_length=1, max_length=12000)
    source_slide: int | None = Field(default=None, ge=1, le=200)
    layout: Id | None = None


Font = Literal["Arial", "Calibri", "Aptos", "Georgia", "Times New Roman", "Verdana"]
Color = Annotated[str, Field(pattern=r"^#[0-9a-fA-F]{6}$")]


class PresentationContract(Contract):
    structure: Literal["flat", "structured", "preserve"]
    reusable_template: bool = False
    title_size: float = Field(ge=8, le=200)
    body_size: float = Field(ge=8, le=200)
    title_font: Font
    body_font: Font
    background: Color
    foreground: Color
    accent: Color


class EditorialStyle(Contract):
    id: Id
    font: Font
    size: float = Field(ge=8, le=100)
    leading: float = Field(ge=8, le=180)
    color: Color
    bold: bool = False


class EditorialContract(Contract):
    margin: float = Field(ge=0, le=500)
    columns: int = Field(ge=1, le=12)
    gutter: float = Field(ge=0, le=200)
    bleed: float = Field(default=0, ge=0, le=100)
    styles: list[EditorialStyle] = Field(min_length=1, max_length=20)

    @model_validator(mode="after")
    def styles_valid(self):
        if len({s.id for s in self.styles}) != len(self.styles) or any(s.leading < s.size for s in self.styles):
            raise ValueError("Duplicate style or leading smaller than font size")
        return self


class ApprovalPolicy(Contract):
    approver: Literal["main"] = "main"
    require_render: Literal[True] = True
    require_native_editability: bool = True
    max_revisions: int = Field(default=2, ge=0, le=5)
    allow_paid_model: bool = False


class DesignTask(Contract):
    parent_request_id: Id
    stage: Id
    operation: Literal["create", "edit", "refine", "assets", "render", "qa", "repair", "brainstorm", "prompt", "other"]
    artifact_type: str = Field(min_length=1, max_length=80)
    units: list[DesignUnit] = Field(min_length=1, max_length=20)
    inputs: list[InputReference] = Field(min_length=1, max_length=20)
    output_format: str = Field(min_length=1, max_length=20)
    editability_requirements: list[Annotated[str, Field(min_length=1, max_length=1000)]] = Field(min_length=1, max_length=20)
    required_features: list[Annotated[str, Field(min_length=1, max_length=80)]] = Field(default_factory=lambda: ["editable_text", "editable_shapes"], max_length=20)
    allowed_tools: list[ToolName] = Field(min_length=1, max_length=6)
    output_dir: str = Field(min_length=1, max_length=1024)
    creative_constraints: str = Field(min_length=1, max_length=20000)
    authorized: bool = False
    no_execution: bool = False
    revision: int = Field(default=0, ge=0, le=5)
    approval_policy: ApprovalPolicy = Field(default_factory=ApprovalPolicy)
    timeout_seconds: int = Field(default=180, ge=10, le=300)
    max_tool_calls: int = Field(default=48, ge=3, le=80)
    presentation: PresentationContract | None = None
    editorial: EditorialContract | None = None

    @model_validator(mode="after")
    def unique_scope(self):
        for values in ([x.id.casefold() for x in self.units], [x.id.casefold() for x in self.inputs], self.allowed_tools):
            if len(values) != len(set(values)):
                raise ValueError("Duplicate unit, input, or tool ID")
        reserved = {"con", "prn", "aux", "nul", "design", "unit-order", "render-checks", *[f"com{i}" for i in range(1,10)], *[f"lpt{i}" for i in range(1,10)]}
        if any(u.id.casefold() in reserved for u in self.units):
            raise ValueError("Unit ID conflicts with a reserved output filename")
        if self.revision > self.approval_policy.max_revisions:
            raise ValueError("Revision limit exceeded")
        if not any(x.role == "brief" for x in self.inputs):
            raise ValueError("An authoritative brief and SHA256 are required")
        slide_indices = [u.source_slide for u in self.units if u.source_slide is not None]
        if len(set(slide_indices)) != len(slide_indices):
            raise ValueError('Duplicate source slide assignment')
        if any(u.id.casefold() in {'publication','native-contract','flow-receipt','web-audit','web-preview','roundtrip','scratch'} for u in self.units):
            raise ValueError('Unit ID conflicts with a reserved medium output')
        return self


class DesignHookDecision(Contract):
    eligible: bool
    reason: str
    task_id: str | None = None
    profile: str | None = None
    duplicate: bool = False


class ArtifactManifest(Contract):
    path: str
    sha256: Digest
    format: str
    unit_ids: list[str]
    editable: bool
    role: Literal["source", "deliverable", "preview", "evidence"]


class DesignQAReport(Contract):
    status: Literal["PASS", "FAIL", "UNVERIFIED"]
    checks: list[str]
    issues: list[str]
    evidence: list[ArtifactManifest]


class DesignResult(Contract):
    task_id: str
    status: Literal["NEEDS_MAIN_REVIEW", "FAILED", "BLOCKED", "UNVERIFIED"]
    artifacts: list[ArtifactManifest]
    qa: DesignQAReport
    issues: list[str]


class MainReviewDecision(Contract):
    task_id: Id
    decision: Literal["APPROVE", "REVISE", "BLOCK"]
    reviewer: Literal["main"]
    artifact_hashes: list[Digest]
    feedback: str = Field(min_length=1, max_length=12000)


class Node(Contract):
    """Safe editable primitives; deliberately excludes executable markup and resource URLs."""
    id: Id
    kind: Literal["rect", "ellipse", "text", "line", "chart", "table", "text_frame"]
    x: float = Field(ge=0, le=4096)
    y: float = Field(ge=0, le=4096)
    width: float = Field(gt=0, le=4096)
    height: float = Field(gt=0, le=4096)
    fill: str = Field(default="#000000", pattern=r"^(#[0-9a-fA-F]{6}|none)$")
    stroke: str = Field(default="none", pattern=r"^(#[0-9a-fA-F]{6}|none)$")
    stroke_width: float = Field(default=1, ge=0, le=20)
    radius: float = Field(default=0, ge=0, le=200)
    text: str = Field(default="", max_length=2000)
    font: Literal["Arial", "Calibri", "Aptos", "Georgia", "Times New Roman", "Verdana"] = "Arial"
    font_size: float = Field(default=24, ge=8, le=200)
    bold: bool = False
    placeholder: bool = False
    layer: Literal["slide", "layout", "master"] = "slide"
    native_placeholder: Literal["title", "subtitle", "body", "picture", "chart", "table", "footer", "slide-number"] | None = None
    placeholder_index: int = Field(default=0, ge=0, le=1000)
    chart: ChartData | None = None
    table: TableData | None = None
    story_id: Id | None = None

    @model_validator(mode="after")
    def payload(self):
        for kind, value in (("chart", self.chart), ("table", self.table), ("text_frame", self.story_id)):
            if (self.kind == kind) != (value is not None):
                raise ValueError("Node kind and native payload must match")
        if self.native_placeholder and self.layer != "slide":
            raise ValueError("Placeholder carriers belong to slide content")
        if self.native_placeholder == 'picture' and self.kind != 'rect':
            raise ValueError('Native picture placeholder requires an empty rectangular slot')
        return self


class ChartSeries(Contract):
    name: str = Field(min_length=1, max_length=100)
    values: list[float] = Field(min_length=1, max_length=40)


class ChartData(Contract):
    type: Literal["column", "bar", "line", "pie"]
    categories: list[Annotated[str, Field(min_length=1, max_length=100)]] = Field(min_length=1, max_length=40)
    series: list[ChartSeries] = Field(min_length=1, max_length=8)

    @model_validator(mode="after")
    def rectangular(self):
        if any(len(s.values) != len(self.categories) for s in self.series):
            raise ValueError("Chart category and series lengths differ")
        return self


class TableData(Contract):
    columns: list[Annotated[str, Field(max_length=100)]] = Field(min_length=1, max_length=12)
    rows: list[list[Annotated[str, Field(max_length=200)]]] = Field(min_length=1, max_length=40)

    @model_validator(mode="after")
    def rectangular(self):
        if any(len(r) != len(self.columns) for r in self.rows):
            raise ValueError("Table row and column lengths differ")
        return self


class TextEdit(Contract):
    shape_id: int = Field(ge=1, le=2147483647)
    expected: str = Field(min_length=1, max_length=2000)
    replacement: str = Field(min_length=1, max_length=2000)


class Story(Contract):
    id: Id
    style: Id
    text: str = Field(min_length=1, max_length=60000)


class UnitContent(Contract):
    unit_id: Id
    nodes: list[Node] = Field(default_factory=list, max_length=300)
    edits: list[TextEdit] = Field(default_factory=list, max_length=50)
    stories: list[Story] = Field(default_factory=list, max_length=30)


Node.model_rebuild()


class ReadInput(Contract):
    input_id: Id


class Empty(Contract):
    pass
