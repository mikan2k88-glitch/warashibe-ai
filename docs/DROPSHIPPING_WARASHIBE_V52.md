# Dropshipping Warashibe v5.2

## Endpoint

v5.2 completes the research-side path from provider diagnostics through long Shadow
evidence to a Promotion Review package for Human Gate review.

It still does not enable live commerce.

## Milestones

### v4.2 Provider Diagnostics

Classifies provider failures into:

- authentication / expired token
- rate limit / quota
- transient connectivity
- unknown/manual review

Only safe READ retries remain eligible.

### v4.3 Real Shadow Collection

Uses the existing persistent Shadow operations layer:

- restore historical observations from Supabase
- perform bounded provider/market READ
- append new observations
- append run ledger evidence
- recompute Shadow progress

### v4.4 Discovery

Creates bounded search plans from:

- product title
- category
- supplier metadata
- SKU/brand metadata

Duplicate discovery queries are removed.

### v4.5 Market Confidence

Comparable-price evidence now includes:

- extreme price outlier removal
- median-centered bounds
- quote-depth score
- price-variation score
- seller/quote liquidity proxy
- market confidence score

### v5.0 Real Product Ranking

Real-product scoring combines:

- opportunity economics
- market confidence
- market liquidity
- supplier reliability
- working-capital allowance

The one-item-only Warashibe rule remains enforced.

### v5.1 Long Shadow Evidence

Default maturity requirements include:

- at least 20 observations
- at least 7 observation days
- inventory confirmation rate >= 0.80
- stable price history
- market confidence >= 0.45
- opportunity score >= 0.35
- positive expected-profit observations >= 70%
- supplier-cost drift <= 20%

These thresholds are research gates, not commerce authorization.

### v5.2 Promotion Review

A Promotion Review package contains:

- product identity and supplier evidence
- expected net profit / margin
- required working capital
- real-product score
- opportunity score
- market confidence / liquidity
- Shadow observation count and days
- supplier-cost drift
- policy checks
- evidence-maturity result
- stop conditions
- Human Gate decision options

Allowed decisions:

- approve for future limited-live preparation
- continue Shadow
- reject candidate

Even the approval option only advances preparation. It does not execute a listing,
supplier order, payment, cancellation, or refund.

## Promotion Queue

Only evidence-mature candidates enter the ready queue.
The queue sorts by real-product score and expected profit.

Automatic promotion remains disabled.

## Stop Conditions

Promotion Review carries explicit pause/stop conditions for:

- non-positive expected profit
- supplier-cost increase
- market-price decline
- inventory loss
- delivery deterioration
- supplier-reliability deterioration

## v5.2 proof

The deterministic proof verifies:

- one real-product candidate is ranked
- one-item-only is preserved
- 21 observations across 7 days satisfy the evidence gate
- market confidence is sufficient
- supplier-cost drift remains bounded
- Promotion Review is ready
- Promotion Queue contains one review
- Human Gate is required
- automatic promotion is disabled
- commerce writes are not performed
- live execution remains disabled

## Current maturity ceiling

**Promotion Review / Human Gate**

The next operational phase is to configure real provider credentials, accumulate real
Shadow evidence, and allow real candidates—not fixture candidates—to enter the review queue.
