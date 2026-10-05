# Evidence-driven learning and Dashboard

## Learning input gate

Learning findings require HTTPS sources and parseable observation times. Day-only
legacy times explicitly mean UTC midnight; datetimes require a timezone. Findings
must be no more than seven days old and cannot be from the future. `as_of` can be
passed for reproducible offline replay; otherwise evaluation uses the current UTC
clock. NaN, infinity, booleans and out-of-range thresholds are rejected. The same
page with query/tracking/fragment changes counts once, using PG-039's shared URL
identity. Different paths are distinct pages, not proof of independent publishers.

Decision preparation revalidates the exact proposal that was evaluated. None of
these checks authenticates a remote source or permits production rule changes.

## Dashboard sources

The Dashboard reads the configured `WARASHIBE_SHADOW_STORE`, showing the most
recent saved candidate, its observation time, evidence references and promotion
reasons. No saved candidate means `not_observed`; no historic example is shown as
current evidence. Candidate evaluation is hypothetical. HTML escapes saved text;
source links require HTTPS without embedded credentials.

P1 execution can be displayed as `observed_success` by configuring
`WARASHIBE_RUNNER_SNAPSHOT` to a local runner `latest.json` and
`WARASHIBE_EXPECTED_HEAD_SHA` to the deployed/tested commit. The reader requires a
successful build, non-empty successful checks, matching SHA, retained Human Gate
and a timestamp within 24 hours. Missing, stale, future, malformed or mismatched
records display `not_verified`. This is local observed execution evidence, not a
signed attestation or a live service heartbeat. A runner result does not establish
P2–P7 completion or an active learning service. Other operational states stay
unverified until corresponding execution evidence is connected. No settings are
automatically changed by this implementation.

## Persistent replay

Run `python -m research_lab.test_shadow_integration` for five independent replays
of one synthetic product identity: success, loss, unsold, invalidated and
insufficient evidence. Each replay reloads JSON storage between stages and checks
that Dashboard and Promotion Gate reference the same candidate ID. Only success
can prepare human review; all five retain `purchase_authorized=false`.
`research_output/shadow_replay.json` records the traces and is included in CI
artifacts. This proves the software path with fixtures, not actual market profit.

## Further engineering work

- JSON remains single-process research storage. Multi-worker deployment needs a
  transaction-based repository with uniqueness and concurrency controls.
- Existing ranking uses gross expected value; a fee/return/holding-aware policy
  should be introduced and compared in Shadow before changing default rankings.
- The eight known baseline failures and the large research module set remain
  separate cleanup work; this change strengthens the critical integration path.
- Real market observation and operational learning evidence are not yet connected.
  Human Gate, authentication, secrets, commerce and deployment are unchanged.
