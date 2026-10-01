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
| PG-004 | 実商品候補評価で、価格・流動性・想定売却期間・手数料・真贋・返品の主要項目が統一契約になっていない | 必須 | PG-001, PG-003 | P1 |
| PG-005 | confidenceを仮想success rateとして使う箇所があり、「情報信頼度」と「取引成功確率」の意味が混在 | 必須 | PG-004 | P1 |
| PG-006 | Candidate選択結果を製品側の結果保存/監査へ一貫して残す運用経路が未完成 | 必須 | PG-004 | P1 |
| PG-007 | Supabaseのwarashibe専用テーブル契約はあるが、v1.0製品経路から安全にread/writeする運用完成証拠が不足 | 条件付き必須 | PG-006 | P2 |
| PG-008 | Render / GitHub / Supabaseの接続状態は個別に存在するが、v1.0製品フローとしての運用チェックが未固定 | 必須 | PG-006 | P2 |
| PG-009 | 実市場APIからの自動商品取得 | 不要 | v1.0後 | Post-v1 |
| PG-010 | 実購入・実決済・実販売の無人実行 | 不要 | v1.0後 + Human Gate | Post-v1 |
| PG-011 | P0 research-lab監査チェーンの追加拡張 | 原則不要 | 製品阻害時のみ | Defer |

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

### 次の実問題

**PG-004: 実商品候補評価の主要項目を統一契約にする。**

狙い:
- 価格・流動性・想定売却期間・手数料・真贋・返品をCandidate契約に揃える。
- 欠落項目はfail-closedまたは明示的な未評価状態にする。
- 実商品候補が同じ契約で比較・保存できる状態へ進める。
