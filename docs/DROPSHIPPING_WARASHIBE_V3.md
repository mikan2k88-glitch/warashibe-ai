# Dropshipping Warashibe v3.0

## Endpoint

v3.0 completes the **real-read / shadow / promotion-review** research foundation.

It does not enable live commerce.

## Research path

Supplier Provider (READ)
→ normalize / map / dedupe
→ data quality
→ supplier evidence
→ comparable market price (READ)
→ currency guard
→ opportunity economics
→ policy
→ opportunity ranking
→ shadow observations
→ shadow metrics
→ shadow gate
→ promotion review package
→ human gate

## Read-only providers

Implemented adapters/contracts include:

- CJdropshipping Product List V2
- Printful catalog discovery
- eBay Browse comparable-price search
- generic paged JSON GET provider
- generic CSV feed GET provider

Credentials are injected through environment variables. Secret values are never returned
through status endpoints.

## Source budget

Research reads are bounded by explicit maximums:

- supplier items
- market queries
- comparable quotes per query

This prevents uncontrolled external API use.

## Evidence

Research evidence is append-only by design:

- dropship_observations
- dropship_audit_log
- dropship_research_snapshots
- dropship_research_runs

Research database writes are allowlisted separately from commerce writes.

## Shadow gate

Default evidence thresholds:

- minimum 20 observations
- minimum 7 distinct observation days
- inventory confirmation rate >= 0.8
- stable observed price series

Passing the Shadow Gate creates a **Promotion Review Package** only.

It does not create a listing or supplier order.

## Safety boundary

Blocked automatic actions:

- live listing creation
- supplier order submission
- payment capture
- supplier-order cancellation
- refund
- automatic promotion to live
- automatic material strategy change

Approval code verification is a Human Gate input only. It does not independently enable
live execution.

## Resilience

- read-only provider failover
- read-only circuit breaker
- bounded transient retries
- DLL Concierge degraded/cache mode
- stale-evidence filtering

Write operations are never automatically retried.

## Scheduled research

GitHub Actions workflows exist for:

- deterministic proof
- shadow collection
- bounded real-read research
- evidence artifact upload

Scheduled workflows become operational from the default branch after the workflow is merged.

## External-read prerequisites

Actual external reads require runtime credentials/configuration such as:

- CJ_ACCESS_TOKEN
- EBAY_ACCESS_TOKEN

Without these tokens, the same research path can be exercised with deterministic fixture
providers for CI/proof.

## v3.0 completion criteria

- v3 deterministic proof passes
- v3 acceptance passes
- exact branch HEAD CI succeeds
- Promotion Review can be reached from sufficient Shadow evidence
- real commerce writes remain disabled
