from __future__ import annotations

from typing import Annotated, Literal
from pydantic import BaseModel, Field, ConfigDict, StringConstraints

EvidenceClass = Literal["verified", "inferred", "unknown"]
Severity = Literal["info", "low", "medium", "high"]


class Evidence(BaseModel):
    id: str
    evidence_class: EvidenceClass
    severity: Severity
    title: str
    detail: str
    source: str
    weight: float = Field(default=0.0, ge=-1.0, le=1.0)


class ContentCredentials(BaseModel):
    status: Literal['verified', 'untrusted', 'invalid', 'absent', 'unavailable', 'external']
    detail: str = Field(max_length=1000)
    signer: str | None = Field(default=None, max_length=256)
    tool: str | None = Field(default=None, max_length=256)
    declaration: Literal['generated', 'edited'] | None = None
    signed_at: str | None = Field(default=None, max_length=256)
    validation_state: str | None = Field(default=None, max_length=256)
    trust_list: str | None = Field(default=None, max_length=256)
    validation_codes: list[str] = Field(default_factory=list, max_length=12)


class Action(BaseModel):
    title: str
    detail: str


class AnalysisReport(BaseModel):
    kind: Literal["text", "url", "email", "image", "call"]
    risk_index: int | None = Field(ge=0, le=100)
    risk_level: Literal["low", "guarded", "high", "critical"]
    confidence: Literal["low", "medium", "high"]
    summary: str
    evidence: list[Evidence]
    limitations: list[str]
    content_credentials: ContentCredentials | None = None
    model_ran: bool | None = None
    decision_basis: Literal['model', 'content_credentials', 'rules'] = 'model'
    actions: list[Action] = Field(default_factory=list)
    share_summary: str = ''


class InputRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')


class TextRequest(InputRequest):
    text: str = Field(min_length=1, max_length=30000)


class UrlRequest(InputRequest):
    url: Annotated[str, StringConstraints(strip_whitespace=False)] = Field(min_length=1, max_length=4096)
    claimed_brand: str | None = Field(default=None, max_length=100)
    known_website: Annotated[str, StringConstraints(strip_whitespace=False)] | None = Field(default=None, min_length=1, max_length=4096)


class EmailRequest(InputRequest):
    raw_email: str = Field(min_length=1, max_length=250000)


class CallRequest(InputRequest):
    transcript: str = Field(min_length=1, max_length=30000)
