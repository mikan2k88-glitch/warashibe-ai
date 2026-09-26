# Warashibe AI 開発引き継ぎ

更新: 2026-09-27 JST。次回の開発開始時は、この文書と [研究マイルストーン Issue #1](https://github.com/mikan2k88-glitch/warashibe-ai/issues/1) の最新記録を読み、ブランチ・CI・実行ログを再確認する。ここに書く「未確認」は、その後に進展した可能性がある。

## 目標と現在地
- 当面は仮想市場の研究を進める。仕入れ・決済など実世界の実行は別途明示的な承認を要する。
- 目標の一周: 前回研究成果物 → GPTの判断と理由 → Geminiへの実際の指示と応答 → 必要ならCodexの作業結果 → CI → 次回GPTの判断。各段階を「実装」「接続」「実行で観測」に分けて記録する。
- GitHub Actionsの研究実行と223件のチェック成功は確認済み。Geminiへの作業指示の実送信、Codexへの実引き渡し、一周完了は未確認。証拠はIssue #1に残す。
- Company X / Gateway X は現在の作業対象外。

## 確認した実装と実行環境
- `research_lab/runner.py`: イベントとチェック結果から `stage`、`next_theme`、理由を成果物に記録。これだけでGPTが自律的にテーマを判断するわけではない。
- `research_lab/gemini_live_probe.py`: 疎通テストは `GEMINI_API_KEY` を読み、別モデルへのフォールバックがある。同ファイルの `send_assignment_once` はGPT作業指示を検証して1回送る別の関数で、呼び出し側に永続的な一回限りのゲートが必要。定期実行への接続は未確認。
- Renderには `warashibe-ai` (main) と `warashibe-ai-research-lab` (research-lab) の別サービスがある。後者の起動コマンドは `gunicorn app:app`。ユーザーは研究用サービスにGeminiキー、Stripeキー、Supabaseキー、Supabase URLが登録済みと確認した。値を表示・転記しない。
- [研究用GitHub Actionsワークフロー](https://github.com/mikan2k88-glitch/warashibe-ai/blob/research-lab/.github/workflows/research-lab.yml)は `runner.py` を実行する。Renderの環境変数はGitHub Actionsに自動で渡らない。定期スケジュールの経路は別途確認すること。
- 過去のIssue本文には古い状態の記述もある。必ず新しいコメント・最新のコミット・実行成果物で照合する。

## 次の一件
1. 現在の定期スケジュールとGPTタスクが読む成果物、Geminiへ渡す作業指示の生成元を特定する。
2. Render側でキーを使うなら、認証された入口と永続的な重複防止ゲートを先に設計・検証する。公開Web経由の無認証送信を作らない。費用・回数・失敗時停止を固定する。
3. 実際の送信前後の記録には同じ `assignment_id` / `source_run_id`、結果、応答ID（取得できた場合）、トークン数を残す。キーや機密値は残さない。
4. 実送信の成功まで「Gemini接続済み」と呼ばず、Codex・main変更・商取引を自動的に許可しない。既存のmain変更権限コードと以前の方針には不一致があり、Issue #1に記録済み。

## 次回の読み方・更新方法
新しい会話では「warashibe-ai の research-lab ブランチにある `DEVELOPMENT_STATUS.md` と Issue #1 を読み、最新のCI・実行記録を確認して続けて」と伝える。作業後はこの文書の現在地と次の一件を更新し、実行証拠の詳細はIssue #1に追記する。未確認の段階を完了に書き換えない。
