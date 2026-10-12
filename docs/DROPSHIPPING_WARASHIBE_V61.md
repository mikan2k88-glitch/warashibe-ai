# Dropshipping Warashibe v6.1

## Purpose

v6.1 prevents deterministic fixtures from qualifying a product for the final Human Gate.

## Qualification requirements

A candidate must have:

- Promotion Review readiness
- non-fixture supplier evidence
- real-read opportunity observations
- at least one real_read run
- persistent Shadow history enabled
- successful CJ/eBay provider handshake
- no fixture markers in supplier/source/mode/provider evidence

## Fixture policy

Fixtures remain valid for:

- CI
- deterministic proof
- architecture testing
- failure-path testing

Fixtures are invalid for:

- real-evidence qualification
- final Human Gate qualification

## Safety boundary

Even a v6.1-qualified candidate still has:

- human_gate_required = true
- automatic_execution = false
- external_write_enabled = false
- live_execution_allowed = false

v6.1 only qualifies evidence quality. It does not execute commerce.


## GitHub Actions required secrets for Actual Evidence

The scheduled/bootstrapped Actual Evidence workflow requires these repository secrets.

CJ (choose a supported credential mode):
- CJ_ACCESS_TOKEN
- or CJ_API_KEY
- optionally CJ_REFRESH_TOKEN

eBay (choose a supported credential mode):
- EBAY_ACCESS_TOKEN
- or EBAY_CLIENT_ID + EBAY_CLIENT_SECRET

Persistent Shadow:
- SUPABASE_URL
- SUPABASE_SERVICE_ROLE_KEY or SUPABASE_SECRET_KEY

If these are absent, Actual Evidence must report setup_required and must not fall back to fixtures.
