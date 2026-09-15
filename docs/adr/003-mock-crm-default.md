# ADR 003: Default to a mock CRM adapter

**Status:** Accepted  
**Date:** 2026-09-15

## Context

A public portfolio repository must run without exposing HubSpot or Slack credentials and without writing arbitrary demo data to a real customer system.

## Decision

The default provider is `mock`. The workflow contains an explicit adapter branch for HubSpot, selected through configuration. Credentials are configured inside n8n or a deployment secret store and never stored in exported JSON.

## Consequences

Anyone can reproduce the demo locally. The integration seam is still visible to a reviewer, while production deployment retains responsibility for scopes, consent, retention, rate limits, and audit logging.
