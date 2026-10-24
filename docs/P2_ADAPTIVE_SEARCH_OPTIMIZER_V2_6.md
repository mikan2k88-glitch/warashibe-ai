# P2 Candidate Search v2.6 — Adaptive Search Optimizer

## Development endpoint

v2.6 is complete when the research branch can:

1. rank candidate investigations by capital velocity and evidence quality,
2. use recent rejection reasons to alter the next search strategy,
3. adapt category allocation without collapsing into one category,
4. preserve all formal evidence, Shadow, Promotion and Human Gates,
5. remain deterministic and testable without live commerce or paid APIs.

This is a search-allocation optimizer, not a purchase algorithm.

## Optimization objective

Primary objective:

```
expected_net_profit_jpy
× sale_probability
÷ expected_hold_days
```

This gives an expected capital-velocity signal in JPY/day.

The final search priority also considers:

- evidence confidence
- source quality
- cost certainty
- acquisition headroom below the maximum allowable acquisition cost
- sold-comp depth
- source diversity

Initial weighting:

- capital velocity: 35%
- evidence confidence: 20%
- source quality: 15%
- cost certainty: 10%
- acquisition headroom: 10%
- sold depth: 5%
- source diversity: 5%

These weights are research defaults. They do not change production policy by themselves.

## Fail-closed research penalties

Candidates receive search-priority penalties when:

- sold comps < 2
- source count < 2
- total acquisition exceeds the calculated acquisition ceiling
- cost certainty < 60

These penalties only reduce investigation priority. Formal P2 selection gates remain separate and stricter.

## Adaptive rejection learning

Recent rejection reasons change the next-run search allocation:

- `sold_evidence_insufficient`
  → spend more search budget on Sold Evidence before source search
- `insufficient_margin` / `over_capital`
  → shift toward lower acquisition cost or higher conservative resale bands
- `shipping_loss`
  → prioritize known/free inbound shipping and small/light products
- `low_liquidity`
  → demand stronger recent sold frequency
- `edition_mismatch` / `condition_mismatch`
  → move exact identity and condition checks earlier
- `stale_evidence` / `source_unavailable`
  → prioritize fresh live-stock sources
- `unstable_price`
  → prefer lower price dispersion
- `authenticity_risk`
  → deprioritize authenticity-sensitive categories

Unknown rejection classes fail closed instead of silently changing strategy.

## Category allocation

Recent category results can provide:

- searched
- seed_pass
- selection_eligible
- near_p3_shadow

The optimizer applies smoothed effectiveness weighting so categories with little history do not disappear. It preserves exploration and prevents one category from intentionally consuming more than roughly 70% of the allocation.

The aim is not equal category coverage. The aim is to allocate more effort where evidence quality and Selection probability are improving while preserving discovery diversity.

## Relationship to v2.5

The intended flow is now:

Sold Evidence Seed
→ Conservative Sale Price
→ Max Total Acquisition Budget
→ v2.5 Multi-source Fully-loaded Comparison
→ **v2.6 Search Priority Optimizer**
→ Evidence Integrity
→ P2 Selection
→ Shadow
→ Shadow Outcome
→ Promotion Gate
→ Human Review Packet
→ Human Gate

v2.6 decides which candidates deserve scarce investigation time first. It does not override v2.5 landed-cost results or any later gate.

## Why no machine learning yet

There are not enough real Selection/Shadow/live outcome samples to justify ML or reinforcement learning. A transparent rule-based optimizer is preferred until enough outcome data exists to estimate whether learned weights generalize.

A later optimizer may learn weights from:

- actual sale price vs prediction
- actual days-to-sale vs prediction
- actual source cost vs estimate
- actual fee/shipping variance
- Selection → Shadow → Promotion conversion rate
- realized capital velocity

Any learned model must first run in Shadow and must not self-authorize commerce.

## Safety

Every optimizer result preserves:

- `human_gate_required=true`
- `external_execution_authorized=false`
- `purchase_authorized=false`
- `production_rule_changed=false`

Strategy adaptations require Shadow validation before any policy promotion.

## Validation

`research_lab.test_candidate_search_optimizer` verifies:

- a faster-turning candidate outranks a slower candidate despite lower nominal profit
- immature/high-uncertainty candidates receive bounded penalties
- rejection history changes next-run search actions
- category weights remain normalized and diversified
- unknown failure classes fail closed
- no result grants commerce authority

The test is included in the normal Research Lab build profile.
