# Warashibe Headquarters

Last updated: 2026-10-03
Status: HQ v1 initial strategy

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
- Real external buy/sell cycle: not verified.
- Controlled automation: not authorized.

## Current bottleneck

`real_external_single_item_pilot_not_verified`

## Active strategy

`real_pilot_readiness -> one_item_live_proof -> learning_feedback -> capital_velocity_improvement`

## Strategic question

What single bottleneck, if removed now, most directly improves progress toward the JPY 1,000,000 North Star?

## Operating rule

At the start of a Warashibe development session or scheduled development cycle:

1. Read this HQ source.
2. Check verified current project/runtime state.
3. Read recent strategy decisions only when needed.
4. Identify one current bottleneck.
5. Select one strategic objective.
6. Execute only within existing permissions and Human Gate boundaries.
7. Collect evidence.
8. Record a material strategy decision when strategy actually changes.
9. Update this document only when the current strategy changes.

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
