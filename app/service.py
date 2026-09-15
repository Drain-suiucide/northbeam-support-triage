from dataclasses import dataclass

from app.schemas import Inquiry, ProcessResponse, TicketType, TriageResult, Urgency


@dataclass(frozen=True)
class Classification:
    ticket_type: TicketType
    urgency: Urgency
    language: str
    sentiment: str
    confidence: float


KEYWORDS: dict[TicketType, tuple[str, ...]] = {
    TicketType.gdpr_request: ("delete my data", "löschung", "supprimer mes données", "gdpr"),
    TicketType.complaint: ("complaint", "unhappy", "beschwerde", "réclamation", "terrible"),
    TicketType.lead: ("pricing", "demo", "angebot", "angeboten", "devis", "buy"),
    TicketType.support: ("error", "login", "broken", "fehler", "problème", "problem"),
    TicketType.spam: ("unsubscribe", "casino", "crypto giveaway"),
}

LANGUAGE_MARKERS = {
    "de": ("hallo", "bitte", "fehler", "löschung", "rechnung"),
    "fr": ("bonjour", "merci", "problème", "réclamation", "supprimer"),
    "en": ("hello", "please", "error", "delete", "pricing"),
}


def classify(inquiry: Inquiry) -> Classification:
    text = f"{inquiry.subject} {inquiry.body}".lower()
    scores = {kind: sum(marker in text for marker in markers) for kind, markers in KEYWORDS.items()}
    ticket_type = max(scores, key=lambda kind: scores[kind])
    if scores[ticket_type] == 0:
        ticket_type = TicketType.other
    language = max(LANGUAGE_MARKERS, key=lambda lang: sum(x in text for x in LANGUAGE_MARKERS[lang]))
    if not any(x in text for x in LANGUAGE_MARKERS[language]):
        language = "unknown"
    urgent = any(x in text for x in ("urgent", "asap", "sofort", "dringend", "urgence"))
    negative = any(x in text for x in ("angry", "unhappy", "terrible", "beschwerde", "réclamation"))
    urgency = Urgency.critical if ticket_type == TicketType.gdpr_request and urgent else Urgency.high if urgent or ticket_type == TicketType.complaint else Urgency.normal
    confidence = min(0.97, 0.58 + scores[ticket_type] * 0.12) if ticket_type != TicketType.other else 0.42
    return Classification(ticket_type, urgency, language, "negative" if negative else "neutral", confidence)


def process(inquiry: Inquiry, request_id: str) -> ProcessResponse:
    result = classify(inquiry)
    flags: list[str] = []
    text = f"{inquiry.subject} {inquiry.body}".lower()
    if "ignore previous instructions" in text or "system prompt" in text:
        flags.append("security.prompt_injection_suspected")
    contact_match = "matched" if inquiry.contact.email else "not_found"
    if inquiry.contact.email and inquiry.contact.email.endswith("@example.test"):
        contact_match = "created"
    if result.ticket_type == TicketType.gdpr_request:
        crm_action = "create_gdpr_task"
        draft = None
        deadline = 30
    elif result.ticket_type == TicketType.lead:
        crm_action = "create_deal"
        draft = f"Thanks for reaching out. We received your request and will follow up in {result.language} shortly."
        deadline = None
    elif result.ticket_type == TicketType.spam:
        crm_action = "ignore"
        draft = None
        deadline = None
    else:
        crm_action = "create_ticket"
        draft = None if result.ticket_type == TicketType.complaint else "Thanks for contacting Northbeam. Our team is reviewing your request."
        deadline = None
    if flags:
        crm_action = "create_ticket"
    record = {"provider": "mock", "action": crm_action, "external_id": inquiry.external_id, "requires_human_approval": True}
    notifications = ["slack:triage-review"] if result.urgency in (Urgency.high, Urgency.critical) or flags else []
    triage = TriageResult(  # type: ignore[arg-type]
        inquiry=inquiry, ticket_type=result.ticket_type, urgency=result.urgency,
        language=result.language,  # type: ignore[arg-type]
        sentiment=result.sentiment,  # type: ignore[arg-type]
        confidence=result.confidence,
        contact_match=contact_match,  # type: ignore[arg-type]
        crm_action=crm_action,  # type: ignore[arg-type]
        draft_reply=draft,
        reply_requires_approval=True, gdpr_deadline_days=deadline,
        sla_escalation_minutes=30 if result.urgency in (Urgency.high, Urgency.critical) else 240,
        safety_flags=flags,
    )
    return ProcessResponse(request_id=request_id, result=triage, crm_record=record, notifications=notifications)  # type: ignore[arg-type]
