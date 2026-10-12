# Dropshipping Warashibe v2.0

## Purpose

Warashibe AI の Candidate / Strategy / Policy / Evidence / Human Gate / Runtime の思想を再利用し、
在庫を持たないドロップシッピング研究を安全に反復する。

North Star:

- small capital
- one item only
- minimize failure cost before maximizing profit
- accumulate evidence through many low-cost experiments
- human approval remains mandatory before any future live commerce

## Architecture

### Common Warashibe Core

- Candidate evaluation
- Strategy selection
- Policy gating
- Evidence / Audit
- Human Gate
- Runtime / Recovery
- Learning

### Dropshipping Domain

- supplier evidence normalization
- supplier reliability scoring
- economics and working-capital calculation
- source freshness
- policy profile
- one-item selection
- shadow observation
- promotion gate
- listing preview
- sandbox order lifecycle
- fulfillment / settlement
- stop-loss
- outcome learning

### Integration

- DLL Concierge v5.3 registry client
- DLL degraded/cache mode
- read-only supplier provider contract
- read-only platform adapter contract
- Supabase append-only repository contract
- GitHub Actions proof / CI

## Maturity ladder

1. Research
2. Shadow
3. Sandbox
4. Live Readiness
5. Human Gate
6. Limited Live
7. Burn-in
8. Controlled Automation

v2.0 intentionally stops at **Human Gate readiness**.

## Live safety boundary

The following automatic actions are blocked:

- create live listing
- submit supplier order
- capture payment
- cancel supplier order
- issue refund
- connect live commerce account

Automatic retry is limited to transient read operations such as supplier inventory,
tracking, Registry, and supplier offer retrieval.

## Working capital

Inventoryless commerce is not capital-free. The economics engine explicitly calculates:

- supplier cost
- supplier shipping
- platform fee
- payment fee
- advertising cost
- expected return cost
- refund reserve
- other costs
- expected net profit
- margin
- required working capital

The selector enforces one-item-only and rejects candidates outside available working capital.

## Validation

Research validation includes:

- Evidence Integrity
- Freshness Gate
- Supplier ranking
- Strategy experiment
- Walk-forward validation
- Champion / Challenger promotion proposal
- Shadow Mode
- Promotion Gate
- Sandbox Campaign
- Burn-in assessment
- v2.0 deterministic proof
- v2.0 acceptance

Strategy promotion is never applied automatically.

## Persistence

Schema draft:

- dropship_observations
- dropship_audit_log
- dropship_research_snapshots

All are designed as append-only research evidence stores.

## DLL Concierge

Primary read endpoint:

`/factory/v5.3/registry`

Warashibe uses DLL Concierge as a component factory/search service.
If DLL Concierge is sleeping or temporarily unavailable, Warashibe enters degraded mode
and continues research from registered supplier providers and cached Registry data.

## Current endpoint

Research v2.0 is considered reached when:

- v2 proof passes
- v2 acceptance passes
- CI passes on the exact branch HEAD
- live commerce remains disabled

The next major phase is real read-only supplier/platform evidence acquisition.
