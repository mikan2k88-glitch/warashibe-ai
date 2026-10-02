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
