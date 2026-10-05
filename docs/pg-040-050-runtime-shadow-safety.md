# PG-040–050 Runtime / Shadow / Safety

This milestone extends PG-037–039 without granting commerce authority.

| PG | Contract | Completion meaning |
|---|---|---|
| 040 | PR Review & Integration Gate | exact head, code match, review, CI evidence can be evaluated; merge/deploy remain false |
| 041 | Runtime Status Integration | maturity, CI, Render/Supabase, Shadow/Promotion/Evidence states are surfaced without inference |
| 042 | Evidence Integrity Gate v2 | canonical page identity and independent sold-source domains are checked |
| 043 | Shadow Scheduler | a later read-only observation can be scheduled with attempt limits |
| 044 | Real-Market Shadow Connector | untrusted read-only adapter payload is normalized; no network/write action lives in the contract |
| 045 | Shadow Outcome Engine | hypothetical profit/variance is computed from persisted observations |
| 046 | Promotion Evidence Pack | CEO review packet combines economics, promotion and integrity evidence |
| 047 | Live Readiness Gate | exact preconditions are checked; explicit human go is still required |
| 048 | Recovery Controller | safe reads can retry; commerce writes fail closed |
| 049 | Duplicate / Idempotency Guard | duplicate or conflicting operation keys are blocked |
| 050 | Burn-in Framework | observed outcomes are measured; passing does not enable automation |

## Safety invariants

Every new contract returns `external_execution_authorized=false` and
`purchase_authorized=false`. PG-047 may say live-readiness is satisfied, and
PG-050 may say burn-in metrics passed, but neither grants permission to purchase,
pay, list, sell, move money, change secrets, migrate production data, or deploy.

PG-044 deliberately contains no marketplace HTTP client. A separately reviewed
read-only adapter may supply market observations; its output is still validated as
untrusted input.

## Next endpoint

PG-051 should add walk-forward strategy validation using historical/Shadow evidence
without contaminating prospective evidence or changing the active strategy
automatically.
