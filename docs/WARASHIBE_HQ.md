# Warashibe Headquarters

Last updated: 2026-10-06
Status: PG-060 integrated; operations/evidence collection mode

## Governance

- Human CEO owns the North Star, constraints, major strategic changes, and Human Gate approvals.
- GPT Headquarters acts as the COO layer: it interprets CEO direction, selects the current bottleneck, ranks work, routes execution, and reviews evidence.
- Research / Development / Operator layers execute only within their existing permissions.
- Auditor evidence returns to HQ before strategy is changed.

HQ never self-authorizes a Human Gate action.

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
- Capital Velocity base implementation: complete.
- Learning Loop entry: complete.
- HQ v1 strategy memory: complete.
- HQ v1.1 CEO Directive / Priority Queue / Escalation / Strategy Review: complete.
- P1 HQ Runner Integration development: complete.
- P2 Real Pilot Decision Packet development: complete.
- P3 CEO Approval Gate development: complete.
- P4 bounded one-item live-pilot control development: complete.
- P5 Learning Feedback adapter development: complete.
- P6 Capital Velocity ranking development: complete.
- P7 Controlled Automation Scope evaluator development: complete.
- Real external buy/sell cycle operational proof: not yet verified.
- Controlled automation operational authorization: not granted.

## Development capability vs operational evidence

The P1-P7 software/control path is implemented through the development endpoint.

Operational progress remains evidence-driven:

- P1: operationally complete — scheduled development can be routed through HQ.
- P2: current operational priority — prepare a real-pilot decision packet from current evidence.
- P3: available once one P2 packet is ready.
- P4: requires explicit Human Gate approval before any real purchase/payment/listing/sale.
- P5: requires a completed pilot review.
- P6: available for candidate ranking and improves when live feedback exists.
- P7: evaluator is implemented, but safe-scope expansion requires repeated verified live cycles and never authorizes Human Gate actions.

Therefore "development endpoint P7 reached" does not mean "live commerce completed" or "controlled automation authorized."

## Current bottleneck

`real_market_shadow_evidence_not_yet_promoted`

## Active strategy

`candidate_discovery -> evidence_integrity -> shadow_observation -> shadow_outcome -> promotion_gate -> human_review_packet -> human_gate`

PG-060 is the feature-development endpoint for the current architecture. The default posture is operations/evidence collection, monitoring, and targeted repair rather than continuing to add PG numbers.

## First Formal Priority Queue

### P1 — HQ Runner Integration
Connect scheduled development to HQ so each cycle runs:

`HQ load -> verified state -> bottleneck -> Priority Queue -> select one objective -> execute -> evidence -> Strategy Review`

Development endpoint: complete.

### P2 — Real Pilot Readiness
Produce one decision packet for a real external item containing:
- acquisition price;
- expected sale price;
- fees;
- liquidity / expected sell-through time;
- condition / authenticity risk;
- maximum acceptable loss;
- exit / stop-loss condition.

Development endpoint: complete.
Operational endpoint: one current candidate ready for CEO review without executing a purchase.

### P3 — CEO Approval Gate
Present one-item pilot evidence to the CEO with:
- why this item;
- expected profit;
- maximum loss;
- expected capital lock time;
- invalidation / abort conditions.

Development endpoint: complete.
Operational endpoint: execution stops at Human Gate pending explicit CEO approval.

### P4 — One Item Live Proof
After explicit Human Gate approval only, verify one real external cycle:
`purchase -> receive/inspect -> sale/listing -> settlement`.

Development endpoint: bounded execution-chain preparation complete.
Operational endpoint: one complete real-world proof with auditable evidence.

### P5 — Learning Feedback
Feed realized spread, fees, sell-through time, failure causes, and settlement evidence back into candidate evaluation.

Development endpoint: feedback adapter complete.
Operational endpoint: next candidate ranking uses realized live evidence.

### P6 — Capital Velocity Improvement
Optimize for capital turnover, not gross margin alone.

Development endpoint: confidence-weighted capital-velocity ranking complete.
Operational endpoint: compare expected return together with expected time-to-next-capital using live feedback.

### P7 — Controlled Automation Expansion
Expand automation only across repeatedly verified safe steps while preserving Human Gate boundaries.

Development endpoint: safe-scope evaluator complete.
Operational endpoint: safe automation scope may expand only after sufficient verified live cycles; real purchase/payment/listing/sale remain Human Gate actions.


## PG-060 operational posture

Verified integration state:

- research-lab HEAD: `7ef2374a7fdf25bd14b4580b65c4ae65e45af1ae`
- exact-SHA Research Lab CI: success
- Render research service: same SHA live
- Supabase runtime status: same SHA, deployment_consistent=true

Operational rules after PG-060:

1. Candidate discovery remains active.
2. A candidate does not move directly to CEO/P3; it must pass Evidence Integrity and Shadow observation/outcome first.
3. Promotion Gate may prepare Human Review, but never grants purchase authority.
4. Scheduled work should collect evidence, monitor runtime, and repair verified defects; it should not create feature churn.
5. Controlled automation remains limited to proven safe read/research/shadow scopes. Real commerce remains behind Human Gate.

## CEO Directive contract

CEO input may be converted into a durable directive only when it changes or constrains strategy.

Each material directive should contain:

- directive key
- instruction
- objective
- constraints
- issued time

Ordinary conversation is not automatically treated as a durable strategy change.

## Priority Queue contract

HQ ranks work by:

- North Star impact
- bottleneck relief
- evidence strength
- readiness
- cost

Any candidate that crosses the Human Gate is removed from normal execution ordering and escalated to the CEO.

## Escalation contract

The following always require CEO / Human Gate approval before execution:

- real purchase
- real payment
- real listing or sale
- real-money movement
- secrets/auth changes
- destructive database changes
- risky production changes
- North Star changes
- Human Gate changes

HQ may research, prepare, compare, simulate, and recommend these actions, but cannot execute them by itself.

## Strategy Review Loop

At a development endpoint or material evidence checkpoint:

1. Compare current evidence with the active bottleneck.
2. If the bottleneck remains, maintain strategy.
3. If the bottleneck is verified as resolved, advance to the next bottleneck.
4. If a material CEO Directive changes the objective or constraints, replan.
5. Record a material strategy decision in Supabase.
6. Update this document only when the current strategy changes.

## Operating rule

At the start of a Warashibe development session or scheduled development cycle:

1. Read this HQ source.
2. Check verified current project/runtime state.
3. Read recent strategy decisions only when needed.
4. Apply any material CEO Directive.
5. Identify one current bottleneck.
6. Rank candidate work in the Priority Queue.
7. Select one strategic objective that does not cross the Human Gate.
8. Route execution to the appropriate worker/tool.
9. Collect exact evidence.
10. Run Strategy Review.
11. Record a material strategy decision when strategy actually changes.

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
