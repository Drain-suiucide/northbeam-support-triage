# Northbeam Support Triage

> A portfolio-grade multilingual customer-inquiry triage workflow built around self-hosted n8n, a typed Python service, and a CRM-safe approval boundary.

**Status:** portfolio v0.1, reproducible demo. All default data is synthetic. The default CRM provider is a mock adapter; HubSpot and Slack are optional integrations and require user-managed credentials.

## Why this project exists

Northbeam receives customer inquiries from email, Slack Connect, and a website form. The workflow normalizes every channel into one contract, classifies the inquiry, extracts routing fields, deduplicates the contact, creates a CRM-safe action, and sends uncertain or sensitive cases to human review.

The important design choice is that **a generated draft is never an automatic customer reply**. Complaints and GDPR requests are never auto-replied. GDPR requests become a separately tracked task, and urgent cases trigger a review notification.

## Architecture

```text
Email / Slack / Website webhook
              |
              v
      n8n Main Router (queue mode)
              |
              v
   Typed triage service /v1/triage
              |
     +--------+---------+
     |                  |
  CRM sub-workflow   Review notification
     |                  |
     +--------+---------+
              v
    Mock CRM or HubSpot adapter

Error Trigger -> normalize error -> Slack alert + retryable record
PostgreSQL stores n8n state; Redis provides the execution queue; two workers process jobs.
```

## What the demo proves

| Scenario | Route | Safety behavior |
|---|---|---|
| Urgent complaint | `create_ticket` | No reply draft; review notification |
| GDPR deletion request | `create_gdpr_task` | Separate task, 30-day tracking field, no auto-reply |
| New lead | `create_deal` | Draft is marked `reply_requires_approval=true` |
| Prompt-injection text | `create_ticket` | Security flag; document cannot authorize an action |

## Run the Python demo

Python 3.11+ and `uv` are recommended.

```bash
cp .env.example .env
uv sync --extra dev
uv run uvicorn app.main:app --reload --port 8010
```

Open the API docs at `http://127.0.0.1:8010/docs`, or run:

```bash
curl http://127.0.0.1:8010/health
curl http://127.0.0.1:8010/v1/demo/urgent-complaint
curl http://127.0.0.1:8010/v1/demo/gdpr-delete
curl http://127.0.0.1:8010/v1/demo/new-lead
```

Post a normalized inquiry:

```bash
curl -X POST http://127.0.0.1:8010/v1/triage \
  -H 'Content-Type: application/json' \
  -H 'X-Request-ID: demo-001' \
  -d '{"external_id":"web-001","channel":"web","subject":"Pricing","body":"Hello, please send pricing and book a demo.","received_at":"2026-09-15T12:00:00Z","contact":{"email":"buyer@example.test","company":"Northwind"}}'
```

## Run n8n with PostgreSQL, Redis, and two workers

```bash
cp .env.example .env
docker compose up -d
```

Open `http://127.0.0.1:5678`. Import the three JSON files from `workflows/`:

1. `01-main-router.json` — inbound webhook, triage call, urgency branch, CRM sub-workflow.
2. `02-crm-routing.json` — safety guard and mock/HubSpot adapter branch.
3. `99-error-handler.json` — Error Trigger, alert, and retryable error record.

The exports deliberately contain no credentials. Configure credentials in n8n or environment-backed adapters. Stop the stack with `docker compose down`; add `-v` only when you intentionally want to remove local data.

## Quality gate

```bash
uv run --extra dev ruff check .
uv run --extra dev mypy app scripts
uv run --extra dev pytest
uv run --extra dev python scripts/evaluate.py
```

The initial regression set checks the critical routing decisions and safety invariants. It is not a claim of production classification accuracy. A serious deployment needs a manually labeled multilingual set, field-level metrics, complaint/GDPR recall, false-auto-reply rate, p50/p95 latency, and cost per inquiry.

## Production boundary

This repository intentionally does **not** send customer replies, delete personal data, or write to a real CRM by default. Before production use, add authentication, webhook signature verification, idempotency keys, contact deduplication backed by a real CRM, encrypted retention controls, rate limits, malware/content scanning, audit events, data-subject request tracking, model/version logging, and an approval UI.

## Design decisions

- [ADR 001: n8n as the orchestration boundary](docs/adr/001-n8n-orchestration.md)
- [ADR 002: approval boundary for customer replies](docs/adr/002-human-approval.md)
- [ADR 003: mock CRM by default](docs/adr/003-mock-crm-default.md)

## Portfolio talking point

> I used n8n for orchestration and operational visibility, but kept the business contract and safety invariants in typed code. The workflow can retry and scale through queue mode, while no model-generated draft can reach a customer without explicit approval.
