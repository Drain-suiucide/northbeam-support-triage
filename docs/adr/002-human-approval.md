# ADR 002: Require human approval before customer replies

**Status:** Accepted  
**Date:** 2026-09-15

## Context

A generated answer can be factually wrong, insensitive, or unsafe. Complaints and GDPR requests have a higher cost of error than ordinary low-risk support questions.

## Decision

Every generated draft carries `reply_requires_approval=true`. Complaint and GDPR routes have no draft by default. n8n may notify a reviewer or create a CRM task, but it may not send a customer-facing answer without an explicit approval workflow.

## Consequences

The demo has a lower apparent automation rate, but the authorization boundary is visible, auditable, and reversible. A later review UI can record the approver, timestamp, source evidence, and final text.
