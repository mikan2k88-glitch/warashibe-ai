# 市場データ取得経路の棚卸し（2026-09-29）

対象: `research-lab` のPythonコード。コード上の経路とオフライン検証結果を記す。実HTTP通信や外部サービスの設定を確認した記録ではない。

| 経路 | 入力・通信 | 現在の境界 |
| --- | --- | --- |
| `research_lab/ebay_browse_transport.py` | eBay Browse検索GET。唯一の市場向けHTTP実装 | `https://api.ebay.com/buy/browse/v1/item_summary/search` に固定。別ホスト・別パス・HTTPを拒否し、リダイレクトを追わない。403/429時の再試行はない。 |
| `research_lab/ebay_browse_adapter.py` | 取得済みeBay JSON | 通信を行わず、検索結果を市場観測レコードへ変換。 |
| `research_lab/real_market_source_adapter.py` | 呼び出し側が渡す辞書 | 通信を行わず、個々のレコードを正規化・検証。 |
| `research_lab/sandbox_market_data_adapter_design.py` と `sandbox_market_candidate_pipeline.py` | fixtureまたは取得済みレコード | 通信を行わず、候補を評価してHuman Gateで停止。 |
| `research_lab/github_actions_bridge.py` と `gemini_live_probe.py` | GitHub ActionsとGeminiのHTTP経路 | 市場データ取得ではない。権限と稼働条件は別途審査する。 |

確認方法: `research_lab` のPythonファイルでHTTPクライアントのimport・呼び出し、および市場データのprovider/fetch経路を検索し、各アダプターの入力を読んだ。外部パッケージ内部、リポジトリ外の実行、実デプロイ環境の通信は対象外。

判断: 現在は市場HTTP経路が一つなので、共有HTTP抽象化は追加しない。将来二つ目の市場プロバイダーを実装する際に、許可ホスト・操作・リダイレクト禁止・制限後停止を同じ契約で検証する。現状のeBay用ガードを、別プロバイダーやネットワーク全体に効くものとして扱わない。


## 2026-10-02 追記：国内市場アクセス調査と初期物理運用条件

初期実運用の前提:
- 対象地域: 東京。
- 初期段階は小型荷物を優先する。
- 小型・軽量・壊れにくい・保管しやすい・国内配送の商品を優先し、大型商品は初期候補から除外する。
- 物理制約は `research_lab/initial_physical_operation_policy.py` でfail-closed評価する。

国内市場アクセス分類:

| 市場 | 公式取得経路 | PG-011での扱い |
| --- | --- | --- |
| 楽天市場 | 楽天Web Serviceの商品検索API。App ID / Access Keyで商品情報を取得可能。フリマ/C2C/オークション掲載は対象外。 | `official_read_only_api`。国内の新品価格・商品発見・相場基準候補。 |
| Yahoo!ショッピング | 商品検索(v3)。キーワード、JAN、カテゴリ、ブランド、ストア、中古/新品等で検索可能。 | `official_read_only_api`。国内の商品発見・価格比較候補。 |
| eBay Browse | 既存read-only Browse GET。 | `comparison_market`。海外/比較市場として維持。 |
| メルカリ | PG-011時点で、わらしべAIが自動取得に採用する公式read-only経路を未確定。 | `research_only_until_official_path_confirmed`。無理なスクレイピングは行わない。 |
| Yahoo!オークション | PG-011時点で、わらしべAIが自動取得に採用する公式read-only経路を未確定。 | `research_only_until_official_path_confirmed`。公式経路確認後に再評価。 |

確認した公式資料:
- 楽天市場 商品検索API: https://webservice.rakuten.co.jp/documentation/ichiba-item-search
- 楽天Web Service API一覧: https://webservice.rakuten.co.jp/documentation
- Yahoo!ショッピング 商品検索(v3): https://developer.yahoo.co.jp/webapi/shopping/v3/itemsearch.html
- Yahoo!ショッピング API一覧: https://developer.yahoo.co.jp/webapi/shopping/

PG-011では市場への購入・出品・決済操作を追加しない。国内市場APIの実HTTP connector実装は次の独立PGで行い、まずアクセス可否・データ契約・物理運用Policyを固定する。


## 2026-10-02 追記：PG-012 Yahoo!ショッピング read-only connector 実装

PG-012では、国内公式read-only市場の最初の実装対象として Yahoo!ショッピング 商品検索(v3) を採用した。

実装:
- `research_lab/yahoo_shopping_ingestion_bridge.py`
- 許可先:
  - scheme: `https`
  - host: `shopping.yahooapis.jp`
  - path: `/ShoppingWebService/V3/itemSearch`
  - method: `GET`
- query / results / condition(new|used) を明示的に組み立てる。
- redirectを拒否する。
- 注文、決済、出品、account mutationのAPIは実装しない。
- `YAHOO_SHOPPING_APP_ID` は環境変数からのみ取得し、未設定時はfail-closed。
- Client IDをMarketObservation / Candidate /ログ用recordへ含めない。

データ経路:
`Yahoo! Shopping itemSearch JSON`
→ `yahoo_search_to_records()`
→ `live_market_evidence_ingestion.ingest_records()`
→ `MarketObservation`
→ `real_market_adapter.observation_to_candidate()`
→ `Candidate evaluation.physical.policy`

Yahoo!商品検索結果では配送サイズ・重量が常に保証されないため、PG-012では未知の物理情報を推測しない。
`package_size_class / weight_grams / shipping_cost_jpy / fragility_score / storage_score / domestic_shipping`
が未取得の場合はPG-011の `insufficient_data` としてfail-closedし、商品を自動購入可能へ昇格させない。

実証:
- RED: `3f18d25e0799110d3e13c37527955951d1855b4e`
  - CI #1095 failure
  - connector未実装を再現。
- repair: `d20844d311aceadbf9ddb86fc3452ae4350bedb4`
  - Yahoo read-only connectorを追加。
  - CI #1096 success。
- safety regression: `be63828e6c30dd5b3a70850b4a7c49056fdaf7ae`
  - GET/HTTPS/固定host/固定path、redirect拒否、資格情報不足fail-closedを固定。
  - CI #1097 success。

公式仕様確認:
- Yahoo!ショッピング 商品検索(v3): https://developer.yahoo.co.jp/webapi/shopping/v3/itemsearch.html
- リクエストURL: https://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch
- 必須資格情報: appid (Client ID)


## 2026-10-02 追記：PG-013 楽天Product Search＋国内JAN比較

PG-013では、第2の国内公式read-only providerとして楽天Product Searchを追加し、
Yahoo!ショッピングとの同一商品照合をJANコードで行う。

楽天公式仕様:
- Rakuten Product Search API:
  `https://openapi.rakuten.co.jp/ichibaproduct/api/Product/Search/20250801`
- `productCode` はJANコードとして定義される。
- App IDとAccess Keyが必要。
- Access KeyはHTTP headerでも送信可能。
- `formatVersion=2` を使用し、flat JSON itemsを受け取る。

実装:
- `research_lab/rakuten_product_ingestion_bridge.py`
- `research_lab/domestic_market_comparison.py`
- Yahoo側は `janCode` を canonical metadata `gtin` へ流す。

安全境界:
- Rakuten connectorはGET/HTTPS/固定host/固定pathのみ。
- Access Keyはquery stringへ含めずHTTP headerへ送る。
- redirect拒否。
- credential不足はfail-closed。
- 購入、注文、決済、出品、account mutationなし。
- 同一商品判定は既存 `market_identity_resolution` を利用。
- validated GTIN/JANが一致しない候補は `identity_mismatch` として比較しない。
- fuzzy/AI推測による商品同一化は行わない。

データ経路:
`Yahoo janCode`
→ `metadata.gtin`

`Rakuten productCode(JAN)`
→ `metadata.gtin`

両方を `market_identity_resolution.identity_key()` で照合し、
同一identityが確定した場合だけasking-priceを比較する。

実証:
- RED: `5cf6c024eafc86e23226dbb9218697a5e0df51d6`
  - CI #1100 failure。
- Yahoo JAN bridge: `dbe21b262acbc25a66e7f8a621fe8e462c7366fe`
  - CI #1101 failure（楽天/比較モジュール未実装を継続確認）。
- Rakuten connector: `4605428ef0c5db7265c7b32e0ec1cc1a5f37174f`
  - CI #1102 failure（比較モジュール未実装を確認）。
- domestic comparison: `e248c9ebc0799e5b387a00e11df5a900ca36c3e1`
  - CI #1103 success。
- safety regression: `fea68449f9ed7ba115366a7f937c13a41cb769db`
  - CI #1104 success。
