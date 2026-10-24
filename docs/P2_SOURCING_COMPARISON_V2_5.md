# P2 Candidate Search v2.5 — Sourcing Channel Comparison

## Development endpoint

v2.5 is complete when the research branch can compare multiple sourcing channels for one exact product using fully-loaded acquisition cost, reject incomplete/unsafe source evidence, rank eligible sources deterministically, and preserve the Human Gate.

This milestone does not require Amazon/Keepa live access and does not authorize any purchase.

## Why v2.5 exists

The previous P2 search accumulated many market-evidence records but produced no selection record. A recurring failure mode was comparing nominal item price while inbound shipping, source handling fees, stock freshness, condition, or exact identity remained uncertain.

v2.5 makes the source-side question explicit:

> For this exact item, which currently available source has the lowest *verified total acquisition cost* that still fits the capital and margin ceiling?

## Initial supported source channels

- Surugaya
- NETOFF
- BOOKOFF
- GEO
- HardOff
- Lashinbang
- Mercari Shops
- Yahoo source listings
- Specialty shops
- Manufacturer shops
- Amazon.co.jp / Keepa adapter (implemented but may remain operationally deferred)

This list is a normalization contract, not a guarantee that every source has a dedicated live API adapter.

## Fully-loaded acquisition

Each source offer carries:

- item price
- inbound shipping
- source handling/marketplace fee
- other acquisition cost
- resulting total acquisition cost
- stock status
- exact identity verification
- condition/completeness match
- source confidence
- observation timestamp/source URL when available

Unknown inbound shipping is **not** interpreted as zero.

The comparison order is:

1. exact identity / condition integrity
2. current availability
3. source-confidence threshold
4. capital limit
5. max-total-acquisition ceiling derived from conservative resale economics
6. lowest total acquisition cost
7. higher source confidence as tie-breaker

This prevents a cheap sticker price with high shipping from outranking a more expensive listing with free shipping.

## Amazon status

The v2.4 Amazon/Keepa observer remains available as a pluggable source adapter, but live Keepa access is deferred until the user decides the external paid API is worth enabling.

v2.5 therefore works with current domestic channels first and can accept Amazon observations later without changing the comparison engine.

## Safety / Human Gate

Every source assessment and final comparison preserves:

- `human_gate_required=true`
- `external_execution_authorized=false`
- `purchase_authorized=false`

No cart operation, checkout, payment, order, listing, or account mutation is performed.

## Selection relationship

A v2.5 source winner is **not automatically a P2 Selection**.

The intended pipeline is:

Sold Evidence Seed
→ Conservative Sale Price
→ Maximum Total Acquisition Budget
→ Source observations
→ **v2.5 fully-loaded source comparison**
→ Evidence Integrity
→ P2 Selection eligibility
→ Shadow
→ Promotion Gate
→ Human Review Packet
→ Human Gate

## Validation

`research_lab.test_sourcing_channel_comparison` verifies:

- sticker-price winner can lose to lower landed cost
- shipping/handling are included
- unknown shipping fails closed
- condition mismatch fails closed
- cross-product comparison is rejected
- Amazon v2.4 observations can plug into v2.5
- no comparison result grants purchase authority

The test is included in the normal Research Lab build profile.
