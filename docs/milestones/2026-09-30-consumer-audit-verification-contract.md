# 2026-09-30 — Consumer-facing audit verification contract

## Milestone

Expose a small, machine-readable verification result for a received public audit distribution bundle.

## Contract

The consumer adapter returns a fixed schema version `1.0` with exactly these fields:

- `consumer_schema_version`
- `status`
- `decision`
- `integrity_verified`
- `target_sha`
- `bundle_digest`
- `reason_codes`
- `read_only`
- `external_runtime_action_authorized`
- `auto_retry_authorized`
- `auto_rollback_authorized`
- `contains_secrets`
- `contains_internal_execution_details`

`decision` is one of `accept`, `reject`, or `hold`.

## Decision semantics

- `accept`: the canonical audit distribution bundle passes the existing bundle verifier.
- `reject`: a supplied bundle is structurally present but fails an integrity, schema, cross-reference, or tamper check.
- `hold`: the consumer does not have a usable bundle object to verify yet; it must not infer validity.

## Safety boundary

The consumer contract is read-only. It exposes no internal payloads or execution details and never authorizes external runtime actions, automatic retries, or automatic rollback.

## Verification

Commit `9e514bc689d6fa95efe576bd15e3ef423cf21402` triggered Research Lab CI #993. All existing research-lab tests and the new consumer verification regression passed; the complete workflow finished with `success`.

The next milestone can build on this stable decision contract without changing the underlying audit evidence or digest chain.
