# Warashibe AI — 開発仕様・運用の正本（初版）

更新日: 2026-09-27 JST  
適用範囲: `research-lab` の研究開発。既存コード・Issue #1・CIの実行証拠を置き換えない。

## 目的と実装状態の表現
- 仮想市場で、極小資本から100万円を目指す研究を行う。各時点では資本全額を使って1品のみ選択し、スピードを重視する。
- 人間が最終判断者。仕入れ・販売・決済など実世界の行為は、別途明示的な承認が必要。
- 「設計済み」「実装済み」「CI成功」「外部サービスへ実送信して応答を観測」は区別する。推測で完了扱いにしない。

## 開発運用
- チャット中はGPTが通常の開発を進める。離席中は有効な定期タスクが安全な研究を最大1件ずつ進める。作業開始時は最新HEAD、同一SHAの該当CI、runnerのstage/next_theme、Human Gateを確認する。
- Actions一覧で結果が見つからなければ、実行ID直接取得やSHA照合で再確認する。HEADと実行結果のSHAが異なる、失敗、未完了、取得不能なら次の変更を重ねない。
- 変更対象は原則 `research-lab` のみ。MAIN、production、Secrets、実DB書込・DDL、実取引・決済は自動変更しない。Human Gateの承認を推定しない。
- 研究成果の詳細証拠は [Issue #1](https://github.com/mikan2k88-glitch/warashibe-ai/issues/1)、現在地と次の一件は [DEVELOPMENT_STATUS.md](../DEVELOPMENT_STATUS.md) に記録する。

## サービス設定台帳（秘密値は記録しない）
| サービス | ユーザーから確認した設定 | 技術的な検証状態 |
| --- | --- | --- |
| Gemini API | 課金設定済み。Render環境変数 `GEMINI_API_KEY` にキー登録済み | 実通信・応答の成功は未確認 |
| Render | 研究用サービス `warashibe-ai-research-lab` を利用 | GitHub ActionsへRenderの環境変数が自動転送されるわけではない |
| Supabase | 研究用Render環境に関連設定が登録済みとの申告 | 実DB変更は本仕様では許可しない |

キーの値、トークン、認証情報は文書・ログ・Issue・チャットへ転載しない。環境変数の登録申告と、実行環境からの取得成功・API疎通成功は別々に検証する。

## Geminiの初回利用条件
- まずSandboxで、小さな研究課題を1件だけ送信し、GPTが構造化された応答を検証する。
- 既存の `research_lab/gemini_live_probe.py`、`gemini_assignment_send_gate.py`、`sandbox_gemini_live_activation_boundary.py` の契約を確認する。送信前に同一SHAのCI成功、認証された実行入口、永続的な重複送信防止、費用・回数上限、ネットワーク・Secret参照・Human Gateの承認を確認する。
- APIの実呼出しは承認とゲート消費が揃うまで行わない。Geminiの応答だけでCodex、MAIN変更、商取引を自動許可しない。
- 記録は `assignment_id`、`source_run_id`、実行結果、取得可能な応答ID・トークン数のみとし、秘密値を除外する。

## 文書の役割
- このファイル: 継続的な仕様・運用方針の正本。
- `DEVELOPMENT_STATUS.md` とIssue #1: 最新の進捗・証拠・未解決事項。
- GPTライブラリの既存「Warashibe AI 開発引き継ぎ.md」: 会話をまたぐ要約。正本へのリンクと差分を保持し、秘密値を保存しない。
- 仕様変更時はコードと実行証拠を照合し、事実・ユーザー申告・未検証事項を分けて更新する。
