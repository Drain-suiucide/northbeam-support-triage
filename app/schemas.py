from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Channel(StrEnum):
    email = "email"
    slack = "slack"
    web = "web"


class TicketType(StrEnum):
    lead = "lead"
    support = "support"
    complaint = "complaint"
    gdpr_request = "gdpr_request"
    spam = "spam"
    other = "other"


class Urgency(StrEnum):
    low = "low"
    normal = "normal"
    high = "high"
    critical = "critical"


class Contact(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str | None = None
    name: str | None = None
    company: str | None = None
    phone_e164: str | None = None


class Inquiry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    external_id: str = Field(min_length=1, max_length=160)
    channel: Channel
    subject: str = Field(default="", max_length=500)
    body: str = Field(min_length=1, max_length=20_000)
    received_at: str
    contact: Contact = Field(default_factory=Contact)


class TriageResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    inquiry: Inquiry
    ticket_type: TicketType
    urgency: Urgency
    language: Literal["en", "de", "fr", "unknown"]
    sentiment: Literal["positive", "neutral", "negative"]
    confidence: float = Field(ge=0, le=1)
    contact_match: Literal["matched", "created", "ambiguous", "not_found"]
    crm_action: Literal["create_ticket", "create_deal", "create_gdpr_task", "ignore"]
    draft_reply: str | None = None
    reply_requires_approval: bool = True
    gdpr_deadline_days: int | None = Field(default=None, ge=0)
    sla_escalation_minutes: int | None = Field(default=None, ge=0)
    safety_flags: list[str] = Field(default_factory=list)

    @field_validator("draft_reply")
    @classmethod
    def reject_unapproved_auto_reply(cls, value: str | None) -> str | None:
        return value


class ProcessResponse(BaseModel):
    request_id: str
    result: TriageResult
    crm_record: dict[str, str | int | bool]
    notifications: list[str]


class HealthResponse(BaseModel):
    status: Literal["ok"]
    mode: str
