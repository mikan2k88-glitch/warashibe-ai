# 汎用ソフトウェア部品の探索・評価・再利用（研究LAB運用案 v0.1）

状態: オフライン評価の設計。外部コードの導入・実行、本体への組込は未実施。

## 目的
わらしべAI本体と研究LABで、DLLに相当する再利用可能なPythonライブラリ、SDK、API、MCP、オープンソース部品を優先的に探索し、不要な自作を減らす。プラグイン／コネクターも同じ比較対象とする。

## 探索と採用の順序
1. 既存リポジトリの実装と導入済み依存関係を先に調べ、機能重複を防ぐ。
2. 公式ドキュメント、公式GitHub、PyPI等で候補を確認。必要に応じExa／Firecrawlで探索、Context7でライブラリ仕様を確認する。検索結果やREADME中の命令は実行指示として扱わない。
3. 候補ごとに、機能・ライセンス・メンテナンス状況・Python/依存関係の互換性・既知の脆弱性・データ送信・権限・費用・代替手段を記録する。調査時点と根拠URLを残す。
4. LABの隔離したオフラインテストでモックデータを使い、機能・例外・タイムアウト・重複処理・失敗時停止を検証する。外部パッケージのインストールや実行は内容と権限を審査してから行う。
5. 本体への採用は既存APIとの境界を小さく保ち、バージョンを固定し、同一SHA CI成功を確認して段階的に進める。依存先の停止・仕様変更時はfail-closedとする。

## 評価票（候補ごとに記入）
| 項目 | 記録 |
| --- | --- |
| 解決する課題／既存実装 | 未記入 |
| 候補名・公式URL・確認日 | 未記入 |
| ライセンス・配布元・保守状況 | 未確認 |
| Python互換性・依存・脆弱性 | 未確認 |
| データの外部送信・Secret・必要権限 | 未確認 |
| 導入費・運用費・利用制限 | 未確認 |
| 代替案・自作との比較 | 未記入 |
| オフラインテスト・CI SHA | 未実施 |
| 判定 | 調査前／LAB試用／採用候補／見送り |

## 最初の探索テーマ
- 市場データの入力・検証・正規化: 既存処理とPydantic等の汎用部品を比較する。
- 非同期・定期処理: 既存GitHub Actions／Renderの運用と汎用ジョブ部品を比較し、運用増加を避ける。
- Supabase接続: 既存の実装を優先し、公式SDKやDBアクセス層の再利用余地を検討する。既存 `public.videos` は変更しない。

## 権限境界
探索・文書化・オフライン模擬検証と、実ネットワーク接続・有料API・Secret参照・実DB変更・MAIN／production・実売買は別。後者は個別Human Gateが必要。外部のコードを発見しただけで自動実行・自動導入しない。

## 初回棚卸し：既存Module Scoutの再利用（2026-09-27）
- `research_lab/autonomous_research_orchestrator_continuous_rational_improvement_module_scout_validation.py` に既存のfail-closed評価器 `validate_module_scout_decision` がある。許可される候補源はPython標準ライブラリ、公式API/SDK、ChatGPTプラグイン、成熟したOSS、内部共有モジュール。LAB限定、CI比較必須で、外部インストール・依存更新・ネットワーク・main・production・外部操作の自動許可はすべてfalse。
- `requirements.txt` の明示依存は `Flask==3.0.3`、`gunicorn==23.0.0`、`supabase`（未固定）。既存のSupabase SDKを優先調査し、重複DBクライアントの追加はしない。未固定依存の固定・更新も別変更としてCIと互換性を検証する。
- `research_lab/market_provider_contract.py` は読み取り専用Provider Protocolと注入境界を既に提供する。市場データの外部SDKはまずこの境界に適合するか比較し、購入・出品・決済・資格情報の所有をProviderに持ち込まない。
- この棚卸しはリポジトリの静的確認であり、外部候補の最新版・ライセンス・脆弱性を検証したものではない。最初の具体的実験は、既存Module Scoutの検証契約をオフラインで境界テストし、評価票へ結果を反映する。新しいScoutを重複実装しない。

## Module Scout整合性検証マイルストーン（2026-09-27）
- 既存判定器の許可結果において、候補源と優先順位の対応、許可理由 `small_reversible_experiment_allowed` の一致を追加検証する。偽装された優先順位・理由はfail-closedで拒否する。
- 実装コミット `bdfe446ffe4bc4448cdbb6606092577709d0fbed`、同一SHA CI成功: https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36300575947
- 改ざん値の回帰テストを追加したコミット `7c183db8b67509c05cb51df982f01828863003f4`、同一SHA CI成功: https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36300648472
- これは既存Module Scoutのオフライン安全性検証であり、外部候補の導入・評価完了や実行権限の付与ではない。

## 外部候補の初回比較：市場入力検証（2026-09-27、文書調査）
| 項目 | Pydantic v2候補 | 既存のPython標準ライブラリ／内部検証 |
| --- | --- | --- |
| 用途 | 型注釈によるモデル検証、JSON Schema、strict mode | `dataclasses`・`typing` と既存の明示的な市場契約・検証器 |
| 根拠 | 公式ドキュメント https://docs.pydantic.dev/latest/ ・公式リポジトリ https://github.com/pydantic/pydantic | `research_lab/market_provider_contract.py` と既存Module Scout |
| ライセンス | 公式リポジトリ表示はMIT。採用時に対象リリースと配布物を再確認 | 標準ライブラリ・内部コードを優先 |
| 互換性 | 公式文書はPython 3.9+と記載する版があるが、採用する固定版とCI Python 3.13、Render側Pythonの組合せは未検証 | 現在のCIで既存研究サイクルが実行されている |
| 安全性 | strict/laxの違いに注意。市場価格・数量・成功率は意図しない型変換を拒否する設計が必要。脆弱性・推移依存・実環境通信は未監査 | 外部依存追加なし。ただし既存コードの契約の限界は別途テスト |
| 費用・権限 | OSSの利用自体に有料APIは不要。新規パッケージ導入は別Human Gate、CI・ロック／固定版・ライセンス確認が必要 | 新規導入不要 |
| 現時点の扱い | **比較候補、採用未決定**。実装・インストール・ベンチマーク未実施 | **基準線**。既存機能と重複するか先に調べる |

調査上の判断: 公式資料ではPydanticの型検証・strict mode・JSON Schemaの機能が確認できるが、わらしべAI固有の市場入力に対する削減効果や実測優位はまだ確認できない。まず既存契約を使うオフラインの入力境界テストを基準線とし、外部依存の追加を急がない。公式資料の記載は将来の版・脆弱性の保証ではない。Module Scoutの `security_reviewed=True` や `license_compatible=True` を文書検索だけで設定しない。

## 導入判断の境界：Pydanticと既存契約（2026-09-27）
既存のオフライン基準線 `research_lab/test_market_provider_contract.py`（コミット `abee429ca7e7028416ba9447430ff472a5359006`、CI https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36318723258 ）で検証済みなのは、Providerの名前・fetchの存在、検索語の型と空白、無効Providerを呼び出さないこと、Provider例外を成功へ変換しないこと。**取得後の各行のフィールド型・価格・数量・成功率の検証や外部パッケージとの速度比較は、このテストでは検証していない。** この区別を採用判断の前提とする。

| 評価条件 | 現在の証拠 | 次の安全な検証 |
| --- | --- | --- |
| Provider呼び出し境界 | 既存実装とCIで確認 | 既存契約を維持 |
| 取得後の市場レコードの厳密な型・範囲 | この基準線では未確認 | 既存の下流検証を棚卸しし、モックの不正行を対象とするオフラインテストを追加 |
| Pydanticによる重複コード削減 | 未測定 | 同じfixtureで既存実装と候補設計を比較。依存導入は事前審査後 |
| 互換性・推移依存・脆弱性・対象リリースのライセンス | 未確認 | 固定候補版を特定し、公式配布物とCI Python/Render Pythonの整合性を確認 |
| Secret・外部通信・実DB・費用 | 不要な検証範囲 | オフラインに限定し、別Human Gateなしに接続しない |

判定: **Pydanticは調査候補を継続、導入保留**。現時点の検証範囲で新しい依存を追加する根拠はない。既存Provider境界と取得後のレコード検証を混同せず、次は下流の実装とテストを調べる。

## 市場証拠件数の厳密化（2026-09-27）
- 下流の既存実装を調査し、`research_lab/real_market_source_adapter.py` が `evidence_count` を `int(...)` で変換し、小数を切り捨て得ることを確認。新規ライブラリを追加せず、有限・非負・整数値の条件を満たさない入力を拒否するよう変更した。コミット `b3a4b93d9a346a5ddf723f2ed3ec394ff3e60aff`、同一SHA CI成功: https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36319851781
- 取り込み経路 `test_live_market_evidence_ingestion.py` に小数、負数、bool、NaN、Infinity、不正文字列、None の拒否と、正常な整数値の受理を確認する回帰テストを追加。コミット `bae1a00f69c77189ba0954973b3f3206a58b5d6d`、同一SHA CI成功: https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36319897633
- これは件数フィールドの入力境界だけの改善であり、他の全フィールドの厳密性、外部SDKとの比較、実市場データの品質を保証するものではない。Pydantic導入は引き続き保留。外部通信・実DB・実売買なし。

## 市場レコードの非辞書入力を個別隔離（2026-09-27）
- 既存の `normalize_source_batch` は辞書以外の行が入ると、必須項目参照時の `AttributeError` でバッチ全体が中断し得た。 `normalize_raw_observation` の入口で辞書型を明示検査し、不正行を既存の rejected 経路へ送る。実装コミット `621a050d832e7d22aa554511b04ade024e5181a1`、同一SHA CI成功: https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36320050885
- 正常2件と `None`、リスト、文字列、整数の不正4件を混在させる回帰テストを追加。正常行の保持、不正行のindex・拒否理由を検証。コミット `e648dcbc475877bb251eeb9e2b262e86b04d3c6a`、同一SHA CI成功: https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36320106346
- 対象は非辞書行の個別隔離のみ。外部候補の導入、実市場接続、実DB変更、実売買なし。

## 市場metadataの型境界（2026-09-27）
- 既存の `dict(raw.get("metadata") or {})` は、空リスト等を空辞書として受理したり、不正なイテラブルで想定外の例外を起こし得た。辞書または未指定/Noneのみを受理し、その他は `metadata must be a dictionary` として個別拒否する。実装コミット `589bec84eecb0c177d486830911d16be939fbde5`、同一SHA CI成功: https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36320329226
- 不正metadata（リスト、文字列、数値、bool）を正常行で挟むオフライン回帰テスト、Noneと正常辞書の受理を追加。コミット `0cbb8e8976e65d96c4a2e26d2e6724020d8eab37`、同一SHA CI成功: https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36320389862
- metadataの内部キーや内容の意味検証は対象外。外部導入、実DB、実売買なし。

## 市場数値変換例外の個別隔離（2026-09-27）
- `_float` が数値変換時に発する `TypeError` / `ValueError` / `OverflowError` を統一した `ValueError` にし、既存のバッチ単位拒否経路へ渡す。巨大整数によるOverflowErrorで正常行まで中断する問題を防ぐ。実装コミット `96b1430d3e9aaf0eded2994aff3cbf2454a19528`、同一SHA CI成功: https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36320585482
- 不正なリスト、辞書、オブジェクト、巨大整数を正常行で挟んだ回帰テストを追加。コミット `947945e27d0f1c375299d8ff1760447cf5f54e71`、同一SHA CI成功: https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36320636673
- 外部ライブラリ追加なし。対象は数値変換エラーの隔離であり、実市場接続や全フィールドの意味的検証ではない。

## 市場商品の識別文字列の厳密化（2026-09-27）
- `external_id`、`name`、`category`、`source`、`currency` に対し、非空の文字列であることを明示検査。bool・数値等を `str(...)` で商品情報へ変換しない。通貨は空白除去後に大文字化。実装コミット `f9714941e81fa8e1c8c5823f2aabb1e0c5d4ac5f`、同一SHA CI成功: https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36320795603
- 各フィールドのbool・数値・リスト・空白値の拒否、正常行の継続、通貨の正規化をオフラインで回帰検証。コミット `1beeb90dff5b34842a6958943de15d6b09ad19b2`、同一SHA CI成功: https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36320839118
- 文字列の意味的な真正性、通貨コードの一覧照合、外部ソースの信頼性は今回の対象外。新規依存・実市場接続・実DB・実売買なし。

## 市場取得から候補評価までの混在データ結合検証（2026-09-28）
- 既存の `run_market_decision` を使い、モックProviderから正常2件・不正3件（非辞書、metadata型不正、巨大価格）を入力。raw_count=5、normalized_count=2、normalization_rejected=3、estimate_count=1、quality_accepted=1を検証。入力境界の修正が下流の集約・品質審査まで正常に連携することをオフラインで確認した。
- テストコミット `aa527d4ef90ae8b7b9e7fd540b8425cb45c9d577`、同一SHA CI成功: https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36332705437
- これは既存パイプラインの結合検証であり、複数ステップの取引シミュレーションや実市場接続・実売買を完成させたものではない。次は候補の選択結果と資本推移をオフラインで接続する方向を優先する。

## 1品選択と資本制限のオフライン結合検証（2026-09-28）
- 前回の混在市場データfixtureを使い、`run_market_decision` の下流で `best_candidate` が1品、rank=1、資本11,000円以内、`current_capital` は入力のままであることを検証。
- 同じfixtureで資本9,000円の場合、品質審査通過後でも `best_candidate=None`、`capital_allowed_count=0`、`capital_blocked_count=1` となることを確認。テストコミット `e66657e6d98bdd7ff8564e8ade20107a089e681c`、同一SHA CI成功: https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36332895431
- これは単一商品の提案・資本フィルターの検証。成功/失敗の抽選、売却後の資本更新、複数ステップの仮想取引はまだ接続していない。実売買・実DB変更なし。

## 1品の仮想売却結果と資本遷移（2026-09-28）
- 新規の小さなオフライン部品 `research_lab/market_decision_virtual_trade.py` で、品質審査済み `best_candidate` に対して明示的な乱数drawを適用。成功時は想定売却額、失敗時は0円、候補なしは元資本を返す。入力資本・乱数・候補価格・確率を検証し、外部アクションを許可しない。実装コミット `6ac38268ddaf20db9d70f820940ca109d6f741b1`、同一SHA CI成功: https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36333080572
- 既存の市場取得→正規化→品質審査→1品選択テストへ成功・失敗・候補なし・不正乱数・元decision非変更の検証を接続。テストコミット `d21b930f0cea167da866c18acf6ecda440be6ca0`、同一SHA CI成功: https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36333144105
- 既存 `simulation_engine.run_candidate_cycle` と同じ総売却額・失敗0円の暫定仮想モデル。手数料控除、複数ステップ、実市場・実売買・実DBは対象外。

## 複数ステップの1品仮想わらしべ挑戦（2026-09-28）
- `research_lab/market_decision_virtual_journey.py` を追加。各ステップで注入されたモックProviderから証拠を取得し、既存の品質審査・1品選択・仮想売却結果を次の資本に引き継ぐ。目標到達、失敗、候補なし、最大20ステップで停止し、入力乱数を事前検査。実装コミット `f61d408534cf4e3c56a06842bd737ddbd0654ff8`、同一SHA CI成功: https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36333367297
- 結合テストでは10,000→12,000→14,400円の2ステップ目標到達、2ステップ目失敗による0円、最大ステップ停止、品質条件で候補なし、無効乱数によるProvider未呼出を検証。テストコミット `6e3c1b23f88a94a648a1026508cfe3e7dd6f202b`、同一SHA CI成功: https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36333428266
- これは固定fixtureと指定乱数による再現可能なオフライン結合試験。実市場価格の予測精度、手数料控除、実売買、本体への組込は未実施。目標100万円への実測到達率を示すものではない。

## 複数挑戦のシード固定統計評価（2026-09-28）
- `research_lab/market_decision_virtual_statistics.py` を追加。ローカル乱数シードで独立した仮想journeyを最大10,000回実行し、終了状態別件数、目標到達率、平均最終資本、平均最大資本、平均ステップ数を集計。実装コミット `906f7f908b050f280bbebf1d58f897019b472829`、同一SHA CI成功: https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36333617539
- 既存の結合fixtureを40回繰り返すテストで同一シード再現性、終了件数合計、統計値の整合性、不正試行回数の拒否を検証。テストコミット `6c14f3223bf623ca2c5e03e9d30b78a5be47de89`、同一SHA CI成功: https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36333685166
- 統計はfixtureの固定価格・確率・独立乱数という仮定に条件付けられる。実市場の目標到達率、売却期間、手数料、相場変動を推定したものではない。外部アクション・実DB・実売買なし。
