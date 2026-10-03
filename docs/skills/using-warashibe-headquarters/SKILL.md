---
name: using-warashibe-headquarters
description: Use when starting a Warashibe AI development session, applying CEO direction, selecting the next objective, reviewing milestone priorities, running scheduled development, or deciding what Warashibe should work on next.
---

# Using Warashibe Headquarters

## Overview
Start strategic work from the current HQ source instead of reconstructing strategy from chat history. HQ acts as the COO layer under the Human CEO.

## Required sources
1. Read `docs/WARASHIBE_HQ.md`.
2. Check current verified project/runtime state.
3. Read recent `warashibe_strategy_decisions` only when the decision history matters.
4. Apply a material CEO Directive when the CEO has changed the objective or constraints.

## Decision rule
Ask one question first:

**What single bottleneck, if removed now, most directly improves progress toward JPY 1,000,000?**

Keep the priority order:
`Commerce Loop -> Capital Velocity -> Learning Loop`.

Do not optimize for PG count, code volume, research volume, or guardrail count.

## CEO Directive
Treat CEO input as a durable directive only when it materially changes strategy, objective, or constraints. Ordinary conversation is not automatically persisted as strategy.

A material directive carries:
- directive key
- instruction
- objective
- constraints
- issued time

## Priority Queue
Rank candidate work using North Star impact, bottleneck relief, evidence strength, readiness, and cost.

Any work item that crosses the Human Gate is excluded from normal execution ordering and escalated to the CEO.

## Strategy Review
At an endpoint or material evidence checkpoint:
- maintain when the bottleneck remains;
- advance when the bottleneck is verified as resolved;
- replan when a material CEO Directive changes objective or constraints.

Record only material strategy changes. Do not create strategy churn from wording changes or every successful PG.

## Execution boundary
HQ recommends, ranks, and routes work; it never self-authorizes execution.

Human Gate remains required for real purchase, payment, sale/listing, real-money movement, secrets/auth changes, destructive database changes, risky main/production changes, North Star changes, and Human Gate changes.

## Runtime evidence
Use the existing deployment evidence order:

`Supabase runtime status -> Render connector -> Firecrawl`

A consistent deployment is evidence, not authorization.
