# Warashibe GPT Headquarters v1 — Endpoint

Date: 2026-10-03
Status: implementation complete pending exact-SHA deployment verification

## Implemented

- Current strategy source: `docs/WARASHIBE_HQ.md`
- HQ contract: `research_lab/headquarters.py`
- HQ contract test: `research_lab/test_headquarters.py`
- Append-only strategy repository: `research_lab/supabase_strategy_decision_repository.py`
- Repository contract test: `research_lab/test_supabase_strategy_decision_repository.py`
- Supabase migration source: `docs/migrations/2026-10-03_strategy_decisions.sql`
- HQ skill: `docs/skills/using-warashibe-headquarters/SKILL.md`
- Skills index: `docs/WARASHIBE_SKILLS.md`

## TDD evidence

- HQ contract RED: CI #1261 failure after activation.
- HQ contract GREEN: CI #1263 success after implementation.
- Strategy repository RED: CI #1265 failure after activation.
- Strategy repository GREEN: CI #1266 success after implementation.
- Migration source: CI #1267 success.
- HQ skill: CI #1268 success.

## Supabase proof

`public.warashibe_strategy_decisions` exists with RLS enabled and anon/authenticated access revoked.

Initial decision:
- decision_key: `hq-v1-initial`
- status: `active`
- strategy: `real_pilot_readiness -> one_item_live_proof -> learning_feedback -> capital_velocity_improvement`

## HQ operating rule

At session/scheduled-development start:

`HQ source -> verified runtime/project state -> recent strategy memory when needed -> single bottleneck -> strategic objective -> execution -> evidence -> material decision record`

HQ never self-authorizes execution.

## Human Gate

Real purchase, payment, sale/listing, real-money movement, secrets/auth changes, destructive DB changes, and risky main/production changes remain explicitly human-gated.

## Strategic endpoint

Current bottleneck:

`real_external_single_item_pilot_not_verified`

Current active strategy:

`real_pilot_readiness -> one_item_live_proof -> learning_feedback -> capital_velocity_improvement`

The next development cycle should begin from this HQ state rather than selecting the next PG mechanically.
