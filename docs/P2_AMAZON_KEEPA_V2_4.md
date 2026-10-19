# P2 Candidate Search v2.4 — Amazon / Keepa sourcing channel

## Development endpoint

v2.4 is complete when the research branch can observe Amazon.co.jp offers through a read-only Keepa boundary, normalize Prime/non-Prime acquisition economics, reject stale/unknown-cost evidence, and feed a deterministic P2 source gate without granting commerce authority.

This milestone does **not** authorize a real purchase and does not require a Keepa subscription to pass CI.

## Role in the Warashibe flow

Sold Evidence Seed
→ Conservative Sale Price
→ Max Total Acquisition Budget
→ **Amazon/Keepa Source Observation**
→ Source Confidence / Fully-loaded Acquisition
→ P2 Selection eligibility
→ Shadow
→ Promotion Gate
→ Human Review Packet
→ Human Gate

Amazon is a sourcing channel. Sold/completed evidence remains independently sourced and must not be inferred from an Amazon active listing.

## Amazon source model

Each offer is evaluated separately. "Amazon price" is not one scalar.

Tracked fields include:

- ASIN and title
- condition
- seller ID
- Amazon seller flag
- FBA flag
- Warehouse Deal flag
- Prime eligibility
- Prime-exclusive price when present
- item price
- explicit shipping cost
- non-Prime acquisition total
- Prime acquisition total
- offer freshness
- 30-day and 90-day offer-total medians
- live/in-stock status
- source confidence

Prime is treated as a scenario, not an assumption. A Prime flag never silently converts unknown shipping into zero.

## Keepa integrity rules

Keepa may retain historical offers. The observer therefore evaluates offer freshness and, when supplied, `liveOffersOrder`. Stale or non-live offers cannot pass the source gate merely because their historical price is attractive.

Raw Keepa offer history is normalized from `offerCSV`. The latest price and shipping are kept separate, and recent medians use price + shipping so source economics are not distorted by nominal item price alone.

## Source confidence

The initial confidence score is 0–100:

- product identity verified: 20
- freshness: 15
- shipping explicitly known: 15
- live/in-stock evidence: 15
- seller + fulfillment evidence: 10
- condition known: 10
- 30/90-day price history: 15

Default P2 source threshold: **70**.

A score below the threshold is evidence, not a selection candidate.

## P2 source gate

Default constraints:

- capital: caller supplied (initial live pilot target about JPY 3,000)
- minimum expected net profit: JPY 300
- source confidence: at least 70
- source currently available
- selected Prime/non-Prime total acquisition known
- total acquisition within capital
- conservative sale price minus selling fee, outbound shipping, packing, and acquisition cost must satisfy minimum profit

A pass returns `selection_eligible` only. It always returns:

- `human_gate_required=true`
- `external_execution_authorized=false`
- `purchase_authorized=false`

## Secrets and cost boundary

`KEEPA_API_KEY` is optional and is read only when the live observer is explicitly invoked. It is not required for deterministic CI and must not be committed.

Subscribing to a paid Keepa API plan is outside this milestone and requires a Human Gate because it creates an external paid-service commitment.

## Validation

`research_lab.test_amazon_keepa_observer` validates:

- raw Keepa offer normalization
- amazon.co.jp domain ID
- freshness/live offer handling
- Prime-exclusive and non-Prime economics
- shipping inclusion
- 30/90-day history
- source confidence
- eligible/rejected P2 decisions
- preservation of Human Gate and zero commerce authorization

The test is included in the normal Research Lab build profile.
