# Warashibe Headquarters

Last updated: 2026-10-03
Status: HQ v1.1 CEO-to-COO operating model

## Governance

- Human CEO owns the North Star, constraints, major strategic changes, and Human Gate approvals.
- GPT Headquarters acts as the COO layer: it interprets CEO direction, selects the current bottleneck, ranks work, routes execution, and reviews evidence.
- Research / Development / Operator layers execute only within their existing permissions.
- Auditor evidence returns to HQ before strategy is changed.

HQ never self-authorizes a Human Gate action.

## North Star

Approximately JPY 3,000 -> exactly one item at a time -> JPY 1,000,000.

## Strategic priority

1. Commerce Loop
2. Capital Velocity
3. Learning Loop

PG count, code volume, research volume, and guardrail count are not top-level KPIs.

## Current state

- Warashibe Loop v2 synthetic one-cycle proof: complete.
- Settlement and next-capital handoff: complete.
- Capital Velocity: implemented.
- Learning Loop entry: complete.
- HQ v1 strategy memory: complete.
- HQ v1.1 CEO Directive / Priority Queue / Escalation / Strategy Review: implemented.
- Real external buy/sell cycle: not verified.
- Controlled automation: not authorized.

## Current bottleneck

`real_external_single_item_pilot_not_verified`

## Active strategy

`real_pilot_readiness -> one_item_live_proof -> learning_feedback -> capital_velocity_improvement`

## CEO Directive contract

CEO input may be converted into a durable directive only when it changes or constrains strategy.

Each material directive should contain:

- directive key
- instruction
- objective
- constraints
- issued time

Ordinary conversation is not automatically treated as a durable strategy change.

## Priority Queue contract

HQ ranks work by:

- North Star impact
- bottleneck relief
- evidence strength
- readiness
- cost

Any candidate that crosses the Human Gate is removed from normal execution ordering and escalated to the CEO.

## Escalation contract

The following always require CEO / Human Gate approval before execution:

- real purchase
- real payment
- real listing or sale
- real-money movement
- secrets/auth changes
- destructive database changes
- risky production changes
- North Star changes
- Human Gate changes

HQ may research, prepare, compare, simulate, and recommend these actions, but cannot execute them by itself.

## Strategy Review Loop

At a development endpoint or material evidence checkpoint:

1. Compare current evidence with the active bottleneck.
2. If the bottleneck remains, maintain strategy.
3. If the bottleneck is verified as resolved, advance to the next bottleneck.
4. If a material CEO Directive changes the objective or constraints, replan.
5. Record a material strategy decision in Supabase.
6. Update this document only when the current strategy changes.

## Operating rule

At the start of a Warashibe development session or scheduled development cycle:

1. Read this HQ source.
2. Check verified current project/runtime state.
3. Read recent strategy decisions only when needed.
4. Apply any material CEO Directive.
5. Identify one current bottleneck.
6. Rank candidate work in the Priority Queue.
7. Select one strategic objective that does not cross the Human Gate.
8. Route execution to the appropriate worker/tool.
9. Collect exact evidence.
10. Run Strategy Review.
11. Record a material strategy decision when strategy actually changes.

Do not create strategy churn from every successful PG.

## Human Gate

HQ may recommend and prepare real-pilot work, but it cannot independently authorize:

- real purchase
- real payment
- real listing or sale
- real-money movement
- secrets/auth changes
- destructive database changes
- risky main/production changes

## Runtime evidence

Deployment evidence uses the existing lookup order:

`Supabase runtime status -> Render connector -> Firecrawl`

Runtime evidence informs HQ; it never grants execution authority.

## Strategy memory

Historical material strategy decisions are stored append-only in:

`public.warashibe_strategy_decisions`

The GitHub HQ document is the current strategy source. Supabase is the durable decision-history ledger.
