# Dropshipping Warashibe v4.0

## Endpoint

v4.0 adds server-side automatic token acquisition for external READ providers while
preserving the v3.0 Real-Read / Shadow / Promotion Review safety boundary.

## eBay

Browse API research uses an Application access token.

Supported credential modes:

1. EBAY_ACCESS_TOKEN
2. EBAY_CLIENT_ID + EBAY_CLIENT_SECRET

When client credentials are configured, Warashibe mints an Application token using
the client-credentials grant and caches it in-process until near expiry.

No user-consent token is used because current eBay integration is search/read-only.

## CJdropshipping

Supported credential modes:

1. CJ_ACCESS_TOKEN
2. CJ_API_KEY
3. CJ_REFRESH_TOKEN, optionally with CJ_API_KEY fallback

Token issuance/refresh occurs server-side. Token values are never returned by readiness,
status, proof, or dashboard endpoints.

## Persistent Shadow

Optional server-side persistence uses:

- SUPABASE_URL
- SUPABASE_SERVICE_ROLE_KEY or SUPABASE_SECRET_KEY

Database tables are research-only, RLS enabled and append-only for service_role:

- dropship_observations
- dropship_audit_log
- dropship_research_snapshots
- dropship_research_runs

anon/authenticated access is revoked.

## Runtime modes

Startup readiness automatically selects:

- fixture_proof
- real_read_ephemeral_shadow
- real_read_persistent_shadow

None of these modes enables live commerce.

## Render sleep handling

DLL Concierge is a free Render service and may sleep when idle.
Warashibe performs read-only pre-wake/retry against the v5.3 Registry before relying on it.

A scheduled Runtime Probe verifies:

- Warashibe dropship health endpoint
- DLL Concierge Registry reachability
- live_execution_allowed remains false

## v4.0 completion criteria

- automatic eBay Application token proof passes
- automatic CJ access-token proof passes
- token values never appear in status/proof output
- v3 real-read shadow proof remains green
- Promotion Review remains the maturity ceiling
- supplier order/listing/payment/refund writes remain disabled
