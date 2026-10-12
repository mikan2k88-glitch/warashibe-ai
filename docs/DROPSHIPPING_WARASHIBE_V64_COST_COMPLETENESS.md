# Dropshipping Warashibe v6.4 — Cost Completeness / Terms Evidence

## Goal

Prevent incomplete real-world cost data from being interpreted as zero cost and promoted toward the Human Gate.

## Cost Completeness Gate

Required evidence:

- supplier cost
- supplier shipping
- platform fee rate
- payment fee rate
- expected return cost
- refund reserve

A numeric value alone is not enough when the provider explicitly marks the evidence as unknown. This is especially important for CJ Product List V2, where supplier shipping is not provided by the current product-list read.

Explicit zero is allowed only when its evidence status is known/confirmed.

## Terms Evidence Gate

Required evidence:

- supplier dropshipping permission
- marketplace/platform terms
- return terms
- cancellation terms

Unknown terms block v6.4 Human Gate eligibility.

## CJ semantics

CJ Product List V2 continues to expose the current normalized numeric placeholder for compatibility, but v6.4 adds explicit evidence metadata:

- supplier_cost: known when a positive CJ cost was returned
- supplier_shipping: unknown
- marketplace fees: unknown
- payment fees: unknown
- return cost/reserve: unknown
- supplier/platform/return/cancellation terms: unknown until separately evidenced

Therefore a CJ-only product cannot be promoted merely because a placeholder shipping value is 0.

## Compatibility

v6.2 remains intact. v6.4 wraps the v6.2 Actual Evidence Controller and applies an additional cost-and-terms gate before reporting a Human Gate candidate.

The real Actual Evidence script now uses the v6.4 controller.

## Supabase duplicate fix

During real CJ verification, a same-hour rerun returned PostgREST uniqueness conflicts. The REST client previously reduced the error to a generic HTTP exception, so `23505` could not be recognized as a duplicate.

v6.4 now safely reads the PostgREST error code only and classifies `23505` as an expected duplicate. Error bodies and secrets are not emitted.

Verified same-hour rerun:

- fetched: 5
- inserted: 0
- duplicates: 5
- errors: 0

## Safety

- automatic promotion: disabled
- commerce external writes: disabled
- live execution: disabled
- Human Gate still required
