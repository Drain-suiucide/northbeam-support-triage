from uuid import uuid4

from fastapi import FastAPI, Request

from app.schemas import HealthResponse, Inquiry, ProcessResponse
from app.service import process

app = FastAPI(title="Northbeam Support Triage", version="0.1.0")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", mode="mock-crm / deterministic-demo")


@app.post("/v1/triage", response_model=ProcessResponse)
def triage(inquiry: Inquiry, request: Request) -> ProcessResponse:
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    return process(inquiry, request_id)


@app.get("/v1/demo/{case}", response_model=ProcessResponse)
def demo(case: str) -> ProcessResponse:
    fixtures = {
        "urgent-complaint": Inquiry.model_validate({"external_id": "demo-complaint-001", "channel": "email", "subject": "Urgent complaint", "body": "We are unhappy and this problem is urgent. Please help ASAP.", "received_at": "2026-09-15T12:00:00Z", "contact": {"email": "ops@acme.test", "name": "Marie Schmidt", "company": "Acme GmbH"}}),
        "gdpr-delete": Inquiry.model_validate({"external_id": "demo-gdpr-001", "channel": "web", "subject": "Please delete my data", "body": "Please delete my data under GDPR. I need confirmation.", "received_at": "2026-09-15T12:01:00Z", "contact": {"email": "user@example.test", "name": "Jean Martin"}}),
        "new-lead": Inquiry.model_validate({"external_id": "demo-lead-001", "channel": "slack", "subject": "Pricing and demo", "body": "Hello, please send pricing and book a demo for our team.", "received_at": "2026-09-15T12:02:00Z", "contact": {"email": "buyer@example.test", "company": "Northwind"}}),
    }
    if case not in fixtures:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Unknown demo case")
    return process(fixtures[case], f"demo-{case}")
