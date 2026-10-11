# Warashibe AI

AIわらしべ長者システム。

## Dropshipping Warashibe

`feature/dropshipping-v0.1` では、既存Warashibe AIを共通Coreとして再利用し、
在庫を持たないドロップシッピング研究レイヤーを実装しています。

Current research version: **5.2**

### Research flow

Supplier offers
→ Evidence / Freshness
→ Economics
→ Policy
→ Working Capital Gate
→ Strategy / Ranking
→ Single Item Selection
→ Shadow
→ Promotion Gate
→ Preflight
→ Sandbox Commerce
→ Settlement
→ Outcome / Learning
→ Research Plan

### Main endpoints

- `GET /dropship/status`
- `GET /dropship/dll/registry`
- `GET /dropship/dll/resilient`
- `POST /dropship/supplier/evaluate`
- `POST /dropship/supplier/rank`
- `POST /dropship/selection/single`
- `POST /dropship/preflight`
- `POST /dropship/shadow/evaluate`
- `POST /dropship/promotion/assess`
- `POST /dropship/sandbox/cycle`
- `POST /dropship/controller/run`
- `POST /dropship/orchestrator/run`
- `POST /dropship/strategy/experiment`
- `POST /dropship/strategy/walk-forward`
- `POST /dropship/campaign/run`
- `POST /dropship/learning/summarize`
- `POST /dropship/research/plan`
- `GET /dropship/v2.0/proof`
- `GET /dropship/v2.0/acceptance`

### Safety boundary

Research v4.0 does **not** create real listings, submit supplier orders,
capture payments, cancel supplier orders, or issue refunds.

Even a valid Human Gate approval does not enable live commerce.
The maturity ceiling is `ready_for_human_gate`.

The scheduled research-proof workflow performs tests and deterministic proof only.
GitHub scheduled workflows execute after the workflow exists on the default branch.


### v3.0 real-read shadow

v3.0 adds bounded read-only integrations for supplier and market evidence:

- CJdropshipping Product List V2 adapter (token required at runtime)
- Printful catalog discovery adapter
- eBay Browse comparable-price adapter
- provider field mapping and data-quality gate
- supplier + market price opportunity ranking
- API-budget guard and quote cache
- append-only research run ledger
- shadow metrics and evidence gate
- promotion review package
- provider failover and read-only circuit breaker

Proof endpoints:

- `GET /dropship/v3.0/proof`
- `GET /dropship/v3.0/acceptance`
- `GET /dropship/v3.0/status`

External provider tokens are only required for actual external reads. Without tokens the deterministic fixture proof remains available.


### v4.0 token automation

v4.0 removes the need to manually maintain short-lived read access tokens.

Supported server-side credential modes:

- CJ: `CJ_ACCESS_TOKEN`, or `CJ_API_KEY`, or `CJ_REFRESH_TOKEN`
- eBay: `EBAY_ACCESS_TOKEN`, or `EBAY_CLIENT_ID` + `EBAY_CLIENT_SECRET`
- Supabase persistence: `SUPABASE_URL` + server secret/service-role key

Readiness endpoints never return credential or token values.

New endpoints include:

- `GET /dropship/tokens/readiness`
- `GET /dropship/persistence/health`
- `GET /dropship/deployment/readiness`
- `GET /dropship/startup/preflight`
- `GET /dropship/runtime/probe`
- `GET /dropship/v4.0/proof`
- `GET /dropship/v4.0/acceptance`
- `GET /dropship/v4.0/status`

The maturity ceiling remains **Promotion Review / Human Gate**.


### v4.1 provider handshake

v4.1 adds a minimal, read-only onboarding handshake before real Shadow collection.

Behavior:

- if CJ/eBay credentials are not configured, the system waits safely
- if credentials are configured, it mints/uses tokens and performs a single minimal READ
- no listing, supplier-order, payment, cancellation, refund, or promotion write is performed
- handshake output never returns token or credential values

Endpoints:

- `GET /dropship/providers/onboarding`
- `GET /dropship/providers/handshake`

A scheduled GitHub Actions handshake produces evidence artifacts and remains safe when credentials are absent.


### v5.2 Promotion Review

v5.2 completes the research path from provider diagnostics through real-product ranking,
long Shadow evidence maturity, and a human-review Promotion Review package.

Milestones included:

- v4.2 provider diagnostics
- v4.3 persistent Real Shadow collection
- v4.4 bounded discovery planning
- v4.5 outlier-filtered market confidence and liquidity
- v5.0 capital-aware real-product ranking
- v5.1 long Shadow evidence maturity
- v5.2 Promotion Review package and queue

A Promotion Review contains expected net profit, margin, required working capital,
market confidence, Shadow observation depth, supplier-cost drift, policy checks,
stop conditions, and Human Gate decision options.

Passing v5.2 does not enable live listing, supplier ordering, payment, cancellation,
refund, or automatic promotion.
