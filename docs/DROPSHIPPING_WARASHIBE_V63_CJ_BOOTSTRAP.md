# Dropshipping Warashibe v6.3 — CJ Supplier Bootstrap

## Goal

Allow real supplier-side evidence collection to start while eBay Developer access is still pending.

## Flow

CJ API Key
→ dynamic CJ access token
→ bounded CJ Product List V2 READ
→ supplier-only observation normalization
→ hourly snapshot fingerprint
→ append-only Supabase persistence

## Safety boundary

This mode intentionally does not create market evidence or promotion candidates.

- market evidence available: false
- Promotion Review enabled: false
- Human Gate candidate ready: false
- commerce external writes: false
- live execution allowed: false

CJ-only observations use source `cj-supplier-shadow` so they cannot satisfy the v6.1 real-market evidence gate by themselves.

## Snapshot semantics

One unchanged product may be stored once per UTC hour. Repeated runs within the same hour are deduplicated. This permits multi-day evidence accumulation without duplicate flooding.

## Activation

The workflow `.github/workflows/dropshipping-cj-supplier-shadow.yml` is scheduled hourly at minute 17. GitHub scheduled workflows execute from the default branch, so the hourly schedule begins only after this change is merged to `main`.

## Verified result

Feature-branch proof run:
- tests: success
- CJ real READ: 20 products
- Supabase inserted: 20
- persistence errors: 0
- live execution: disabled
