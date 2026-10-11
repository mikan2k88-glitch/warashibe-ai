# Warashibe AI

AIわらしべ長者システム。

## Dropshipping Warashibe

`feature/dropshipping-v0.1` では、既存Warashibe AIを共通Coreとして再利用し、
在庫を持たないドロップシッピング研究レイヤーを実装しています。

Current research version: **2.0**

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

Research v2.0 does **not** create real listings, submit supplier orders,
capture payments, cancel supplier orders, or issue refunds.

Even a valid Human Gate approval does not enable live commerce.
The maturity ceiling is `ready_for_human_gate`.

The scheduled research-proof workflow performs tests and deterministic proof only.
GitHub scheduled workflows execute after the workflow exists on the default branch.
