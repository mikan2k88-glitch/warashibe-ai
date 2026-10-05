# PG-037–039: Maturity, Shadow and Promotion

The implementation is based on `research-lab` at
`9643d34cfbc9c07e2f074a121ff678a5b845c41d`. Main/production, secrets,
authentication and database schema are unchanged. No deployment or commerce
execution is part of this milestone.

## Execution boundary

`maturity_stage.stage_contract` defines operations, prohibited operations and
adjacent stages. Unknown stages/operations and skipped transitions are rejected.
All ten stages retain `external_execution_authorized=false`,
`purchase_authorized=false` and `human_gate_required=true` in this milestone.
Live stage names reserve future interfaces; they do not implement live execution.
Advancement from Human Gate and later requires the existing explicit, unexpired
Human Go/No-Go record matched to its readiness audit. The caller must retrieve
that record through the existing authenticated human workflow: a dictionary
alone is not proof of a person's identity. This contract adds no approval API.

## Shadow storage and loop

Shadow records preserve the existing Candidate name, source, purchase price,
sale price and evaluation fields. An explicit assessment supplies product ID,
edition/condition/model/JAN/accessories, costs, evidence and risk decisions.
Missing evidence may be saved for research but cannot produce promotion.
The acquisition snapshot is copied and remains immutable. Later observations
and the terminal hypothetical outcome are separate records. Finished candidates
cannot be observed or completed again.

`ShadowRepository` has in-memory and atomic local JSON implementations. JSON is
single-process storage, not a concurrent production database. Malformed storage
raises an error rather than displaying fabricated zero counts. Shadow outcomes
are intentionally separate from `OutcomeRepository` and its real-sale learning
data. No Supabase migration or write is performed; a future adapter must provide
RLS, transactions and the same safety contract.

The optional P2 arguments `shadow_repository`, `shadow_assessment`, `as_of`
route only the existing selected candidate to Shadow. Calls without those
arguments retain the previous result. Routing does not bypass the existing
Danger/Capital/Ranking pipeline and does not advance to P3 automatically.

Alternatively use the explicit local CLI:

```sh
python -m research_lab.shadow_cli candidate --store research_output/shadow.json --as-of 2026-10-05T00:00:00Z --input candidate-packet.json
python -m research_lab.shadow_cli observe --store research_output/shadow.json --as-of 2026-10-06T00:00:00Z --id SHADOW_ID --input observation.json
python -m research_lab.shadow_cli outcome --store research_output/shadow.json --as-of 2026-10-06T00:00:00Z --id SHADOW_ID
python -m research_lab.shadow_cli snapshot --store research_output/shadow.json --as-of 2026-10-06T00:00:00Z
```

Candidate input is `{"candidate": <existing Candidate>, "assessment": <assessment>}`.
The offline fixtures in `test_shadow_promotion.fixture` and
`observation_fixture` document the packet fields. These are synthetic examples,
not market observations. The CLI does not fetch markets or execute commerce.

Configure the runner and Dashboard with `WARASHIBE_SHADOW_STORE` pointing to
the same JSON file and `WARASHIBE_MATURITY_STAGE=shadow`. Without configuration,
the declared system stage is research, counts are zero and integrity is
`not_evaluated`. Recording a candidate does not automatically advance the system
stage. `/hq/api`, HQ program and the rendered Dashboard derive their counts
from the same backend snapshot, recalculating freshness at read time.

## Promotion gate

Minimum evidence checks cover HTTPS source URLs, timezone-aware observation
time, future/stale dates, unique evidence IDs and source URLs per evidence kind,
product identity (including edition, condition, accessories, model/JAN), cost
amounts and sold-price evidence. Listing prices cannot substitute for two
independent sold references. Estimated sale price cannot exceed their median.
Zero fees/shipping still require an explicit evidence record. Every evidence
record must pass; invalid additional evidence also closes the gate.

Promotion additionally requires low condition/authenticity risk, verified
return conditions, supported sellability, a stop-loss price and bounded holding
period, evidence for those assessments, sufficient liquidity and net profit,
and a successful completed hypothetical Shadow outcome. Current observation
identity, freshness, liquidity, costs, availability and source price are checked
again; an attractive acquisition snapshot cannot hide deteriorated observations.
Default thresholds are 7 days, liquidity 0.5 and net profit JPY 300.

Results distinguish `research_usable_not_promotion_ready` from `promotion_ready`.
Promotion can prepare Human Review, but `live_ready` remains false: this module
never records a human approval, imports commerce adapters or authorizes purchase.
Declared metadata and URLs are checked locally; remote source existence,
authenticity and actual ability to sell are not proven by these checks.

## Verification

Run the three new module-style tests and the existing build/core profiles.
The branch/PR workflow checks the exact head SHA and preserves existing Commerce,
HQ, Human Review, P2 and Strategy Learning regressions. Broader local discovery
found eight pre-existing failing modules at the base SHA; those are documented
separately in the delivery report rather than changing unrelated contracts.
