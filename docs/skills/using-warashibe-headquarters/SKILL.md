---
name: using-warashibe-headquarters
description: Use when starting a Warashibe AI development session, selecting the next objective, reviewing milestone priorities, running scheduled development, or deciding what Warashibe should work on next.
---

# Using Warashibe Headquarters

## Overview
Start strategic work from the current HQ source instead of reconstructing strategy from chat history.

## Required sources
1. Read `docs/WARASHIBE_HQ.md`.
2. Check current verified project/runtime state.
3. Read recent `warashibe_strategy_decisions` only when the decision history matters.

## Decision rule
Ask one question first:

**What single bottleneck, if removed now, most directly improves progress toward JPY 1,000,000?**

Keep the priority order:
`Commerce Loop -> Capital Velocity -> Learning Loop`.

Do not optimize for PG count, code volume, research volume, or guardrail count.

## Strategy updates
Record a strategy decision only for a material change in bottleneck or active strategy. Do not create strategy churn from wording changes or every successful PG.

Update `WARASHIBE_HQ.md` only when the current strategy actually changes.

## Execution boundary
HQ recommends and routes work; it never self-authorizes execution.

Human Gate remains required for real purchase, payment, sale/listing, real-money movement, secrets/auth changes, destructive database changes, and risky main/production changes.

## Runtime evidence
Use the existing deployment evidence order:

`Supabase runtime status -> Render connector -> Firecrawl`

A consistent deployment is evidence, not authorization.
