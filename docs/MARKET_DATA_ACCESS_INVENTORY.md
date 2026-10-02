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
