# Warashibe GPT Headquarters Design

Date: 2026-10-03
Status: Proposed architecture for implementation
Branch: research-lab

## 1. Purpose

Create a persistent strategy layer so Warashibe AI does not reconstruct its strategy from scratch in every chat or scheduled development cycle.

The Headquarters (HQ) must preserve strategic intent across sessions while keeping real-world execution behind existing Human Gate controls.

## 2. North Star

Start with approximately JPY 3,000, trade exactly one item at a time, and grow capital toward JPY 1,000,000.

Strategic priority order remains:

1. Commerce Loop
2. Capital Velocity
3. Learning Loop

PG count, code volume, guardrail count, or research volume are not top-level KPIs.

## 3. Architecture

The HQ uses three layers.

### 3.1 GitHub strategy source

Canonical current strategy:

`docs/WARASHIBE_HQ.md`

This is the human-readable strategy source for:
- North Star
- current state
- current bottleneck
- active strategy
- explicit non-goals
- Human Gate boundaries
- next strategic review trigger

This file represents the current strategy, not the complete historical ledger.

### 3.2 Supabase strategy memory

Append-only table:

`public.warashibe_strategy_decisions`

This stores durable decision history so future GPT sessions can understand:
- what question was considered
- what decision was made
- why it was made
- what evidence supported it
- what result was expected
- what would invalidate it
- what later result occurred
- whether the decision is active, superseded, invalidated, or completed

Supabase is the strategy memory ledger. It is not an authorization system.

### 3.3 GPT HQ runtime

Module:

`research_lab/headquarters.py`

Its responsibility is to build a strategy snapshot from explicit inputs.

It must not:
- perform purchases
- perform payments
- list or sell real items
- alter secrets or authentication
- modify production/main destructively
- self-authorize controlled automation

The HQ produces recommendations and strategic routing only.

## 4. GPT operating modes

GPT-side reasoning is separated conceptually into three roles.

### HQ Mode
Reads current strategic state and identifies the single highest-value bottleneck relative to the North Star.

### Operator Mode
Executes approved development/research work inside existing tool and repository permissions.

### Auditor Mode
Checks whether claimed completion is supported by evidence such as tests, exact SHA CI, Render live state, Supabase proof, and milestone criteria.

A single implementation may run these roles sequentially, but the output contracts remain distinct.

## 5. HQ cycle

Each HQ cycle follows:

1. Read current HQ strategy.
2. Read current verified project/runtime state.
3. Read recent relevant strategy decisions when needed.
4. Identify the current bottleneck.
5. Select one strategic objective.
6. Route work to the appropriate development/research mechanism.
7. Collect evidence.
8. Record a strategy decision when a material strategic choice was made.
9. Update `WARASHIBE_HQ.md` only if the current strategy actually changed.

The cycle must not create strategy churn from every successful PG.

## 6. Initial HQ state

Initial current state:

- Warashibe Loop v2 synthetic one-cycle proof: complete.
- Settlement and next-capital handoff: complete.
- Capital Velocity: implemented.
- Learning Loop entry: complete.
- Real external buy/sell cycle: not verified.
- Controlled automation: not authorized.

Initial bottleneck:

`real_external_single_item_pilot_not_verified`

Initial active strategy:

`real_pilot_readiness -> one_item_live_proof -> learning_feedback -> capital_velocity_improvement`

## 7. Strategy decision record

Minimum fields:

- `id bigint identity primary key`
- `decision_key text unique not null`
- `strategic_question text not null`
- `decision text not null`
- `rationale text not null`
- `evidence jsonb not null default '{}'::jsonb`
- `expected_effect text not null`
- `invalidation_condition text not null`
- `result jsonb not null default '{}'::jsonb`
- `status text not null`
- `decided_at timestamptz not null`
- `created_at timestamptz not null default now()`

Allowed status values:

- `active`
- `superseded`
- `invalidated`
- `completed`

Initial implementation uses append-only inserts. No update/delete application workflow is required.

## 8. Supabase security contract

Because the table is in the exposed `public` schema:

- RLS must be enabled.
- No anon/authenticated access policy is created.
- privileges for `anon` and `authenticated` are revoked.
- service-side administrative access remains the intended path.
- no service-role secret is stored in repository files or strategy rows.

This follows the current Warashibe closed-by-default audit-table pattern.

## 9. Python contracts

### 9.1 Build strategy snapshot

`build_headquarters_snapshot(...)`

Inputs include:
- north_star
- priority_order
- current_state
- current_bottleneck
- active_strategy
- human_gate_required
- evidence
- observed_at

Output includes:
- `status = "headquarters_ready"`
- normalized priority order
- one current bottleneck
- one active strategy
- `human_gate_required = true`
- `execution_authorized = false`

### 9.2 Evaluate strategy transition

`evaluate_strategy_transition(current, candidate, evidence)`

The function returns whether the candidate represents a material strategy change.

Documentation-only wording changes must not create a new strategy decision.

### 9.3 Strategy repository

`research_lab/supabase_strategy_decision_repository.py`

Minimum API:
- `latest(limit=...)`
- `append(decision)`

No update/delete API is included in the first version.

## 10. TDD contract

Target tests will prove:

1. HQ snapshot always keeps Human Gate enabled.
2. HQ snapshot never self-authorizes execution.
3. the initial bottleneck is represented as one explicit value.
4. material strategy change is distinguishable from unchanged strategy.
5. strategy decision repository is append-only.
6. runner/build profile includes the HQ contract tests.

Development sequence:

contract test -> targeted RED -> minimal implementation -> exact-SHA CI success -> Supabase schema application/verification -> advisors -> Render same-SHA verification -> Runtime Status append -> Library/Skills sync.

## 11. Integration with existing runtime status

HQ must use the existing runtime lookup policy:

`Supabase runtime status -> Render connector -> Firecrawl`

Runtime status tells HQ whether deployment evidence is current and consistent.

Runtime status does not determine strategy by itself.

## 12. Integration with Skills

Add project skill:

`docs/skills/using-warashibe-headquarters/SKILL.md`

It should trigger when:
- starting a new Warashibe development session
- selecting the next development objective
- reviewing milestone priorities
- scheduled development begins
- a user asks what Warashibe should work on next

Skill management remains indexed in:

`docs/WARASHIBE_SKILLS.md`

## 13. Human Gate

HQ can recommend and prepare real-pilot work.

HQ cannot independently authorize:
- a real purchase
- a real payment
- a real listing or sale
- real-money movement
- secrets/auth changes
- destructive database changes
- risky main/production changes

Those require explicit Human Gate.

## 14. Failure behavior

If current strategy source is missing:
- fall back to the last known valid project policy and report HQ strategy as incomplete.

If strategy history is unavailable:
- continue with current GitHub strategy source but do not invent historical rationale.

If runtime state is stale or inconsistent:
- refresh through the existing runtime-status policy before declaring deployment evidence valid.

If evidence is insufficient:
- HQ may recommend research or validation, but must not mark the strategic objective complete.

## 15. Completion criteria

HQ v1 is complete when all are true:

- `docs/WARASHIBE_HQ.md` exists with initial strategy.
- HQ Python contract exists and passes.
- append-only strategy repository exists.
- `warashibe_strategy_decisions` exists with RLS and closed-by-default permissions.
- initial strategic decision is recorded.
- HQ skill exists and skills index references it.
- exact-SHA CI is successful.
- same SHA is live on Render.
- runtime status records `deployment_consistent=true`.
- Library handoff records the HQ architecture and operating rule.

## 16. Out of scope for HQ v1

- autonomous real-world commerce
- automatic Human Gate approval
- changing secrets/auth configuration
- multi-agent voting systems
- strategy scoring models
- automatic strategy rewriting from every experiment
- replacing existing Product Gap or Research Lab components
