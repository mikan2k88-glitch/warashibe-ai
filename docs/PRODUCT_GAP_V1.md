# Warashibe AI v1.0 Product Gap

更新日: 2026-10-01 JST
対象: `research-lab`
方針: Product-first。P0研究基盤の再設計ではなく、本体v1.0の未完成部分を1件ずつ減らす。

## 1. v1.0の完成定義

v1.0は「実売買の完全自動化」ではない。
仮想市場/サンドボックス上で、商品候補を共通形式へ変換し、安全Policyを通し、
1品だけ選択し、戦略評価・シミュレーション・結果記録まで一貫して実行できる製品状態を指す。

完成判定は次の3段階を区別する。

1. 設計完成: インターフェース、Policy、完成条件が明文化されている。
2. 実証完成: targeted test と exact-SHA CI で、代表ケースのend-to-end動作が証明されている。
3. 運用完成: 定常経路から同じ機能を繰り返し使え、結果保存・監査・失敗時停止が確認されている。

実商品購入、実決済、無人取引、MAIN/productionの自動変更、Secrets/権限拡大はv1.0完成条件に含めない。

## 2. 現在実装済みの製品機能

### API / UI
- FlaskアプリとAPIドキュメント入口。
- `/journey`, `/simulate`, `/campaign/simulate` のシミュレーション系入口。
- strategy API / human-readable report。
- candidate API / candidate form / JSON評価API。
- real-world read-only / proposal-only API境界。

### Simulation / Strategy
- 1回のcycle、campaign再挑戦、複数戦略比較。
- random / safe / balanced / aggressive / adaptive / route。
- route strategy用Candidate経路。
- 目標 `1_000_000`、最大step、履歴、失敗理由、分析統計。

### Candidate / Evaluation
- Candidate共通形式。
- danger filter。
- capital filter。
- ranking engine。
- candidate pipeline。
- demand / value transformation情報をランキングへ反映。

### Policy / Safety
- `policy_engine.py` に1品限定と全資本購入ルール。
- real-world APIは実行/商取引を直接許可しない境界。
- research-lab側にはBuild-first P0 repair line、exact-SHA CI、audit/ledger、problem queue遷移が実証済み。

## 3. 未完成 / 不整合

| ID | Gap | v1.0 | 依存 | 優先 |
| --- | --- | --- | --- | --- |
| PG-001 | Candidate経路のcapital filterが「資本以下」を許可し、全資本1品ルールと不一致 | 必須 | なし | DONE（実証完成） |
| PG-002 | `START_CAPITAL=100` が初期実運用想定約3,000円と不一致。市場段階も100円起点 | 必須 | PG-001 | DONE（実証完成） |
| PG-003 | legacy market/policy経路とCandidate経路でPolicy適用方式が二重化し、同一ルール保証が弱い | 必須 | PG-001 | DONE（実証完成） |
| PG-004 | 実商品候補評価で、価格・流動性・想定売却期間・手数料・真贋・返品の主要項目が統一契約になっていない | 必須 | PG-001, PG-003 | DONE（実証完成） |
| PG-005 | confidenceを仮想success rateとして使う箇所があり、「情報信頼度」と「取引成功確率」の意味が混在 | 必須 | PG-004 | DONE（実証完成） |
| PG-006 | Candidate選択結果を製品側の結果保存/監査へ一貫して残す運用経路が未完成 | 必須 | PG-004 | DONE（実証完成） |
| PG-007 | Supabaseのwarashibe専用テーブル契約はあるが、v1.0製品経路から安全にread/writeする運用完成証拠が不足 | 条件付き必須 | PG-006 | DONE（実証完成） |
| PG-008 | Render / GitHub / Supabaseの接続状態は個別に存在するが、v1.0製品フローとしての運用チェックが未固定 | 必須 | PG-006 | DONE（実証完成・運用確認済み） |
| PG-009 | 実市場APIからの自動商品取得 | Post-v1拡張 | PG-008 | DONE（開発エンドポイント到達） |
| PG-010 | 実購入・実決済・実販売の無人実行 | Post-v1拡張 | PG-009 + Human Gate | DONE（安全実行境界・dry-runエンドポイント到達） |
| PG-011 | 国内市場アクセス調査＋初期物理運用Policy | Post-v1拡張 | PG-009, PG-010 | DONE（開発エンドポイント到達） |
| PG-012 | Yahoo!ショッピング公式read-only connector | Post-v1拡張 | PG-011 | DONE（開発エンドポイント到達） |
| PG-013 | 楽天Product Search＋国内JAN同一商品比較 | Post-v1拡張 | PG-012 | DONE（開発エンドポイント到達） |
| PG-014 | 物理証拠補完＋安全なcross-market proposal | Post-v1拡張 | PG-013 | DONE（開発エンドポイント到達） |
| PG-015 | cross-market proposal/comparisonのSupabase永続化＋鮮度評価 | Post-v1拡張 | PG-014 | DONE（開発エンドポイント到達） |
| PG-016 | Human Review API/UI＋approve/reject監査記録 | Post-v1拡張 | PG-015 | DONE（開発エンドポイント到達） |
| PG-017 | Approved Proposal → Dry-run Commerce Plan | Post-v1拡張 | PG-016 | DONE（開発エンドポイント到達） |
| PG-018 | Realistic Cost / Profit / Stop-loss Model | Post-v1拡張 | PG-017 | DONE（開発エンドポイント到達） |
| PG-019 | Human Review / Price History Dashboard | Post-v1拡張 | PG-018 | DONE（開発エンドポイント到達） |
| PG-020 | Pre-flight Safety Gate | Post-v1拡張 | PG-019 | DONE（開発エンドポイント到達） |
| PG-021 | Human Pilot Session | Post-v1拡張 | PG-020 | DONE（開発エンドポイント到達） |
| PG-022 | Purchase Intent Record | Post-v1拡張 | PG-021 | DONE（開発エンドポイント到達） |
| PG-023 | Commerce Adapter Sandbox | Post-v1拡張 | PG-022 | DONE（開発エンドポイント到達） |
| PG-024 | Live-readiness Audit | Post-v1拡張 | PG-023 | DONE（開発エンドポイント到達） |
| PG-025 | Human Go/No-Go Decision | Post-v1拡張 | PG-024 | DONE（開発エンドポイント到達） |
| PG-026 | Live Pilot Guard | Post-v1拡張 | PG-025 | DONE（開発エンドポイント到達） |
| PG-027 | Live Commerce Adapter Interface | Post-v1拡張 | PG-026 | DONE（開発エンドポイント到達） |
| PG-028 | Single Purchase Execution | Post-v1拡張 | PG-027 | DONE（開発エンドポイント到達・実注文未実行） |
| PG-029 | Purchase Receipt / Reconciliation | Warashibe Loop v2 | PG-028 | DONE（開発エンドポイント到達） |
| PG-030 | Receive / Inspection | Warashibe Loop v2 | PG-029 | DONE（開発エンドポイント到達） |
| PG-031 | Sale Plan | Warashibe Loop v2 | PG-030 | DONE（開発エンドポイント到達） |

## 4. 依存関係

```text
PG-001 Candidate Policy整合
  -> PG-002 3,000円開始整合
  -> PG-003 Policy経路一本化
      -> PG-004 実商品評価契約
          -> PG-005 confidence/success probability分離
          -> PG-006 結果保存/監査
              -> PG-007 Supabase運用接続
              -> PG-008 v1.0運用チェック
```

Post-v1:
- 実市場API自動取得
- 実購入/決済/販売
- production/main自動変更

## 5. 最初にP0ラインへ投入する実問題

### PG-001: Candidate経路が全資本購入ルールを守らない

現状:
- `policy_engine.py` は `FULL_CAPITAL_PURCHASE_REQUIRED=True` で、商品価格と現在資本の一致を要求する。
- `capital_filter.py` は `purchase_price <= current_capital` を購入可能として扱う。
- candidate API / candidate pipeline のテスト例には、現在資本10,000円に対して8,000円商品をallowedとして扱うケースがある。
- `run_candidate_cycle()` の説明も「現在資本以下」を購入可能としている。

期待:
- Candidate経路でも、同一時点では現在資本全額で1品のみを選択する。
- current_capitalとpurchase_priceが一致しない候補はfail-closedでblocked。
- legacy `evaluate_trade()` とCandidate経路の判定意味が一致する。
- 既存の正確一致ケースは通る。
- over-capital / under-capital / zero / invalid capitalはblocked。

実装候補:
1. targeted testを先に追加し、8,000 / 10,000 が現状allowedで失敗することを固定。
2. `capital_filter.evaluate_capital_fit()` を全資本購入Policyへ合わせる。
3. candidate API / pipelineのfixture期待値を更新。
4. exact-SHA CI Greenを確認。
5. controller finalize -> audit -> ledger -> advance_problem_queue。

### PG-001 完成条件
- targeted testが修正前FAIL、修正後PASS。
- research-labの通常CIが同一SHA `completed/success`。
- Candidate経路で under-capital候補がblocked、exact-capital候補のみallowed。
- legacy Policyとの意味不一致が解消。
- P0 repair lineのaudit/ledgerが生成され、次問題へ遷移可能。

## 6. Product-first運用ルール

- CI failureなら新テーマへ逃げず、同じPG-IDを修復する。
- queued / in_progress中は同一HEADへ追加writeしない。
- exact-SHA Green後に次のwriteへ進む。
- 通常の低リスクresearch-lab修正は自律的に進める。
- P0基盤の追加研究は、製品Gapの解消を妨げる具体的問題が出た場合だけ行う。
- CI Green、文書追加、研究テーマ追加だけではv1.0進捗と数えない。


## 7. 実行状況

### PG-001 — 実証完成

- RED: commit `f395cf00c46106f69a36bb02ce82d354d1962bc3` / CI #1034 failure。
  - `10,000` 円資本に対する `8,000` 円候補がallowedになる不整合をtargeted testで再現。
- Product fix: `capital_filter.py` を全資本一致Policyへ変更。
  - repair commit `8f4480fe46c2737ac28d8e5873ed6f54c0b145d8`
  - exact-SHA CI #1035 `completed / success`
- P0 finalize:
  - 実repair evidenceをcontrollerへ投入。
  - audit / ledger / `advance_problem_queue` をproduct testで検証。
- Product-first blocker修復:
  - auditの旧 `research_lab/` 専用path制限を限定製品Pythonパスへ拡張: `8dddb03a6a7f98b2c03953e302a8384ec6846fb9`
  - execution boundaryも同じ限定範囲へ拡張: `171b8d77a3d4524bb71cbb47eeeb645a9b85a52b`
  - 旧Research-first境界テストをProduct-first契約へ同期: `05f5e3ec3db6200dca78da33722d4989a31c77ce`
  - exact-SHA CI #1040 `completed / success`

判定:
- 設計完成: 完了。
- 実証完成: 完了。
- 運用完成: 未判定。定時/定常の自律サイクルから別の製品Gapを同じP0経路で完遂できた時点で判定する。

### PG-002 — 実証完成

- P0 planning:
  - `policy_engine.py` を限定single-file repair対象としてcontrollerがwrite-readyを返すことを確認。
- ベースライン:
  - test追加 commit `afb0b6ee6c48cc4b11234bd317cd9c881663bf23`
  - CI #1042 `completed / success`
- RED:
  - build profile接続 commit `fed644480232c493f48ddf9e06ca197e55998076`
  - CI #1043 `failure`
  - failureは `START_CAPITAL == 3_000` のassertのみで再現。
- Product fix:
  - `policy_engine.START_CAPITAL` を `100 -> 3000` に変更。
  - repair commit `24ef74142c0e5ed651acf56a78a8e991469625b9`
  - exact-SHA CI #1044 `completed / success`
- P0 finalize:
  - before `fed6444...` -> after `24ef741...`
  - path `policy_engine.py`
  - exact-SHA CI evidenceをcontrollerへ投入。
  - audit / ledger / `advance_problem_queue` を固定。
  - evidence commit `8d6630085dc57e9422939a33ced93f7d23f45fba`
  - CI #1045 `completed / success`
- 市場側:
  - `market_engine` には既に3,000円価格帯の商品が存在したため、PG-002では市場データの追加変更は不要と判定。

判定:
- 設計完成: 完了。
- 実証完成: 完了。
- 運用完成: 未判定。

### PG-003 — 実証完成

- ベースライン:
  - contract test追加 commit `6172ca0f0e1db6628cee008c3309f882bd0f8402`
  - CI #1047 `completed / success`
- P0 planning境界確認:
  - 初回接続 commit `2ad766f883e171b3fde2b4270f7029a1de2003d6`
  - CI #1048 `failure`
  - 原因は `change_summary` 内の禁止語 `trade`。P0が安全側に停止したため、意図を変えず表現のみ修正。
- RED:
  - boundary-safe test commit `ec5a15ac28da80029f5cc000b30d5f025ec676e4`
  - CI #1049 `failure`
  - Candidate側decisionに `policy_version` が存在せず、独自Policy実装であることを再現。
- Product fix:
  - `capital_filter.py` をCandidate形式のadapter + `policy_engine.evaluate_trade()` 委譲へ変更。
  - 全資本1品ルールの正本を `policy_engine` へ一本化。
  - repair commit `6791e7a8300af042485077497767aa7f2c1797e4`
  - exact-SHA CI #1050 `completed / success`
- P0 finalize:
  - before `ec5a15a...` -> after `6791e7a...`
  - path `capital_filter.py`
  - exact-SHA CI evidenceをcontrollerへ投入。
  - audit / ledger / `advance_problem_queue` を固定。
  - evidence commit `63e609e2c780b68daf0b571b940f407e6242aee2`
  - CI #1051 `completed / success`

判定:
- 設計完成: 完了。
- 実証完成: 完了。
- 運用完成: 未判定。

### PG-004 — 実証完成

- ベースライン:
  - contract test追加 commit `4f9ab223980152bac80088403365d3311fb07967`
  - CI #1053 `completed / success`
- RED:
  - 既存build-profile製品テストへPG-004契約assertを接続。
  - commit `ad84f241be7e317e1512b497a3a079e9ed47d90f`
  - CI #1054 `failure`
  - `KeyError: evaluation` でCandidate共通契約欠如を再現。
- Product fix:
  - `candidate_engine.py` をv1.2へ更新。
  - 全Candidateに `evaluation` を追加。
  - 共通項目:
    - `purchase_price`
    - `expected_sale_price`
    - `liquidity_score`
    - `estimated_days_to_sell`
    - `estimated_fees`
    - `authenticity_status`
    - `return_risk`
  - 未評価項目は `None` または `unassessed` として明示。
  - repair commit `ebc4431a1f01a9d3d678a0a99ee71d827860f035`
  - exact-SHA CI #1055 `completed / success`
- P0 finalize:
  - before `ad84f24...` -> after `ebc4431...`
  - path `candidate_engine.py`
  - audit / ledger / `advance_problem_queue` を固定。
  - evidence commit `f6c9af445c82e591c886a382256c535cfe068e49`
  - CI #1056 `completed / success`

判定:
- 設計完成: 完了。
- 実証完成: 完了。
- 運用完成: 未判定。

### PG-005 — 実証完成

- RED:
  - contract regression commit `448aa04adc50ed10143cff447b796457c0028b81`
  - CI #1058 `failure`
  - `create_candidate()` が `success_probability` を受け取れず、意味分離未実装を再現。
- 段階修復:
  - Candidate契約:
    - `candidate_engine.py` に `success_probability` を追加。
    - commit `6a83adc5a3cd09ef62318d9d266097452aa61b1b`
    - CI #1059 `failure`、次の混線箇所がrankingであることを確認。
  - Ranking:
    - 期待値・scoreの成功確率を `success_probability` へ分離。
    - `confidence` は情報信頼度として独立加点。
    - commit `16d21712cbd8d5ceab157d9657cc7fb43920c8e5`
    - CI #1060 `failure`、次の混線箇所がdanger filterであることを確認。
  - Danger:
    - risk分類を `success_probability` に変更。
    - `information_confidence` と `success_probability` を別々に返す。
    - commit `5bd961f9067c847e13e2e45da590eb9686625236`
    - CI #1061 `failure`、次の混線箇所がpolicy bridgeであることを確認。
  - Policy bridge:
    - `capital_filter.py` がlegacy Policyへ `success_probability` を渡すよう変更。
    - 未評価時は `confidence` を流用しない。
    - commit `5824619cdc028e1df4bbd7e99548cd2b69cce4d2`
    - CI #1062 `failure`、次の混線箇所がstrategy adapterであることを確認。
  - Strategy adapter:
    - Strategy用 `success_rate` を `success_probability` 由来へ変更。
    - commit `dc5d0380e0beded528af33bcb620d445d438f6e8`
    - CI #1063 `failure`、次の混線箇所がvirtual-market adapterであることを確認。
  - Virtual-market adapter:
    - 仮想市場の `success_rate` を `success_probability` へ格納。
    - 仮想市場データの情報信頼度は `confidence=1.0` として分離。
    - commit `ea6374bd2db55b6a1937277b411d3516a7a19ff0`
    - CI #1064 `completed / success`
  - Simulation:
    - `simulation_engine.py` の成功判定を `confidence` から `success_probability` へ変更。
    - commit `6502be77815f4cd022cbcf60f19d5b1ba4f82469`
    - CI #1065 `completed / success`
- P0 finalize:
  - simulation回帰: `confidence=0.99`, `success_probability=0.4`, `random=0.5` で失敗となることを固定。
  - before `ea6374b...` -> after `6502be7...`
  - path `simulation_engine.py`
  - audit / ledger / `advance_problem_queue` を固定。
  - evidence commit `7eab883bcf67f21fa943a0fde2bb1603cc875747`
  - CI #1066 `completed / success`

判定:
- 設計完成: 完了。
- 実証完成: 完了。
- 運用完成: 未判定。

### 次の実問題

**PG-008: Render / GitHub / Supabaseをv1.0製品フローとして定常監視・運用確認する。**

狙い:
- GPT定時を監督役としてGitHub HEAD/CI、Supabase queue、Render deploy、Product Gapを横断確認する。
- 異常時は同じ問題を修復対象として記録し、正常時は次のProduct Gapへ進む。
- MAIN/production、Secrets、実購入・実決済・課金などはHuman Gateを維持する。


### PG-006 — 実証完成

- RED:
  - queue task `scheduled-pg006-red-919f3e19`。
  - `selection_record` が存在しない状態を固定し、fixed tests failureを確認。
- Product fix:
  - `candidate_pipeline.py` v1.2。
  - `selected_candidate`、`selection_reason`、`candidate_result`、`strategy_result`、`simulation_result` を共通recordとして返す。
  - repair commit `8306e31b4aedd985361cbd7688c5835ef4df9344`。
- Green固定:
  - 同じtargeted testをqueue経路から再投入。
  - commit `d21f5cff5380938a94565aa39ce366a3e2cd75f7`。
  - executor fixed tests success。
- その後のHEAD `73d6d37af253b73a69998f9ef71dfeff5920f75a` でも Research Lab CI Greenを確認。

判定:
- 設計完成: 完了。
- 実証完成: 完了。
- 運用完成: PG-008の定常監視・運用経路で最終確認する。

### PG-007 — 実証完成

- RED:
  - commit `3de312811db15989153e83db2721d4bb9c4b98b1`。
  - CI #1072 failure。
  - `ModuleNotFoundError: research_lab.supabase_selection_record_repository` で未実装を再現。
- Product fix:
  - `research_lab/supabase_selection_record_repository.py` を追加。
  - server-side injected client方式で、secretをコード・返却値・ログへ出さない。
  - record key validation、selection record必須キー検証、duplicate fail-closed、write/read-back契約を実装。
  - repair commit `7823c7d418de1489a3b79c31c02b1c59cc330244`。
  - exact-SHA CI #1073 `completed / success`。
- Supabase:
  - `public.warashibe_selection_records` を追加。
  - `record_key text unique`、`selection_record jsonb`、`created_at`。
  - RLS有効、公開policyなし。server/service-role境界を維持。
  - probe recordで実write -> read-back一致 -> probe cleanupを確認。

判定:
- 設計完成: 完了。
- 実証完成: 完了。
- 運用完成: PG-008のv1.0定常運用経路で最終確認する。


### PG-008 — 実証完成・運用確認済み

- RED:
  - commit `5c2197197b905fe21a4fd77c2000e08a905a5a20`
  - CI #1075 `completed / failure`
  - `research_lab.system_health_contract` 未実装を再現。
- Product fix:
  - `research_lab/system_health_contract.py` を追加。
  - GitHub HEAD/CI、Supabase read/write・stale pending、Render deploy、Product Gap観測を `healthy / degraded / blocked` に分類。
  - commit `3eff41b43a836501339deee323e5e189c7143f17`
  - CI #1076 failureで stale queue時のnext_action差分を検出。
- Minimal repair:
  - stale queue時のnext_actionを `inspect_queue` に修正。
  - commit `02d0e5c1e1156b0fef9b5baafe0a56ce93833b4c`
  - exact-SHA CI #1077 `completed / success`。
- Live operational check:
  - Render `warashibe-ai-research-lab` は同一SHA `02d0e5c1...` で `live`。
  - Supabase `warashibe_dev_queue` に新規pending/leased滞留なし。
  - PG-006/007の保存・Supabase接続実証を前提に、GitHub/Supabase/Renderの定常監督契約がGreen。

判定:
- 設計完成: 完了。
- 実証完成: 完了。
- 運用確認: 完了。
- v1.0 Product Gapの必須項目 PG-001〜PG-008 は、PG-009/010のPost-v1項目を除き到達。


## 8. v1.0 Product-first 開発エンドポイント

2026-10-02時点で、PG-001〜PG-008の必須/条件付き必須項目は設計・実証・必要な運用確認まで到達した。
PG-009（実市場API自動取得）とPG-010（実購入・実決済・実販売の無人実行）は明示的にPost-v1であり、本エンドポイントには含めない。

したがって、本書で定義したv1.0 Product-first開発エンドポイントは到達済みと判定する。
次フェーズへ進む場合は、新しい完成条件とHuman Gate境界を別途定義してから開始する。


### PG-009 — 開発エンドポイント到達

目的:
- 実市場APIから商品情報を自動取得し、既存のcanonical market evidenceへread-onlyで流し込む。
- 実購入・出品・決済などのcommerce操作は一切許可しない。
- 認証情報は環境変数からのみ読み、コード・返却値・ログへ露出しない。

既存資産:
- `research_lab/ebay_browse_transport.py`
  - eBay Browse `GET /buy/browse/v1/item_summary/search` のみに固定。
  - HTTPS / api.ebay.com / 固定pathを検証。
  - redirect拒否。
  - cart/order/offer/payment操作なし。
- `research_lab/ebay_browse_adapter.py`
  - Browse payloadをasking-price evidenceへ正規化。
- `research_lab/live_market_evidence_ingestion.py`
  - 取得済みrecordをcanonical MarketObservationへ検証・正規化。

PG-009 RED / repair:
- RED 1:
  - commit `f5bd79d6df21f017adcf929835108a912f981efb`
  - CI #1079 `completed / failure`
  - `fetch_and_ingest_browse_search` 未実装を再現。
- repair 1:
  - commit `76badf9823545c23a5c64847355bfb183ba3c23e`
  - 既存eBay read-only transport → Browse adapter → canonical ingestionを1関数で接続。
  - CI #1080 `completed / success`。
- RED 2:
  - commit `e6c37345e5b17e8cdadc0ed5f8db4d12df008798`
  - CI #1081 `completed / failure`
  - environment-driven runtime入口未実装を再現。
- repair 2:
  - commit `c12e74f61c118620cc3c5d59957b441e4a19a7d8`
  - `fetch_and_ingest_browse_from_environment()` を追加。
  - `EBAY_BROWSE_ACCESS_TOKEN` を環境からのみ取得。
  - token未設定時はfail-closed。
  - tokenはingestion resultへ含めない。
  - CI #1082 `completed / success`。
  - Render `warashibe-ai-research-lab` は同一SHA `c12e74f6...` で `live`。

安全境界:
- read-only GETのみ。
- 購入、出品、order、payment、account mutationなし。
- redirectでbearer tokenを外部へ転送しない。
- 認証情報の新規発行・表示・変更はHuman Gate。
- CIでは実API通信せず、injected fake transportで自動取得経路を再現。
- 実行環境では既存credentialが設定されている場合のみlive fetch可能。credential未設定は安全停止。

判定:
- 設計完成: 完了。
- 実証完成: 完了。
- runtime接続: 完了。
- Render配備確認: 完了。
- 実市場credentialの存在・値・live API応答は秘密情報/外部依存として別管理し、PG-009開発エンドポイント判定を巻き戻さない。
- **PG-009開発エンドポイント: 到達。**

### 次の境界

PG-010は実購入・実決済・実販売の無人実行でありHuman Gate対象。
PG-009到達後は、明示的な新しい完成条件とHuman Gate承認なしにPG-010へ自動進行しない。


## 9. PG-009 開発エンドポイント

2026-10-02時点で、PG-009のread-only自動市場取得経路は、
eBay Browse transport → adapter → canonical ingestion → environment-driven runtime入口
まで接続され、targeted RED/repair/GreenとRender配備を確認した。

したがって、**PG-009開発エンドポイントは到達済み**と判定する。
PG-010は実commerceを含むため、自動継続対象ではなくHuman Gateを要求する。


### PG-010 — 安全実行境界・dry-run開発エンドポイント到達

目的:
- purchase / payment / sale を共通のcommerce execution contractで扱う。
- 実購入・実決済・実販売を自動実行する前に、Human Gate・資本上限・idempotency・監査を必須化する。
- 開発エンドポイントでは実資金を動かさず、dry-run実行計画と監査記録までを完成させる。

既存資産:
- `research_lab/stripe_sandbox_adapter_design.py`
  - sandbox key / idempotency / webhook / failure classification設計。
- `research_lab/sandbox_trade_ledger_design.py`
  - append-only ephemeral ledgerとrealized PnL設計。
- `research_lab/sandbox_stripe_webhook_ledger_pipeline.py`
  - verified fixture webhook → ledgerのoffline pipeline。
- `research_lab/trade_monitor_guard.py`
  - approval / capital / duplicate / API errorをfail-closed監視。

PG-010 RED / repair:
- RED:
  - commit `02b96e4cc56904ee6e47413c36c3f6eb9920773f`
  - CI #1084 `completed / failure`
  - `research_lab.commerce_execution_gate` 未実装を再現。
- repair:
  - commit `ddc8ff61ae9fe0c40f5d9c4936bb765430ffc56a`
  - `research_lab/commerce_execution_gate.py` を追加。
  - purchase / payment / saleの共通request validationを実装。
  - `trade_id`, `item_id`, `operation`, `amount_jpy`, `capital_before_jpy`, `idempotency_key` を必須化。
  - purchase/paymentでamountがcapitalを超える場合はfail-closed。
  - Human Gate未承認なら `human_gate_required`。
  - Human Gate承認済みでも `dry_run=False` は `live_execution_blocked`。
  - dry-runのみ `dry_run_ready` とし、execution planとaudit recordを生成。
  - purchase/payment/sale authorizationは常にFalse。実外部actionはこのモジュールから許可しない。
  - CI #1085 `completed / success`。
  - Renderは同一SHA `ddc8ff61...` で `live`。
- live-block回帰:
  - commit `98e7d9c3712c2766d6f510e5f8182b91162713b7`
  - Human Gate承認済みでも `dry_run=False` のlive commerceが必ずblockedであることを回帰テスト化。
  - CI #1086 `completed / success`。

安全境界:
- 実購入・実決済・実販売は実行しない。
- 実commerceの外部API呼び出し、実資金移動、production mutationはHuman Gate対象。
- Human Gate承認は、このgateを自動的にlive execution可能へ昇格させない。
- idempotency keyを必須化し、重複実行設計を防ぐ。
- dry-runのexecution plan / audit recordのみ自動生成可能。
- amount > capitalはpurchase/paymentで拒否。
- malformed requestはfail-closed。

判定:
- 設計完成: 完了。
- 共通commerce execution contract: 完了。
- Human Gate enforcement: 完了。
- dry-run実証: 完了。
- live execution fail-closed実証: 完了。
- CI exact-SHA evidence: 完了。
- Render配備: 完了。
- **PG-010の安全実行境界・dry-run開発エンドポイント: 到達。**
- 実commerceそのものの有効化は、本エンドポイントとは分離しHuman Gate後の別運用フェーズとする。

## 10. PG-010 開発エンドポイント

2026-10-02時点で、PG-010は
candidate/market側の判断結果を、purchase / payment / saleの共通commerce execution gateへ渡し、
Human Gate・資本上限・idempotency・監査・dry-runを強制する境界まで到達した。

重要:
- `human_approved=True` だけではlive commerceは許可されない。
- `dry_run=False` は `live_execution_blocked` となる。
- 実資金移動・実購入・実販売はこの開発エンドポイントでは一切行っていない。

したがって、**PG-010安全実行境界・dry-run開発エンドポイントは到達済み**と判定する。
実commerceの有効化はHuman Gateと別途の運用承認を必要とする。


### PG-011 — 国内市場アクセス＋初期物理運用Policy 開発エンドポイント到達

目的:
- 東京での初期実運用を前提に、受取・保管・発送負荷の小さい商品を優先する。
- 初期段階は小型・軽量・低破損リスク・保管容易・国内配送の商品に絞る。
- eBay単独依存ではなく、国内公式read-only市場を調査し、複数市場へ拡張できる入口を固定する。
- 実購入・実決済・実販売はPG-010のHuman Gate / live-block境界を維持する。

国内市場アクセス調査:
- 楽天市場:
  - 公式楽天Web Serviceの商品検索APIを確認。
  - App ID / Access Keyで商品情報取得が可能。
  - フリマ/C2C/オークション掲載は商品検索API対象外。
  - PG-011分類: `official_read_only_api`。
- Yahoo!ショッピング:
  - 公式商品検索(v3)を確認。
  - キーワード、JAN、カテゴリ、ブランド、ストア、中古/新品等で検索可能。
  - PG-011分類: `official_read_only_api`。
- eBay Browse:
  - PG-009で実装済みread-only比較市場として維持。
- メルカリ / Yahoo!オークション:
  - PG-011時点では自動取得へ採用する公式read-only経路を未確定。
  - 無理なスクレイピングを行わず `research_only_until_official_path_confirmed` とする。

物理運用Policy:
- 新規 `research_lab/initial_physical_operation_policy.py`。
- target region: Tokyo, Japan。
- initial package policy: `small_first`。
- preferred package classes: compact / small / 60。
- 初期上限:
  - weight <= 2,000g
  - fragility_score <= 0.4
  - storage_score >= 0.6
  - shipping_cost_jpy <= 1,000
  - domestic_shipping == True
- 物理データ不足は `insufficient_data` としてfail-closed。
- commerce authorizationは常にFalse。

PG-011 RED / repair:
- RED 1:
  - commit `f3e19cc4550d9c5f98f27e601cf3230ce2e37f8f`
  - CI #1088 `completed / failure`
  - `research_lab.initial_physical_operation_policy` 未実装を再現。
- repair 1:
  - commit `d27625511ed8f87fa1b108f2d67897b8e8b80832`
  - 国内市場アクセスsnapshotと初期物理運用Policyを実装。
  - CI #1089 `completed / success`。
- RED 2:
  - commit `459ef8c9e9ae653126f0b59646c8d826ebd50ff5`
  - CI #1090 `completed / failure`
  - Candidateが `package_size_class` 等の物理情報を受け取れないことを再現。
- repair 2:
  - commit `92f4b9313bcede99bd98c2685baf266d18fb37f2`
  - `candidate_engine.py` v1.4。
  - Candidate evaluationへ `physical` 契約を追加。
  - package size / weight / shipping cost / fragility / storage / domestic shippingを保持し、PG-011 Policy評価を埋め込む。
  - CI #1091 `completed / success`。
- contract整合:
  - commit `05172346b57be1020c1ff2844c519662d64911c0`
  - Candidate契約テストをphysical評価へ更新。
  - CI #1092 `completed / success`。
- 国内市場棚卸し:
  - commit `5b160e72f6c016e3627505775ecb8678a7c7c02b`
  - `docs/MARKET_DATA_ACCESS_INVENTORY.md` に公式read-only国内市場分類と物理運用方針を固定。
  - CI #1093 `completed / success`。

判定:
- 国内市場アクセス調査: 完了。
- 初期物理運用Policy: 完了。
- Candidate物理契約: 完了。
- small-first fail-closed評価: 完了。
- 公式read-only / research-only市場分類: 完了。
- 実commerce境界: PG-010のlive-blockを維持。
- **PG-011開発エンドポイント: 到達。**

旧PG-011として記載していた「P0 research-lab監査チェーンの追加拡張」は、製品GapではなくDefer研究項目として扱い、具体的な製品阻害が生じた場合のみ再採番する。

## 11. PG-011 開発エンドポイント

PG-011到達時点で、わらしべAIは
「実市場候補を取得する」だけでなく、
「東京で現実に受け取り・保管・発送しやすい小型商品か」
をCandidateの共通評価契約で判定できる。

初期実運用では大型・重量・高破損・高送料・海外配送中心の商品をfail-closedまたは低優先とし、
国内公式read-only市場を次のconnector候補として扱う。

次の自然な開発対象は、楽天市場またはYahoo!ショッピングのread-only connectorを実装し、
国内実データ → common observation → Candidate → PG-011 physical policy
を一周させることである。


### PG-012 — Yahoo!ショッピング公式read-only connector 開発エンドポイント到達

目的:
- 国内公式市場の実データをread-onlyで取得し、既存のcanonical market evidence / Candidate契約へ接続する。
- PG-011の小型物流Policyを実データ候補へ適用する。
- 物理情報が取得できない場合は推測せずfail-closedする。
- 実購入・注文・決済・出品・account mutationは追加しない。

採用市場:
- Yahoo!ショッピング 商品検索(v3)。
- 公式endpoint:
  `https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch`
- method: GET。
- 必須資格情報: `appid` (Client ID)。
- 実行環境では `YAHOO_SHOPPING_APP_ID` からのみ取得する。

実装:
- `research_lab/yahoo_shopping_ingestion_bridge.py`
- 安全境界:
  - HTTPS固定。
  - host `shopping.yahooapis.jp` 固定。
  - path `/ShoppingWebService/V3/itemSearch` 固定。
  - GETのみ。
  - redirect拒否。
  - query / results / condition(new|used) のみを明示的に組み立てる。
  - Client ID未設定はfail-closed。
  - 資格情報をMarketObservation / Candidate /監査recordへ含めない。
  - order/payment/listing/account mutation APIを持たない。

データ経路:
`Yahoo! Shopping itemSearch JSON`
→ `yahoo_search_to_records()`
→ `live_market_evidence_ingestion.ingest_records()`
→ `MarketObservation`
→ `real_market_adapter.observation_to_candidate()`
→ `Candidate evaluation.physical.policy`

市場データの意味:
- Yahoo!商品検索価格はasking-price evidenceとして扱い、実売却実績へ昇格しない。
- `sale_probability=0.0`, `confidence=0.0` で未評価を明示。
- 商品検索結果で配送サイズ・重量等が保証されない場合、
  `package_size_class / weight_grams / shipping_cost_jpy / fragility_score / storage_score / domestic_shipping`
  は未知のまま保持し、PG-011の `insufficient_data` でfail-closedする。

PG-012 RED / repair:
- RED:
  - commit `3f18d25e0799110d3e13c37527955951d1855b4e`
  - CI #1095 `completed / failure`
  - `research_lab.yahoo_shopping_ingestion_bridge` 未実装を再現。
- repair:
  - commit `d20844d311aceadbf9ddb86fc3452ae4350bedb4`
  - Yahoo!ショッピング公式read-only connectorを実装。
  - fixture payloadから MarketObservation → Candidate → PG-011 physical policyまで接続。
  - CI #1096 `completed / success`。
- safety regression:
  - commit `be63828e6c30dd5b3a70850b4a7c49056fdaf7ae`
  - GET / HTTPS / 固定host / 固定path / redirect拒否 / credential fail-closedを回帰固定。
  - CI #1097 `completed / success`。
- inventory:
  - commit `9fc94483f6ae194201d5771d55998ecd8ff6bfe4`
  - `docs/MARKET_DATA_ACCESS_INVENTORY.md` へ実装済みconnectorとして記録。
  - CI #1098 `completed / success`。

判定:
- 国内公式read-only connector: 完了。
- MarketObservation正規化: 完了。
- Candidate接続: 完了。
- PG-011 physical policy接続: 完了。
- physical data不足時fail-closed: 完了。
- connector安全境界: 完了。
- live commerce: blocked。
- **PG-012開発エンドポイント: 到達。**

## 12. PG-012 開発エンドポイント

PG-012到達時点で、わらしべAIはYahoo!ショッピング公式商品検索の国内商品データを
read-onlyで取得し、canonical MarketObservationからCandidateへ変換し、
PG-011の東京・小型物流Policyで評価できる。

配送サイズ・重量などの物理データをYahoo!商品検索だけで確定できない場合は、
推測で補完せず `insufficient_data` として停止する。

次の自然な開発対象は、Yahoo!検索結果の不足物理情報を公式/許可された追加データで補完する、
または楽天市場を第2の国内公式read-only providerとして追加し、
複数国内市場の比較・価格差・同一商品照合へ進むことである。


### PG-013 — 楽天Product Search＋国内JAN比較 開発エンドポイント到達

目的:
- Yahoo!ショッピングに加え、第2国内公式read-only市場として楽天Product Searchを接続する。
- 商品名の曖昧一致ではなく、JAN/GTINを使って同一商品を保守的に照合する。
- 同一identityが確定した場合だけ、国内市場間のasking-price差を比較する。
- 実購入・注文・決済・出品は行わない。

楽天公式provider:
- endpoint:
  `https://openapi.rakuten.co.jp/ichibaproduct/api/Product/Search/20250801`
- method: GET。
- `productCode` はJANコード。
- required credential:
  - `applicationId`
  - `accessKey`
- 実装ではAccess KeyをURL queryへ含めずHTTP headerへ送る。
- `formatVersion=2` を使用。

実装:
- `research_lab/rakuten_product_ingestion_bridge.py`
- `research_lab/domestic_market_comparison.py`
- `research_lab/yahoo_shopping_ingestion_bridge.py`:
  - Yahoo response `janCode` を canonical `metadata["gtin"]` へ追加。

Rakuten normalization:
- `productCode` → `metadata.gtin`
- `productNo` → `metadata.model_number`
- `salesMinPrice` を優先asking priceとして `purchase_price` へ格納。
- `averagePrice` をaggregate asking-price evidenceとして保持。
- `sale_probability=0.0`, `confidence=0.0`。
- 実売却実績へ昇格しない。

国内同一商品比較:
- 既存 `market_identity_resolution.identity_key()` / `same_identity()` を再利用。
- validated GTIN/JAN一致時のみ `comparison_ready`。
- 不一致時は `identity_mismatch`。
- fuzzy matching / AI推測で異なる商品をmergeしない。
- comparison result:
  - lowest asking price
  - lowest asking source
  - highest asking price
  - price spread
- commerce authorizationは常にFalse。

PG-013 RED / repair:
- RED:
  - commit `5cf6c024eafc86e23226dbb9218697a5e0df51d6`
  - CI #1100 failure。
  - Rakuten connector / domestic comparison未実装を再現。
- Yahoo JAN bridge:
  - commit `dbe21b262acbc25a66e7f8a621fe8e462c7366fe`
  - Yahoo `janCode` → canonical `gtin`。
  - CI #1101 failureで楽天/比較未実装を継続確認。
- Rakuten connector:
  - commit `4605428ef0c5db7265c7b32e0ec1cc1a5f37174f`
  - Rakuten Product Search read-only connectorを追加。
  - CI #1102 failureで比較モジュール未実装を確認。
- domestic comparison:
  - commit `e248c9ebc0799e5b387a00e11df5a900ca36c3e1`
  - JAN/GTIN identity一致時のみ国内価格比較を実装。
  - CI #1103 success。
- safety regression:
  - commit `fea68449f9ed7ba115366a7f937c13a41cb769db`
  - GET/HTTPS/固定host/固定path、Access Key URL非露出、redirect拒否、credential不足fail-closed、identity mismatch拒否を固定。
  - CI #1104 success。
- inventory:
  - commit `7fab3e81031d7438b0c66958a4b6a8c99f9d67f5`
  - 市場データ棚卸しへ第2国内providerとして反映。
  - CI #1105 success。

安全境界:
- Rakuten/Yahooともread-only GETのみ。
- credentialをMarketObservation / Candidate /比較結果へ含めない。
- 実売却実績・成功確率をasking priceから推測しない。
- JAN不一致は比較しない。
- PG-011 physical情報が不足していれば、Candidateは引き続きfail-closed。
- live commerceはPG-010でblockedのまま。

判定:
- 第2国内公式provider: 完了。
- Yahoo JAN normalization: 完了。
- Rakuten JAN normalization: 完了。
- conservative identity resolution: 完了。
- domestic asking-price comparison: 完了。
- connector safety regression: 完了。
- **PG-013開発エンドポイント: 到達。**

## 13. PG-013 開発エンドポイント

PG-013到達時点で、わらしべAIはYahoo!ショッピングと楽天Product Searchから得た
国内市場データをJAN/GTINで同一商品として照合し、
同一性が確定した場合だけ国内asking-price差を比較できる。

これにより、
`国内市場Aの候補 → JAN照合 → 国内市場B価格確認 → Candidate/物理Policy`
という複数市場比較の基礎が成立した。

次の自然な開発対象は、
1. JAN一致候補の物理情報補完、
2. 国内価格差から仕入れ/売却候補を推測せず安全に提案へ繋ぐcomparison policy、
3. Supabaseへcross-market comparison recordを保存して履歴比較すること。


### PG-014 — 物理証拠補完＋安全なcross-market proposal 開発エンドポイント到達

目的:
- PG-013でJAN一致した国内候補について、物理情報を推測せず、出所付きの証拠でのみ補完する。
- 補完後にPG-011の東京・小型物流Policyを再評価する。
- 価格差を「購入命令」へ変換せず、Human Review前提のproposalとして提示できるようにする。
- 実購入・決済・出品・販売は引き続きblockedとする。

実装:
- `research_lab/physical_evidence_enrichment.py`
- `research_lab/cross_market_proposal.py`
- `research_lab/real_market_adapter.py` v0.2
  - MarketObservation.metadataをCandidate metadataへ保持。
  - GTIN/JANなどのcanonical identityを落とさない。
  - 物理項目が存在する場合はCandidate physical evaluationへ渡す。
  - `confidence` と `success_probability` の意味を分離したまま接続。

物理証拠契約:
- validated GTINがCandidateと一致すること。
- 許可source kind:
  - `manufacturer_spec`
  - `official_product_page`
  - `marketplace_shipping_spec`
- `source_ref` と `observed_at` を必須化。
- 必須物理項目:
  - `package_size_class`
  - `weight_grams`
  - `shipping_cost_jpy`
  - `fragility_score`
  - `storage_score`
  - `domestic_shipping`
- 不足、identity mismatch、不正provenanceはfail-closed。
- 補完後もPG-011 physical policyが不合格ならproposalへ進めない。

cross-market proposal:
- PG-013 `comparison_ready` が必須。
- Candidate sourceが比較対象市場に含まれること。
- PG-011 physical policyが `allowed=True` であること。
- 出力は `proposal_type=review_candidate`。
- `human_review_required=True`。
- `commerce_authorized=False`
- `external_action_authorized=False`
- purchase/payment/sale authorizationは全てFalse。

PG-014 RED / repair:
- RED:
  - commit `29426e6f4e6781f68a1aed968322c8724e38283b`
  - CI #1107 failure。
  - physical evidence enrichment / cross-market proposal未実装を再現。
- module implementation:
  - `58660c916656d318c13545f20fd403ff074557a2`
  - `5fc2df5f1c43ac2710c31a95a5949b0ca8889e06`
  - CI #1109 failureで、MarketObservation→Candidate間でGTINが失われる契約不足を検出。
- adapter repair:
  - commit `366392f22bc0b76b7288b7dcf7f303ac93162d94`
  - canonical metadata保持、physical field bridge、confidence/success_probability接続を修正。
  - CI #1110 success。
- safety regression:
  - commit `2c302672c1436d7fd19bf7a851a60ba80100ac4c`
  - invalid provenance / incomplete evidence / identity mismatch / oversized physical policy rejectionを回帰固定。
  - CI #1111 success。

判定:
- canonical GTIN preservation: 完了。
- provenance-bearing physical evidence contract: 完了。
- PG-011 physical re-evaluation: 完了。
- cross-market review proposal: 完了。
- invalid/oversized/unknown evidence fail-closed: 完了。
- live commerce: blocked。
- **PG-014開発エンドポイント: 到達。**

## 14. PG-014 開発エンドポイント

PG-014到達時点で、わらしべAIは
`Yahoo/Rakuten JAN comparison`
→ `出所付き物理証拠`
→ `Candidate physical enrichment`
→ `PG-011 small-first policy`
→ `Human Review用proposal`
までを一周できる。

ただしproposalは「検討候補」であり、購入命令ではない。
実commerceはPG-010のlive-block境界を維持する。

次の自然な開発対象は、
1. proposal/comparison recordのSupabase永続化、
2. 過去価格との差分・鮮度評価、
3. Human Review用のAPI/UI表示、
のいずれかである。


### PG-015 — Supabase永続化＋鮮度評価 開発エンドポイント到達

目的:
- PG-014で生成したcross-market comparison / proposalをappend-onlyで履歴保存する。
- 保存前後に市場観測の鮮度を同一契約で評価する。
- stale/future/invalid timestampはHuman Review利用不可としてfail-closedする。
- 実購入・決済・販売は引き続きblockedとする。

実装:
- `research_lab/cross_market_record.py`
- `research_lab/supabase_cross_market_record_repository.py`
- migration:
  `docs/migrations/2026-10-02_pg015_cross_market_records.sql`

record contract:
- `record_key`
- `identity_key`
- `comparison`
- `proposal`
- `observed_at`
- `captured_at`
- commerce / external action authorizationは常にFalse。

freshness contract:
- timezone付き `observed_at` / `captured_at` を必須化。
- `captured_at >= observed_at`。
- default `max_age_seconds=3600`。
- status:
  - `fresh`: Human Review利用可。
  - `stale`: 利用不可。
  - `future`: 利用不可。
  - `invalid_timestamp_order`: 利用不可。
- freshness判定はcommerce authorizationを変更しない。

Supabase repository:
- table: `warashibe_cross_market_records`
- append-only record key。
- duplicate `record_key` はfail-closed。
- `get(record_key)`。
- `latest_for_identity(identity_key)`。
- server-side client injectionのみ。
- credentialの読み出し・ログ出力なし。

実Supabase migration:
- 新規独立テーブルのみ追加。既存テーブルは変更・削除しない。
- columns:
  - `id bigint identity primary key`
  - `record_key text unique not null`
  - `identity_key text not null`
  - `comparison jsonb not null`
  - `proposal jsonb not null`
  - `observed_at timestamptz not null`
  - `captured_at timestamptz not null`
  - `created_at timestamptz default now()`
- `captured_at >= observed_at` check。
- identity + captured_at index。
- RLS enabled。
- public/anon policyは作成せず、server-side専用。
- security advisorの `rls_enabled_no_policy` はINFOであり、このclosed-by-default設計では意図した状態。

実DB往復証拠:
- test key: `pg015-live-proof-20261002`
- insert成功。
- same record_key read-back成功。
- comparison / proposal / identity / timestamps一致を確認。
- cleanup delete成功。
- テストrowは残していない。

PG-015 RED / repair:
- RED:
  - commit `bb2ffdb9182063f4f20e7b75fd87d208e2c3fdb2`
  - CI #1113 failure。
  - cross-market record / repository未実装を再現。
- implementation:
  - `73b0d246cba2810eb7bba5efd27bba44e531cfe5`
  - `4da0653bbc47f8843c7d792765d72fc76e1cafcd`
  - record freshness contract / Supabase repositoryを実装。
  - CI #1115 success。
- live Supabase:
  - migration `add_warashibe_cross_market_records` success。
  - RLS enabledを確認。
  - insert → read-back → cleanup実証完了。
- migration source:
  - commit `4773146cb19cb57d75b7bdbd50fd5d96240ed35d`
  - CI #1116 success。

判定:
- cross-market append-only record: 完了。
- Supabase persistence contract: 完了。
- live DB schema: 完了。
- live write/read-back proof: 完了。
- freshness gate: 完了。
- stale fail-closed: 完了。
- test data cleanup: 完了。
- live commerce: blocked。
- **PG-015開発エンドポイント: 到達。**

## 15. PG-015 開発エンドポイント

PG-015到達時点で、
`Yahoo/Rakuten comparison`
→ `physical evidence`
→ `Human Review proposal`
→ `freshness evaluation`
→ `Supabase append-only history`
までを一周できる。

古い市場データは保存履歴として残せるが、freshness gateが `stale` の場合は
Human Review用の現行候補として再利用しない。

次の自然な開発対象は、
1. Human Review用API/UI、
2. 最新recordと過去recordの価格差分・トレンド評価、
3. review approve/rejectの監査記録、
のいずれかである。


### PG-016 — Human Review API/UI＋approve/reject監査記録 開発エンドポイント到達

目的:
- PG-015で保存されたfreshなproposalだけを人間が確認できるようにする。
- approve/rejectをappend-only監査記録としてSupabaseへ保存する。
- approveをcommerce authorizationへ変換しない。
- stale proposal、認証不足、二重reviewはfail-closedする。

実装:
- `research_lab/human_review_decision.py`
- `research_lab/supabase_review_decision_repository.py`
- `research_lab/human_review_api.py`
- `research_lab/test_human_review_api.py`
- `app.py` へ `human_review_bp` 登録。
- build profileへHuman Review API回帰テストを追加。

Human Review契約:
- decision: `approve` / `reject` のみ。
- `reviewer_id` / `reason` / `reviewed_at` を必須化。
- PG-015 freshnessが `fresh` のrecordのみreview可。
- 同一 `record_key` は1回だけreview可能。
- approveでも:
  - `commerce_authorized=False`
  - `external_action_authorized=False`
  - `purchase_authorized=False`
  - `payment_authorized=False`
  - `sale_authorized=False`

API/UI:
- `GET /review`
  - Human ReviewブラウザUI。
  - Identity Key / Review Code入力。
  - 最新候補読込。
  - approve / reject。
  - 判断理由入力。
- `POST /api/review/latest`
  - identity単位で最新record取得。
  - freshness再評価。
  - staleは409で拒否。
  - 既review済みrecordは409。
- `POST /api/review/decision`
  - approve/reject監査記録を作成。
  - commerce execution関数は呼ばない。
  - responseに `execution_triggered=False`。

レビュー認証:
- `WARASHIBE_REVIEW_CODE` 環境変数必須。
- 未設定時は `review_runtime_not_configured` で503 fail-closed。
- review codeはURLへ含めない。
- review codeをSupabase監査rowへ保存しない。
- 比較にはconstant-time `hmac.compare_digest` を使用。
- PG-016開発ではsecret値の新規設定・表示・変更は行わない。

Supabase:
- table: `public.warashibe_review_decisions`
- schema:
  - `id bigint identity primary key`
  - `record_key text unique not null`
  - `identity_key text not null`
  - `decision text check (approve/reject)`
  - `reviewer_id text not null`
  - `reason text not null`
  - `reviewed_at timestamptz not null`
  - `created_at timestamptz default now()`
- RLS enabled。
- public/anon policyなし。
- server-side専用closed-by-default。
- migration source:
  `docs/migrations/2026-10-02_pg016_review_decisions.sql`

実DB往復:
- test record `pg016-live-proof-20261002`
- approve監査row insert成功。
- read-back成功。
- record_key / identity_key / decision / reviewer / reason / reviewed_at一致を確認。
- cleanup delete成功。
- テストrowは残していない。

RED / repair / CI:
- decision contract RED:
  - commit `feadfa91f288e6fdd5303f50a0b0aa47f24e52b8`
  - CI #1118 failure。
- decision/repository実装:
  - `dc1dbf065b7ca057e875e968524174afa5873a39`
  - `becbec9ede87dd2576d8204296a0b17474143088`
  - CI #1120 success。
- API/UI RED:
  - `771db7f732bf65ab3d93360d097398944cb341be`
  - build profile追加 `0c2f200f9fe7b23d261cfd68fb1ddf704d92dd0d`
  - CI #1122 failure。
- API/UI repair:
  - `6f80da5f03920f071fad430cd08b1b2e38ffc183`
  - app registration `0f71974c1e5bcee5e4dcda896febac52b48fcdd8`
  - CI #1124 success。
- Supabase migration:
  - `add_warashibe_review_decisions` success。
  - RLS enabledを確認。
  - live insert/read-back/cleanup成功。
- migration source:
  - `6d21b654bc2709dd772623d461af8e2c9bdfd9ba`
  - CI #1125 success。
- interactive UI:
  - `91f9ad6f10a8526a36f2209763b6eb9c0775afad`
  - CI #1126 success。

判定:
- Human Review decision contract: 完了。
- fresh-only review gate: 完了。
- approve/reject API: 完了。
- browser Human Review UI: 完了。
- append-only Supabase audit: 完了。
- live DB roundtrip: 完了。
- duplicate review rejection: 完了。
- stale review rejection: 完了。
- approve→commerce非接続: 完了。
- review secret runtime dependency: fail-closed。
- live commerce: blocked。
- **PG-016開発エンドポイント: 到達。**

## 16. PG-016 開発エンドポイント

PG-016到達時点で、
`cross-market proposal`
→ `freshness gate`
→ `Human Review UI/API`
→ `approve/reject audit`
→ `Supabase append-only history`
までを一周できる。

approveは「人間が候補を確認し、次段階の検討を許可した」という監査イベントであり、
購入・決済・販売を実行する権限ではない。
実commerceはPG-010のlive-blockを維持する。

次の自然な開発対象は、
1. review後のdry-run commerce plan連携、
2. 過去review/価格履歴のダッシュボード、
3. 有人パイロット向けの最終確認フロー、
である。


### PG-017 — Approved Proposal → Dry-run Commerce Plan 開発エンドポイント到達

目的:
- PG-016のapprove監査済みproposalだけをdry-run commerce planへ変換する。
- dry-run planをappend-onlyの監査artifactとしてSupabaseへ保存できるようにする。
- approveを実購入・決済・販売の許可へ昇格させない。

実装:
- `research_lab/dry_run_commerce_plan.py`
- `research_lab/supabase_dry_run_plan_repository.py`
- `research_lab/test_dry_run_commerce_plan.py`
- `docs/migrations/2026-10-02_pg017_dry_run_plans.sql`
- build profileへPG-017 contract testを追加。

dry-run contract:
- source review decisionは `approve` のみ。
- reviewの `record_key` / `identity_key` はsource proposal recordと一致必須。
- proposalは `proposal_ready` かつ Human Review必須。
- `execution_mode=dry_run`。
- `human_final_confirmation_required=True`。
- `execution_triggered=False`。
- `commerce_authorized=False`。
- `external_action_authorized=False`。
- purchase/payment/sale authorizationは全てFalse。
- reject済みproposalはplan生成不可。

Supabase:
- table: `public.warashibe_dry_run_plans`
- append-only plan key。
- columns:
  - `id bigint identity primary key`
  - `plan_key text unique not null`
  - `source_record_key text not null`
  - `identity_key text not null`
  - `review_decision text check (approve only)`
  - `plan jsonb not null`
  - `generated_at timestamptz not null`
  - `created_at timestamptz default now()`
- RLS enabled。
- public/anon policyなし。
- server-side専用closed-by-default。

実DB往復:
- test key: `pg017-live-proof-20261002`
- insert成功。
- read-backでplan key / source record / identity / approve / dry_run / commerce_authorized=Falseを確認。
- cleanup delete成功。
- テストrowは残していない。

主要commits:
- contract test: `90d2c19f295ba93170f640000f25281444e247d3`
- RED activation: `17b2e1c771724006e2bb2529d3a141fc1bcc31ec`
- plan implementation: `c849506e4e3111b6c1bfb3bc41576e1788880917`
- Supabase repository: `c9a2da7a32cd63923ba3703e6172fa32e85f2fd7`
- migration source: `6b9f411406b1aa7cacac6693f605b2c03bba2880`

判定:
- approved-only plan generation: 完了。
- rejected review fail-closed: 完了。
- dry-run authorization boundary: 完了。
- Supabase append-only persistence: 完了。
- live DB roundtrip: 完了。
- test row cleanup: 完了。
- live commerce: blocked。
- **PG-017開発エンドポイント: 到達。**

## 17. PG-017 開発エンドポイント

PG-017到達時点で、
`fresh proposal`
→ `Human Review approve`
→ `dry-run commerce plan`
→ `Supabase append-only history`
までを一周できる。

dry-run planは取引計画の監査artifactであり、注文・決済・出品・販売を一切実行しない。
次の開発対象はPG-018の現実的な費用・利益・損切りモデルである。


### PG-018 — Realistic Cost / Profit / Stop-loss Model 開発エンドポイント到達

目的:
- PG-017 dry-run planを現実的な費用構造で評価する。
- 単純な売価−仕入ではなく、送料・梱包・販売手数料・決済手数料・返品等リスク引当を含める。
- break-even価格と最大許容損失からstop-loss価格を逆算する。
- 経済合理性を実行許可へ変換しない。

実装:
- `research_lab/commerce_economics.py`
- `research_lab/supabase_economic_assessment_repository.py`
- `research_lab/test_commerce_economics.py`
- `docs/migrations/2026-10-02_pg018_economic_assessments.sql`
- build profileへPG-018 contract testを追加。

経済モデル:
- fixed cost =
  `purchase_price + inbound_shipping + packaging_cost + return_risk_reserve`
- selling fee = `expected_sale_price * selling_fee_rate`
- payment fee = `expected_sale_price * payment_fee_rate`
- expected net profit =
  `sale_price - fixed_cost - selling_fee - payment_fee`
- expected margin = `expected_net_profit / sale_price`
- break-even price =
  `ceil(fixed_cost / (1 - total_fee_rate))`
- stop-loss price =
  `ceil((fixed_cost - max_loss) / (1 - total_fee_rate))`
- `max_hold_days` を明示。
- `profit_gate.economically_viable` は
  `min_net_profit_jpy` と `min_margin_rate` の両方を満たす場合のみTrue。

安全境界:
- economicsは分析結果のみ。
- `execution_mode=dry_run`
- `execution_triggered=False`
- `commerce_authorized=False`
- `external_action_authorized=False`
- purchase/payment/sale authorization=False。
- profit gate通過は購入許可ではない。

Supabase:
- table: `public.warashibe_economic_assessments`
- `assessment_key` uniqueのappend-only監査保存。
- `plan_key` / `identity_key` / `economics jsonb` / `evaluated_at` を保持。
- RLS enabled。
- public/anon policyなし。
- server-side専用closed-by-default。

実DB往復:
- test key: `pg018-live-proof-20261002`
- insert成功。
- read-back:
  - expected net profit = 520円
  - break-even = 4399円
  - stop-loss = 3820円
  - economically viable = true
  - commerce authorized = false
- cleanup delete成功。
- テストrowは残していない。

主要commits:
- contract test: `1e1b88035a5a01dba46997ea59e2090b3525c9c1`
- RED activation: `ce454a3adfe1fb48060234a2c4e1c13df262d8e7`
- economics implementation: `56752c08018b25bb6b2a99ec9ccf6a31739ee7e5`
- repository: `6af7532e4e23b39e5ad135adc8ca9acc6aaa0b95`
- migration source: `71efdc29f1b6a24a267c923497ae04f563397f99`

Render:
- economics implementation SHAはlive。
- repository SHAはbuild successfulと新instance起動をlogで確認。
- status APIは長めにupdate_in_progressを返し、その後続migration source deployはqueued表示。
- コード起因のbuild failure証拠はなく、反映status遅延として継続扱い。

判定:
- realistic cost model: 完了。
- expected net profit / margin: 完了。
- break-even: 完了。
- max-loss based stop-loss: 完了。
- profit gate: 完了。
- economic assessment persistence: 完了。
- live DB roundtrip: 完了。
- test row cleanup: 完了。
- live commerce: blocked。
- **PG-018開発エンドポイント: 到達。**

## 18. PG-018 開発エンドポイント

PG-018到達時点で、
`Human Review approve`
→ `dry-run commerce plan`
→ `realistic economics`
→ `profit / break-even / stop-loss gate`
→ `Supabase append-only assessment history`
までを一周できる。

経済合理性が高くても実購入・決済・販売は開始しない。
次の自然な開発対象は、過去価格・review・plan・economic assessmentをまとめるHuman Review/Price History Dashboardである。


### PG-019 — Human Review / Price History Dashboard 開発エンドポイント到達

目的:
- PG-015〜018の履歴をidentity単位で一画面へ統合する。
- price / proposal / review / dry-run plan / economicsをread-onlyで確認可能にする。
- 履歴閲覧をcommerce executionへ接続しない。

実装:
- `research_lab/history_dashboard_api.py`
- `research_lab/test_history_dashboard_api.py`
- `app.py` へ `history_dashboard_bp` 登録。
- build profileへPG-019 contract testを追加。

API/UI:
- `GET /history`
  - browser dashboard。
  - Identity Key / Review Code入力。
  - 閲覧専用であることを明示。
- `POST /api/history`
  - identity単位で以下をまとめて返す:
    - cross-market records
    - Human Review decisions
    - dry-run plans
    - economic assessments
  - latest snapshot:
    - lowest/highest asking price
    - latest review decision
    - latest plan key
    - expected net profit
    - break-even
    - stop-loss
    - economically viable
- review codeはconstant-time比較。
- runtime dependency不足時はfail-closed。

安全境界:
- read-only。
- 新規DB mutationなし。
- `execution_triggered=False`
- `commerce_authorized=False`
- `external_action_authorized=False`
- purchase/payment/sale actionなし。

CI:
- contract commit: `62ecbcadf1e86de5d1a88997c4d9d0779b13f969`
  - CI #1140 success。
- RED activation: `8507a29a8aeaf2e360c2d12de505f8a8927b696e`
  - CI #1141 failure。
- repair: `751aaccf8a9d1ed999da49e109fa3b8342595a86`
  - CI #1142 success。
- route registration: `c3e312b032977fd3edf185b211c983130f42918b`
  - CI #1143 success。

Render:
- exact SHA `c3e312b032977fd3edf185b211c983130f42918b` live。
- `GET /history` live画面確認済み。
- heading: `Warashibe AI History Dashboard`
- 「閲覧専用。ここから購入・決済・販売は実行されない」表示を確認。

判定:
- cross-market history view: 完了。
- review history view: 完了。
- dry-run plan history view: 完了。
- economics history view: 完了。
- browser dashboard: 完了。
- live route: 完了。
- commerce mutation: なし。
- live commerce: blocked。
- **PG-019開発エンドポイント: 到達。**

## 19. PG-019 開発エンドポイント

PG-019到達時点で、
`market observation history`
→ `Human Review history`
→ `dry-run plan history`
→ `economics history`
をidentity単位で人間が一画面確認できる。

次の開発対象はPG-020のPre-flight Safety Gateである。


### PG-020 — Pre-flight Safety Gate 開発エンドポイント到達

目的:
- Human Review approve後、実購入直前を想定した全条件の再検証を行う。
- freshness / identity chain / Human Review / physical policy / inventory / price / budget / economics / duplicate transaction / dry-run boundaryを一括判定する。
- 通過結果を `ready_for_human_purchase_confirmation` までに留め、実購入・決済・販売を起動しない。

実装:
- `research_lab/preflight_safety_gate.py`
- `research_lab/supabase_preflight_assessment_repository.py`
- `research_lab/test_preflight_safety_gate.py`
- `docs/migrations/2026-10-03_pg020_preflight_assessments.sql`
- build profileへPG-020 contract testを追加。

Pre-flight checks:
- PG-015 freshness = fresh。
- record / review / plan / economics のidentity chain一致。
- Human Review decision = approve。
- physical policy = allowed。
- inventory available。
- current purchase priceの上昇率が上限以内。
- required cash <= available capital。
- PG-018 economics profit gate = viable。
- duplicate transaction = false。
- dry-run authorization境界維持。

資本・ポジション:
- `quantity=1`
- `capital_commitment_mode=single_item`
- `parallel_positions_allowed=False`
- current purchase price + inbound shipping + packaging costをrequired cashとして予算判定。
- 3,000円資本の実証ケースではrequired cash 3,000円で通過。

出力:
- `status=preflight_ready / preflight_blocked`
- `ready_for_human_purchase_confirmation=True/False`
- `human_final_confirmation_required=True`
- `execution_mode=dry_run`
- `execution_triggered=False`
- `commerce_authorized=False`
- `external_action_authorized=False`
- purchase/payment/sale authorization=False。

Supabase:
- table: `public.warashibe_preflight_assessments`
- `preflight_key` uniqueのappend-only監査保存。
- columns:
  - `id bigint identity primary key`
  - `preflight_key text unique not null`
  - `record_key text not null`
  - `plan_key text not null`
  - `identity_key text not null`
  - `preflight jsonb not null`
  - `evaluated_at timestamptz not null`
  - `created_at timestamptz default now()`
- RLS enabled。
- public/anon policyなし。
- server-side専用closed-by-default。
- advisorの `rls_enabled_no_policy` は、この設計では意図したINFO。

実DB往復:
- test key: `pg020-live-proof-20261003`
- insert成功。
- read-back:
  - status = preflight_ready
  - ready_for_human_purchase_confirmation = true
  - commerce_authorized = false
  - quantity = 1
  - parallel_positions_allowed = false
- cleanup delete成功。
- テストrowは残していない。

CI:
- contract commit: `b2102f9f8bbda65dccb3d0b15f6e920696f6fae2`
  - CI #1145 success。
- RED activation: `ffa05db97847c680013db4b76b7a8ea1330dc237`
  - CI #1146 failure。
- gate implementation: `1e980ec813a49f04fb4d3f7da9b688e2e38b6bad`
  - CI #1147 success。
- repository: `13d9938c2f5474e48fc18806c67bbdefc7edec80`
  - CI #1148 success。
- migration source: `9430868d4c5ccfeaf902310cee5469f4480e86b0`
  - CI #1149 success。

Render:
- repository SHA `13d9938...` live。
- gate implementation SHAは正常deploy済み。
- migration source SHAはstatus API上 update_in_progress表示だが、コード起因failureなし。

判定:
- freshness re-check: 完了。
- identity chain: 完了。
- Human Review gate: 完了。
- physical policy gate: 完了。
- inventory gate: 完了。
- price drift gate: 完了。
- budget gate: 完了。
- economics gate: 完了。
- duplicate transaction gate: 完了。
- single-item / no-parallel-position: 完了。
- append-only preflight audit: 完了。
- live DB roundtrip: 完了。
- live commerce: blocked。
- **PG-020開発エンドポイント: 到達。**

## 20. PG-020 開発エンドポイント

PG-020到達時点で、
`fresh proposal`
→ `Human Review approve`
→ `dry-run commerce plan`
→ `realistic economics`
→ `Pre-flight Safety Gate`
→ `ready_for_human_purchase_confirmation`
までを一周できる。

ただし `ready_for_human_purchase_confirmation=True` は「人間が最終購入判断を行える状態」であり、
購入・決済・販売の実行権限ではない。
PG-010 live-commerce blockを維持する。

次の自然な開発対象はPG-021 Human Pilot Sessionである。


### PG-021 — Human Pilot Session 開発エンドポイント到達

目的:
- PG-020でpreflight_readyとなった1候補を、人間が最終確認するための有人pilot sessionへ束ねる。
- 1セッション=1候補=1品を維持する。
- pilot sessionをappend-onlyで監査保存する。
- 実購入・決済・販売は起動しない。

実装:
- `research_lab/human_pilot_session.py`
- `research_lab/supabase_pilot_session_repository.py`
- `research_lab/test_human_pilot_session.py`
- `docs/migrations/2026-10-03_pg021_pilot_sessions.sql`
- build profileへPG-021 contract testを追加。

session contract:
- source preflightは `preflight_ready` のみ。
- `ready_for_human_purchase_confirmation=True` 必須。
- `human_final_confirmation_required=True` 維持。
- `session_state=awaiting_human_final_confirmation`。
- `quantity=1`。
- `capital_commitment_mode=single_item`。
- `parallel_positions_allowed=False`。
- `purchase_intent_recorded=False`。
- `execution_mode=dry_run`。
- `execution_triggered=False`。
- commerce/external/purchase/payment/sale authorizationは全てFalse。
- preflight_blockedからsession生成不可。

Supabase:
- table: `public.warashibe_pilot_sessions`
- append-only `session_key`。
- RLS enabled。
- public/anon policyなし。
- server-side専用closed-by-default。

実DB往復:
- test key: `pg021-live-proof-20261003`
- insert / read-back成功。
- quantity=1、parallel_positions_allowed=false、
  human_final_confirmation_required=true、
  commerce_authorized=falseを確認。
- cleanup成功。テストrowは残していない。

CI:
- contract commit `c52071d056b2598cdb5358385b6e18e2cfdea77f` — CI #1151 success。
- RED `239751a739cd3af1ca5d5212af97063f9c7cc912` — CI #1152 failure。
- implementation `3f1ef2e606db88ea946387d36b3fcd3aa6097b2f` — CI #1153 success。
- repository `3d7e257c55519386fcee6adb305df952113831f0` — CI #1154 success。
- migration source `b5311ee3e2bcedff2bd568b4ab5e66616c061644` — CI #1155 success。

判定:
- preflight-ready → pilot session: 完了。
- blocked preflight rejection: 完了。
- single-item / no-parallel-position: 完了。
- append-only persistence: 完了。
- live DB roundtrip: 完了。
- Human final confirmation gate: 維持。
- live commerce: blocked。
- **PG-021開発エンドポイント: 到達。**

## 21. PG-021 開発エンドポイント

PG-021到達時点で、
`Pre-flight Safety Gate`
→ `Human Pilot Session`
→ `awaiting_human_final_confirmation`
までを監査可能な状態で一周できる。

次の開発対象はPG-022 Purchase Intent Recordである。


### PG-022 — Purchase Intent Record 開発エンドポイント到達

目的:
- PG-021 Human Pilot Sessionで最終確認待ちの1候補について、人間の「この条件なら購入してよい」という意思を監査記録として保存する。
- intentに価格上限・総額上限・有効期限を持たせる。
- intentを注文・決済・販売の実行権限へ変換しない。

実装:
- `research_lab/purchase_intent.py`
- `research_lab/supabase_purchase_intent_repository.py`
- `research_lab/test_purchase_intent.py`
- `docs/migrations/2026-10-03_pg022_purchase_intents.sql`
- build profileへPG-022 contract testを追加。

Purchase Intent contract:
- source sessionは `pilot_session_ready`。
- `session_state=awaiting_human_final_confirmation`。
- `human_final_confirmation_required=True`。
- sessionあたりintentは1件のみ。
- `quantity=1`。
- `parallel_positions_allowed=False`。
- `max_purchase_price_jpy <= max_total_cost_jpy`。
- `max_total_cost_jpy <= available_capital_jpy`。
- `max_total_cost_jpy >= current required cash`。
- `expires_at > confirmed_at`。
- `human_confirmation_recorded=True`。
- `order_submission_authorized=False`。
- `execution_mode=dry_run`。
- `execution_triggered=False`。
- commerce/external/purchase/payment/sale authorizationは全てFalse。

Supabase:
- table: `public.warashibe_purchase_intents`
- `intent_key` unique。
- `session_key` unique。
- append-only intent audit。
- confirmed_at / expires_atを保持。
- expires_at > confirmed_at check。
- RLS enabled。
- public/anon policyなし。
- server-side専用closed-by-default。

実DB往復:
- test key: `pg022-live-proof-20261003`
- max purchase price = 2,850円。
- max total cost = 3,000円。
- insert / read-back成功。
- order_submission_authorized=false。
- commerce_authorized=false。
- quantity=1。
- parallel_positions_allowed=false。
- cleanup成功。テストrowは残していない。

CI:
- contract `fa9fa7a1a883839a3624bc0fd8fc2fa712d91d15` — CI #1157 success。
- RED `84ad522643f1543c7dcb970bf52a991b8b016860` — CI #1158 failure。
- implementation `6fe5a597b9a09502c7bcb2351ff74122c6a5c950` — CI #1159 success。
- repository `6093ee88f99f7a70f6908640b63c4a36f47693ab` — CI #1160 success。
- migration source `a19d55359366cdf4fcab68e1f4761241a69d92c8` — CI #1161 success。

判定:
- Human Pilot Session → Purchase Intent: 完了。
- price/cost/time bounds: 完了。
- one intent per session: 完了。
- single-item/no-parallel rule: 維持。
- append-only persistence: 完了。
- live DB roundtrip: 完了。
- order submission authorization: blocked。
- live commerce: blocked。
- **PG-022開発エンドポイント: 到達。**

## 22. PG-022 開発エンドポイント

PG-022到達時点で、
`Pre-flight Safety Gate`
→ `Human Pilot Session`
→ `Human Purchase Intent`
までを、価格・総額・期限つきで監査保存できる。

Purchase Intentは「人間が条件付きで購入意思を記録した」だけであり、
注文API・決済API・出品APIを呼ぶ権限ではない。
`order_submission_authorized=False` と PG-010 live-commerce blockを維持する。

次の自然な開発対象はPG-023 Commerce Adapter Sandboxである。


### PG-023 — Commerce Adapter Sandbox 開発エンドポイント到達

目的:
- PG-022 Purchase Intentを入力に、将来のcommerce adapter呼び出し境界をsandbox/no-opで固定する。
- purchase/sale要求を受けても外部ネットワークwriteを一切行わない。
- sandbox試行をappend-only監査保存する。

実装:
- `research_lab/commerce_adapter_sandbox.py`
- `research_lab/supabase_sandbox_commerce_attempt_repository.py`
- `research_lab/test_commerce_adapter_sandbox.py`
- `docs/migrations/2026-10-03_pg023_sandbox_commerce_attempts.sql`
- build profileへPG-023 contract testを追加。

adapter contract:
- `adapter_mode=sandbox_noop`
- purchase/saleの両要求を `status=sandbox_blocked` で返す。
- `network_call_attempted=False`
- `external_write_attempted=False`
- `order_created=False`
- `payment_created=False`
- `listing_created=False`
- `sale_created=False`
- `execution_triggered=False`
- commerce/external/purchase/payment/sale authorizationは全てFalse。
- reason=`live_commerce_disabled`。

Supabase:
- table: `public.warashibe_sandbox_commerce_attempts`
- append-only `attempt_key`。
- intent/provider/requested_action/result/attempted_atを保持。
- RLS enabled。
- public/anon policyなし。
- server-side専用closed-by-default。

実DB往復:
- test key: `pg023-live-proof-20261003`
- provider=yahoo_shopping / action=submit_purchase。
- insert/read-back成功。
- sandbox_noop / network_call_attempted=false / external_write_attempted=false / order_created=false / commerce_authorized=falseを確認。
- cleanup成功。テストrowは残していない。

CI:
- contract `992707d0d10c2db5b841f0aaec8a466571e25192` — CI #1163 success。
- RED `416031c0d10b7f488b3adfaf66ae877733d58741` — CI #1164 failure。
- implementation `2f65702133e3f0c55591b7b0b93735af6f2f82a1` — CI #1165 success。
- repository `dc61b234b4be110920b274062da4cecb4eff945c` — CI #1166 success。
- migration source `0c21be5e8f4acd58e6d8ef787946bdc561be6190` — CI #1167 success。

判定:
- sandbox purchase adapter: 完了。
- sandbox sale adapter: 完了。
- external network/write prohibition: 完了。
- append-only audit: 完了。
- live DB roundtrip: 完了。
- live commerce: blocked。
- **PG-023開発エンドポイント: 到達。**

## 23. PG-023 開発エンドポイント

PG-023到達時点で、
`Human Purchase Intent`
→ `Commerce Adapter Sandbox`
→ `sandbox_blocked/no-op audit`
までを一周できる。

このadapterは実注文を実行できない。
次の開発対象はPG-024 Live-readiness Auditである。


### PG-024 — Live-readiness Audit 開発エンドポイント到達

目的:
- PG-011〜023で構築した安全・監査・dry-run系統を総合監査する。
- 全required check通過時も、実取引許可ではなくHuman go/no-go判定へ進めるだけにする。
- readiness gapが1つでもあればfail-closedでHuman go/no-go不可にする。

実装:
- `research_lab/live_readiness_audit.py`
- `research_lab/supabase_live_readiness_audit_repository.py`
- `research_lab/test_live_readiness_audit.py`
- `docs/migrations/2026-10-03_pg024_live_readiness_audits.sql`
- build profileへPG-024 contract testを追加。

required checks:
- identity match。
- physical policy。
- freshness。
- Human Review approve。
- economics viable。
- preflight ready。
- pilot session ready。
- purchase intent valid。
- sandbox adapter verified。
- sandbox network call not attempted。
- sandbox external write not attempted。
- duplicate transaction guard。
- single-item guard。
- parallel positions disabled。
- RLS enabled。
- public/anon write policy absent。
- audit cleanup verified。
- live-commerce block enabled。
- rollback plan documented。
- refund/cancel path documented。
- marketplace terms review requirement maintained。
- secrets server-side only。

出力:
- `status=live_readiness_audit_complete`
- `all_required_checks_passed=True/False`
- `ready_for_human_go_no_go=True/False`
- `human_go_no_go_required=True`
- pass時 `recommended_next_stage=human_live_pilot_decision`
- fail時 `recommended_next_stage=repair_readiness_gaps`
- `live_commerce_authorized=False`
- `execution_mode=audit_only`
- `execution_triggered=False`
- commerce/external/purchase/payment/sale authorizationは全てFalse。

Supabase:
- table: `public.warashibe_live_readiness_audits`
- append-only `audit_key`。
- auditor_id/audited_at/audit jsonbを保持。
- RLS enabled。
- public/anon policyなし。
- server-side専用closed-by-default。

実DB往復:
- test key: `pg024-live-proof-20261003`
- all_required_checks_passed=true。
- ready_for_human_go_no_go=true。
- human_go_no_go_required=true。
- live_commerce_authorized=false。
- commerce_authorized=false。
- insert/read-back成功。
- cleanup成功。テストrowは残していない。

CI:
- contract `6cb2dc602bded467f3a35de266d51f956f1d00f6` — CI #1169 success。
- RED `9b3b6c2e9f54aab94763faba9b499de323b691f6` — CI #1170 failure。
- implementation `13905ea34fb0bbdf37ee17c449927538f7a6d1f6` — CI #1171 success。
- repository `dc68b9facd4176280db7ac7d98567784571aabe7` — CI #1172 success。
- migration source `648022d840fe9a3c7cae9c6e92a265c8df6556d0` — CI #1173 success。

判定:
- end-to-end readiness checklist: 完了。
- fail-closed readiness gap handling: 完了。
- Human go/no-go boundary: 完了。
- append-only audit persistence: 完了。
- live DB roundtrip: 完了。
- live commerce authorization: blocked。
- **PG-024開発エンドポイント: 到達。**

## 24. PG-024 開発エンドポイント

PG-024到達時点で、
`market discovery`
→ `identity/physical evidence`
→ `Human Review`
→ `dry-run plan/economics`
→ `Pre-flight`
→ `Human Pilot Session`
→ `Purchase Intent`
→ `Commerce Adapter Sandbox`
→ `Live-readiness Audit`
までを監査可能な状態で一周できる。

全チェックが通っても実購入・決済・販売は開始しない。
次の段階はHuman go/no-goによるLimited Live Pilot判断であり、PG-010 live-commerce blockは現在も維持する。


### PG-025 — Human Go/No-Go Decision 開発エンドポイント到達

目的:
- PG-024 readiness audit通過後のHuman GO/NO_GOを監査記録する。
- GOでも実購入権限へ変換しない。
- Limited Live Pilotのscopeだけを固定する。

実装:
- `research_lab/human_go_no_go.py`
- `research_lab/supabase_live_pilot_decision_repository.py`
- `research_lab/test_human_go_no_go.py`
- `docs/migrations/2026-10-03_pg025_live_pilot_decisions.sql`

GO scope:
- approved budget = 最大3,000円。
- max transactions = 1。
- quantity per transaction = 1。
- parallel positions = false。
- approved provider allowlist。
- valid_until必須。
- Human final buy required。

安全境界:
- `live_execution_authorized=False`
- `execution_triggered=False`
- commerce/external/purchase/payment/sale authorization=False。

Supabase:
- table: `public.warashibe_live_pilot_decisions`
- decision_key unique / append-only。
- decision = go/no_go。
- RLS enabled、public/anon policyなし。

実DB:
- `pg025-live-proof-20261003`
- GO / budget=3000 / max_transactions=1をread-back。
- live_execution_authorized=false / commerce_authorized=false確認。
- cleanup済み。

CI:
- contract `23193f50c647dab6b2637ebf4b49965400d06ca9` — #1175 success。
- RED `417f88bffee29536e8412758e1c8d2b5c943687f` — #1176 failure。
- implementation `3c243986ec37d2ae8a5408d08257cef5aa4aa00e` — #1177 success。
- repository `552ecb972d279aba74e5c834cce9cf782ec6a788` — #1178 success。
- migration source `df72665c15a994d644882d86d8c1758fa8d55b7b` — #1179 success。

判定:
- Human GO/NO_GO audit: 完了。
- bounded pilot scope: 完了。
- live execution authorization: blocked。
- **PG-025開発エンドポイント: 到達。**

## 25. PG-025 開発エンドポイント

PG-025到達時点で、PG-024 readiness auditからHuman GO/NO_GOを記録し、
GOの場合でも「限定pilot scopeを承認した」だけの状態を保持する。
次の開発対象はPG-026 Live Pilot Guard。


### PG-026 — Live Pilot Guard 開発エンドポイント到達

目的:
- PG-025 GO scopeとPG-022 Purchase Intentを、将来のlive adapter直前に再検証する。
- 予算・取引数・1品制約・provider allowlist・期限・価格上限・総額上限・重複防止・open position・在庫・Pre-flight・emergency kill switchを強制する。
- Guard通過を実行許可へ変換しない。

実装:
- `research_lab/live_pilot_guard.py`
- `research_lab/supabase_live_pilot_guard_repository.py`
- `research_lab/test_live_pilot_guard.py`
- `docs/migrations/2026-10-03_pg026_live_pilot_guard_results.sql`

Guard checks:
- Human GO decision。
- GO decision expiry。
- Purchase Intent validity/expiry。
- provider allowlist。
- current purchase price <= intent max purchase price。
- current total cost <= intent max total cost and approved budget。
- max transactions=1 / completed transactions < 1。
- quantity=1。
- parallel positions disabled / open positions=0。
- duplicate order=false。
- emergency kill switch not engaged。
- inventory available。
- current Pre-flight passed。
- Human final buy required。
- authorization boundary remains closed。

出力:
- `status=live_pilot_guard_passed / live_pilot_guard_blocked`
- `guard_passed=True/False`
- `eligible_for_live_adapter_validation=True/False`
- `live_execution_authorized=False`
- `execution_triggered=False`
- commerce/external/purchase/payment/sale authorization=False。

Supabase:
- table: `public.warashibe_live_pilot_guard_results`
- guard_key unique / append-only。
- RLS enabled、public/anon policyなし。

実DB:
- `pg026-live-proof-20261003`
- approved budget=3,000円 / current total=2,950円。
- guard_passed=true / eligible_for_live_adapter_validation=true。
- live_execution_authorized=false / commerce_authorized=false。
- cleanup済み。

CI:
- contract `84fe10dbb00b0fc0dc312f5bfefa7aa00eace1c0` — #1181 success。
- RED `bbb0acb8622414dfa8beec93395fa6cba55afa19` — #1182 failure。
- implementation `3f95b732da7a97198f500b7f7487552f744a8f63` — #1183 success。
- repository `90cd7f0cdd60fa21ba45fce4a8371ea6c1de586a` — #1184 success。
- migration source `590afe8d33aa79469b68b0ad785bef872caaa737` — #1185 success。

判定:
- bounded live-pilot guard: 完了。
- budget/provider/expiry/duplicate/kill-switch guards: 完了。
- append-only audit persistence: 完了。
- live execution authorization: blocked。
- **PG-026開発エンドポイント: 到達。**

## 26. PG-026 開発エンドポイント

PG-026到達時点で、
`Human GO`
→ `bounded pilot scope`
→ `Purchase Intent`
→ `Live Pilot Guard`
→ `eligible_for_live_adapter_validation`
まで進める。

Guard通過は実購入許可ではない。
次の自然な開発対象はPG-027 Live Commerce Adapter Interfaceであり、
実金銭を動かすPG-028より前にHuman Gateを維持する。


### PG-027 — Live Commerce Adapter Interface 開発エンドポイント到達

目的:
- PG-026 Live Pilot Guard通過後に利用するlive commerce adapterの共通interfaceを定義する。
- prepare / validate / submit / status / cancelの契約を固定する。
- PG-028 Human Gate前では外部ネットワークwriteを一切行わず、submit/status/cancelを必ずblockedにする。

実装:
- `research_lab/live_commerce_adapter.py`
- `research_lab/supabase_live_adapter_validation_repository.py`
- `research_lab/test_live_commerce_adapter.py`
- `docs/migrations/2026-10-03_pg027_live_adapter_validations.sql`

interface:
- `LiveCommerceAdapterInterface.prepare_order()`
- `validate_order()`
- `submit_order()`
- `get_order_status()`
- `cancel_order()`

DisabledLiveCommerceAdapter:
- `adapter_mode=live_interface_disabled`
- prepare_orderはPG-026 Guard / provider / quantity / approved budgetを再検証。
- validate_orderはローカル検証のみ。
- validation pass時:
  - `status=live_adapter_validation_ready`
  - `eligible_for_human_final_buy=True`
  - `order_submission_authorized=False`
- submit/status/cancel:
  - `status=live_adapter_blocked`
  - reason=`human_gate_before_pg028`
  - `network_call_attempted=False`
  - `external_write_attempted=False`
  - `order_created=False`
  - `live_execution_authorized=False`
  - commerce/external/purchase/payment/sale authorization=False。

Supabase:
- table: `public.warashibe_live_adapter_validations`
- validation_key unique / append-only。
- provider/item/validation/validated_atを保持。
- RLS enabled。
- public/anon policyなし。
- server-side専用closed-by-default。

実DB:
- test key: `pg027-live-proof-20261003`
- provider=yahoo_shopping。
- purchase price=2,800円 / total cost=2,950円 / approved budget=3,000円。
- validation_passed=true。
- eligible_for_human_final_buy=true。
- network_call_attempted=false。
- external_write_attempted=false。
- live_execution_authorized=false。
- order_submission_authorized=false。
- commerce_authorized=false。
- cleanup済み。

CI:
- contract `5d9de7de56b141ef08150a7d35799be2266eb148` — #1187 success。
- RED `3a0c4f2730c6e4e94a2dbb300cf62ebd456f5191` — #1188 failure。
- implementation `0b423a88fdaff887465a9ddc316c7c2f332f7b23` — #1189 failure（fixtureにapproved_budget_jpy欠落）。
- fixture repair `bd2d0491cd34b9d7b89c0d652ef92a04e8990b87` — #1190 success。
- repository `35c54c727d909aaa9ce96a6442e6e2af319b782a` — #1191 success。
- migration source `e23cb8924000a5f69a011ab017c3c2312929233c` — #1192 success。

判定:
- common adapter interface: 完了。
- live-shaped prepare/validate: 完了。
- PG-028前submit/status/cancel block: 完了。
- external network/write prohibition: 完了。
- append-only validation audit: 完了。
- live execution authorization: blocked。
- **PG-027開発エンドポイント: 到達。**

## 27. PG-027 開発エンドポイント

PG-027到達時点で、
`Human GO`
→ `Live Pilot Guard`
→ `Live Commerce Adapter prepare/validate`
→ `eligible_for_human_final_buy`
まで進める。

submit_order / get_order_status / cancel_order はPG-028 Human Gate前のため必ずblocked。
次のPG-028は初めて実金銭が動く可能性があるため、ここでHuman Gateを置く。


### PG-028 — Single Purchase Execution 開発エンドポイント到達

目的:
- PG-027 live-adapter validation後に、明示的Human Final Buyを1注文だけ実行可能な契約へ変換する。
- Human Final Buy / expiry / provider / item / quantity / max cost / approved budget / kill switch / live enable / idempotencyを全て強制する。
- 開発runでは実注文を発生させず、fake adapterと合成DB proofのみで実行境界を検証する。

実装:
- `research_lab/human_final_buy.py`
- `research_lab/single_purchase_execution.py`
- `research_lab/supabase_pg028_repositories.py`
- `research_lab/test_single_purchase_execution.py`
- `docs/migrations/2026-10-03_pg028_single_purchase_execution.sql`
- build profileへPG-028 contract testを追加。

Human Final Buy:
- source validationは `live_adapter_validation_ready`。
- decision=`buy / do_not_buy`。
- provider / item / quantity=1を固定。
- validated total costとapproved pilot budgetを再確認。
- max total costを明示。
- confirmed_at / expires_atを保持。
- `execution_authorized_for_single_order=True` はdecision=buyの場合のみ。

Single Purchase Execution:
- explicit `live_execution_enabled=True` が必要。
- emergency kill switch engaged時は必ずblocked。
- Human Final Buy expiry前のみ実行可能。
- provider / item / quantity / total cost一致必須。
- idempotency key必須。
- 同一idempotency key再呼び出しではadapterを再度呼ばず、保存済み結果を返す。
- execution count=1。
- adapter charged amountがHuman Final Buy上限またはapproved budgetを超えた場合は異常扱い。
- live_execution_enabled=False時は `single_purchase_blocked / live_execution_disabled`。
- kill switch時は `single_purchase_blocked / emergency_kill_switch_engaged`。

検証:
- fake live adapterによる成功パス:
  - order reference=`fake-order-028`
  - charged amount=2,950円
  - execution count=1
- 同一idempotency key再実行:
  - `idempotency_reused=True`
  - adapter call countは1のまま。
- disabled / kill-switch pathはadapter callなしでblocked。

Supabase:
- `public.warashibe_human_final_buy_confirmations`
  - confirmation_key unique。
  - decision check buy/do_not_buy。
  - confirmed_at / expires_at。
  - RLS enabled。
  - anon/authenticated grants明示revoke。
- `public.warashibe_single_purchase_executions`
  - idempotency_key unique。
  - confirmation_key unique。
  - Human Final Buyへのforeign key。
  - RLS enabled。
  - anon/authenticated grants明示revoke。
- public/anon/authenticated policyなし。
- server-side専用closed-by-default。

実DB proof:
- `pg028-final-buy-proof-20261003`
- `pg028-idem-proof-20261003`
- synthetic DB proofのみ。
- execution_environment=`synthetic_db_proof`。
- network_call_attempted=false。
- external_write_attempted=false。
- decision=buy / max_total_cost=3,000円。
- insert / join read-back / cleanup成功。
- 最終row count=0。
- **実際の外部注文・決済は行っていない。**

Supabase current security verification:
- current Supabase API security docsを再確認。
- 両PG-028テーブルでRLS enabled。
- anon SELECT/INSERT=false。
- authenticated SELECT/INSERT=false。
- advisorのrls_enabled_no_policyは、明示revoke＋server-side closed-by-default設計では意図したINFO。

CI:
- contract `eb201ccf4d563f1d0064b24c10057c5a1c2a1f4d` — #1194 success。
- RED `e21c3285b9174eb528242958d1133986adc8f596` — #1195 failure。
- execution engine `5d77da52aa5b0cb81a25a64067b20fcfc8cda4d8` — #1196 success。
- Human Final Buy artifact `02224bdf7eaa41388e9742cabd546e4875c47045` — #1197 success。
- Human Final Buy integration test `dbc5d48bd851d45096c4df6b32eed7fdfa6266cd` — #1198 success。
- repositories `5ca31248f7a490126277f8d4957cf7993742824f` — #1199 success。
- migration source `6bb9f65ea19a8040666545f98f085bbf5169eb33` — #1200 success。

判定:
- Human Final Buy artifact: 完了。
- single-order execution contract: 完了。
- kill switch: 完了。
- explicit live enable gate: 完了。
- idempotency / duplicate execution prevention: 完了。
- append-only audit schema: 完了。
- synthetic DB proof: 完了。
- **real marketplace order: 未実行。**
- **PG-028開発エンドポイント: 到達。**

## 28. PG-028 開発エンドポイント

PG-028到達時点で、
`Live Pilot Guard`
→ `Live Commerce Adapter validation`
→ `Human Final Buy`
→ `Single Purchase Execution engine`
→ `idempotent execution audit`
まで実装済み。

ただし今回の開発runでは実注文を送信していない。
実際の外部注文には、具体的な商品・provider live adapter・有効な認証情報・最新Guard/validation・Human Final Buyが別途必要。
次の自然な開発対象はPG-029 Purchase Receipt / Reconciliation。


### PG-029 — Purchase Receipt / Reconciliation 開発エンドポイント到達

目的:
- PG-028 Single Purchase Executionの結果を、実支払額・送料・税・割引・注文状態・決済状態を含むPurchase Receiptへ確定する。
- execution時の想定請求額とprovider側の実請求額を照合し、差異があれば次工程へ進めずHuman Reviewへ戻す。
- 実際に資本拘束された金額を `capital_committed_jpy` としてCommerce Loopへ渡す。

実装:
- `research_lab/purchase_receipt_reconciliation.py`
- `research_lab/supabase_purchase_receipt_repository.py`
- `research_lab/test_purchase_receipt_reconciliation.py`
- `docs/migrations/2026-10-03_pg029_purchase_receipts.sql`
- build profileへPG-029 contract testを追加。

reconciliation:
- source status=`single_purchase_executed`
- quantity=1
- provider order reference一致
- expected chargeとactual total charge比較
- item price + shipping + tax - discount とactual totalのcomponent reconciliation
- payment status / order status確認
- pass時:
  - `status=purchase_receipt_reconciled`
  - `reconciliation_passed=True`
  - `capital_state=awaiting_receipt_or_delivery`
- mismatch時:
  - `status=purchase_receipt_mismatch`
  - `reconciliation_passed=False`
  - `requires_human_review=True`
  - `capital_state=reconciliation_hold`

Supabase:
- table: `public.warashibe_purchase_receipts`
- receipt_key unique。
- idempotency_key unique。
- RLS enabled。
- anon/authenticated grants revoke。
- server-side closed-by-default。

実DB proof:
- `pg029-proof`
- actual_total_charged_jpy=2,950円。
- capital_committed_jpy=2,950円。
- reconciliation_passed=true。
- capital_state=awaiting_receipt_or_delivery。
- insert/read-back/cleanup成功。

CI:
- contract `6709bf45a2aa63d0fda1783d97e3192651be3b4a` — #1202 success。
- RED `4cf3d281bf46504c093d5da28cd80a7fef2563fa` — #1203 failure。
- implementation `ee759e54d1b0af50dbd8a957c54864b4e3002f30` — #1204 success。
- repository `2a5961d5a4e34a2048b9dedfa33cc0978a7440ff` — #1205 success。
- migration source `5c4dc9e6e114da420677c4c13eda5867c2b50d83` — #1206 success。

判定:
- purchase receipt model: 完了。
- charge reconciliation: 完了。
- capital committed handoff: 完了。
- mismatch hold: 完了。
- append-only persistence: 完了。
- **PG-029開発エンドポイント: 到達。**

## 29. PG-029 開発エンドポイント

PG-029到達時点で、
`Single Purchase Execution`
→ `Purchase Receipt / Reconciliation`
→ `actual capital committed`
までCommerce Loopを進められる。

次はPG-030 Receive / Inspection。


### PG-030 — Receive / Inspection 開発エンドポイント到達

目的:
- PG-029で照合済みの購入品について、受領・数量・商品同一性・状態・破損・欠品・真贋疑義・機能確認・返品可能性を記録する。
- 検品結果を `sale_ready / return_required / inspection_hold` の3状態へ分岐し、Sale Planへ進める商品を明確にする。
- Purchase Receiptで確定した `capital_committed_jpy` を `capital_basis_jpy` として在庫へ引き継ぐ。

実装:
- `research_lab/receive_inspection.py`
- `research_lab/supabase_receive_inspection_repository.py`
- `research_lab/test_receive_inspection.py`
- `docs/migrations/2026-10-03_pg030_receive_inspections.sql`
- build profileへPG-030 contract testを追加。

検品:
- source status=`purchase_receipt_reconciled`
- reconciliation_passed=True
- quantity received=1
- identity verified
- condition grade
- listingとの状態一致
- damage / missing parts
- counterfeit suspicion
- functional check
- return window
- 正常時:
  - `disposition=sale_ready`
  - `sale_ready=True`
  - `capital_state=inventory_ready_for_sale`
- 問題あり＋return window open:
  - `disposition=return_required`
  - `return_required=True`
  - `capital_state=return_or_refund_pending`
- 問題あり＋return不可:
  - `disposition=inspection_hold`
  - `requires_human_review=True`
  - `capital_state=inspection_hold`

Supabase:
- table: `public.warashibe_receive_inspections`
- inspection_key unique。
- receipt_key unique。
- disposition check constraint。
- RLS enabled。
- anon/authenticated SELECT/INSERT=false。
- server-side closed-by-default。

実DB proof:
- `pg030-proof`
- disposition=sale_ready。
- sale_ready=true。
- capital_basis_jpy=2,950円。
- capital_state=inventory_ready_for_sale。
- insert/read-back成功。
- cleanup後 test_rows=0。

CI:
- contract `314d64ba763f0413f2250c1ae85196cf1d348b9a` — #1208 success。
- RED `de7d5f3cd35acd702dcf099b421df0afb8824e1c` — #1209 failure。
- implementation `9d3829cab01279f94f20ba8913502d8cec5a2240` — #1210 success。
- repository `01313fcf3ca6c9dbc3768958cdda6297a2626104` — #1211 success。
- migration source `7fa8da04cd646153debaa8887860047b8224b904` — #1212 success。

判定:
- receive model: 完了。
- inspection/disposition: 完了。
- return/hold branching: 完了。
- capital basis handoff: 完了。
- append-only persistence: 完了。
- **PG-030開発エンドポイント: 到達。**

## 30. PG-030 開発エンドポイント

PG-030到達時点で、
`Single Purchase Execution`
→ `Purchase Receipt / Reconciliation`
→ `Receive / Inspection`
→ `inventory_ready_for_sale`
までCommerce Loopを進められる。

次はPG-031 Sale Plan。


### PG-031 — Sale Plan 開発エンドポイント到達

目的:
- PG-030でsale_readyとなった1商品に対して、売価・手数料・送料・純手取り・期待利益・予想売却日数・損切りを一つのSale Planへまとめる。
- Warashibe Loop v2の上位KPIであるCapital Velocityを販売計画へ正式導入する。
- Sale Plan自体はlisting/saleを許可しない。

実装:
- `research_lab/sale_plan.py`
- `research_lab/supabase_sale_plan_repository.py`
- `research_lab/test_sale_plan.py`
- `docs/migrations/2026-10-03_pg031_sale_plans.sql`

主要出力:
- current market price
- recommended listing price
- expected sale price
- estimated marketplace fee
- estimated shipping
- expected net proceeds
- expected profit
- estimated days to sell
- `expected_capital_velocity_jpy_per_day`
- minimum acceptable net proceeds
- minimum sale price for net floor
- stop-loss price / days
- `human_sale_decision_required=True`
- `listing_authorized=False`
- `sale_authorized=False`

代表実証:
- capital basis = 2,950円
- recommended listing = 4,100円
- expected sale = 4,000円
- fee = 400円
- shipping = 210円
- expected net proceeds = 3,390円
- expected profit = 440円
- estimated days = 3
- Capital Velocity = 146.67円/日

Supabase:
- table: `public.warashibe_sale_plans`
- plan_key unique / inspection_key unique
- RLS enabled
- anon/authenticated grants revoke
- closed-by-default
- DB proof insert/read-back/cleanup成功

CI:
- contract `11ad3df9bcd42d3462f679001eccfe48712f909f` — #1214 success。
- RED `80ac3ab75f56bab9ab129e54aa57fc529b06b7e1` — #1215 failure。
- implementation `c7bac5a6bb4b15dd7932f9dcdcf50a5d580bf419` — #1216 success。
- repository `8e9486844a33483be22a1ca473e3c28be47cc022` — #1217 success。
- migration source `6148b9baa3ee1c5c5dc27fed99feed85caa2b5f0` — #1218 success。

判定:
- sale economics plan: 完了。
- Capital Velocity: 完了。
- stop-loss plan: 完了。
- append-only persistence: 完了。
- sale authorization: blocked。
- **PG-031開発エンドポイント: 到達。**

## 31. PG-031 開発エンドポイント

`Receive / Inspection`
→ `Sale Plan`
→ `Human Sale Decision待ち`

まで進められる。
次はPG-032 Human Sale Decision。
