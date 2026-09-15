# ADR 001: Use n8n as the orchestration boundary

**Status:** Accepted  
**Date:** 2026-09-15

## Context

The portfolio target includes workflow-platform experience, integrations, queueing, retries, and versioned exports. A pure Python service would demonstrate backend skills but would not show how an automation engineer operates a workflow platform.

## Decision

Use self-hosted n8n for channel triggers, routing, notifications, sub-workflow composition, and operational visibility. Keep classification and safety-sensitive contract validation in a small typed Python service.

## Consequences

The workflow is inspectable and easy to connect to email, Slack, and CRM systems. Business logic remains testable outside n8n and can later move to a service without rewriting the orchestration layer. n8n exports must be versioned and credentials must never be exported.
