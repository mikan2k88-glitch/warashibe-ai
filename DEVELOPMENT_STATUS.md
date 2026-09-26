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

## 2026-09-27: Codex不在時の暫定LAB開発ループ（検証済み）
- GPTが research-lab に限定して小規模な変更を反映し、GitHub Actionsが実行される経路を実証した。Gemini/Codexへの実送信は行っていない。
- Sandbox preflight は設計上の実行許可が false のまま。隔離された実行環境の稼働を意味しない。
- `1c0f10c9a893646fd5f065a8c8ff84fe59e1b2bc`: Sandbox preflight と通常Research LAB CIの両方が成功。
  - https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36264867095
  - https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36264867117
- `7a3000e55db7ecc2160295d233e3d10d99daa99b`: Codex fallback gate と通常Research LAB CIの両方が成功。
  - https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36264941738
  - https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36264941692
- `affb882b5c9c30349b9462dc47940674daddb079`: 通常Research LAB CIが成功。checkoutをトリガー時の `github.sha` に固定し、runの表示SHAと実際のテスト対象の食い違いを防ぐ。
  - https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36265194740
- ChatGPTの定期監視「わらしべLAB CI自動判定」は最新HEADの同一SHAの必要なCIを確認する。ライブラリ引継ぎ資料の更新も別の定期タスクで設定済み。ただし自動タスクの設定は、実際のライブラリ更新成功の証拠とは区別する。
- MAINへの昇格、実DB書き込み、実取引、外部AIの実呼び出しはこのマイルストーンに含まれない。

## 次の実装候補
- 既存の仮想市場・市場証拠・成約結果の閉ループから、1件のオフライン再現可能な評価ケースを選び、商品選択の根拠と期待利益・失敗リスク・手数料を同じ出力で比較できるか検証する。既存モジュールを優先的に再利用し、同時点の全資本で1品のみの方針を維持する。
- 研究の検証はLABのみ。実市場API・Gemini/Codex・MAIN・実決済は自動起動しない。

## 次の一件
1. 現在の定期スケジュールとGPTタスクが読む成果物、Geminiへ渡す作業指示の生成元を特定する。
2. Render側でキーを使うなら、認証された入口と永続的な重複防止ゲートを先に設計・検証する。公開Web経由の無認証送信を作らない。費用・回数・失敗時停止を固定する。
3. 実際の送信前後の記録には同じ `assignment_id` / `source_run_id`、結果、応答ID（取得できた場合）、トークン数を残す。キーや機密値は残さない。
4. 実送信の成功まで「Gemini接続済み」と呼ばず、Codex・main変更・商取引を自動的に許可しない。既存のmain変更権限コードと以前の方針には不一致があり、Issue #1に記録済み。

## 次回の読み方・更新方法
新しい会話では「warashibe-ai の research-lab ブランチにある `DEVELOPMENT_STATUS.md` と Issue #1 を読み、最新のCI・実行記録を確認して続けて」と伝える。作業後はこの文書の現在地と次の一件を更新し、実行証拠の詳細はIssue #1に追記する。未確認の段階を完了に書き換えない。
