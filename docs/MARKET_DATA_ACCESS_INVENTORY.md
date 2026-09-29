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
