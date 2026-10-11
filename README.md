# Warashibe AI

AIわらしべ長者システム。

## Dropshipping Warashibe

`feature/dropshipping-v0.1` では、既存Warashibe AIを共通Coreとして再利用し、
在庫を持たないドロップシッピング研究レイヤーを実装しています。

Current research version: **3.0**

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

Research v3.0 does **not** create real listings, submit supplier orders,
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
