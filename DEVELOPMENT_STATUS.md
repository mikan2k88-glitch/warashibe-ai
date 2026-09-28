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

## 2026-09-27: Gemini一回限り送信のオフライン安全検証
- 永続SQLiteゲートと疑似Gemini応答の結合テストを追加。重複・別runからの再送・不確実な通信失敗後の再送・台帳消失を拒否する。commit `5fb0e7bfb90819403ab09ea4eb7213ee57d5571a`、同一SHA CI success: https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36287976148
- 費用・回数・トークン上限とHuman Gate等をfail-closedで確認するオフラインpreflightを追加。commit `c6bc3f76454c48b464e312bbad1915b6e534626b`、同一SHA CI success: https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36288120655
- preflightが合格してもAPI呼出し・ネットワーク・Secret読取・Codex・main・商取引の実行許可はすべてfalse。費用上限は設計上の1試行上限であり、プロバイダー実請求の確認ではない。永続共有ストレージへの本番接続、認証された入口、実際の承認とGemini実送信は未確認。
- GPT定期研究はCI完了まで可能な範囲で再照会し、実行時間上限に達したら次の毎時実行で自動再開する運用に変更。CI未成功の新規コード変更は禁止。
- 次の一件: CIでこの文書更新の同一SHA成功を確認し、Issue #1と既存Library引き継ぎへ実証・未検証を反映する。外部送信には別途具体的なHuman Gateが必要。

## 2026-09-27: Gemini初回送信Human Gate審査準備マイルストーン
- `docs/GEMINI_FIRST_SEND_APPROVAL.md` に初回Sandbox研究指示1件の審査票を作成。commit `fa3ef1310319618f38bc2e890df6d665e589cc0a`、同一SHA CI completed/success: https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36288381746
- 審査票は未承認。実行環境の認証入口、永続共有台帳、モデルID・料金・請求上限、個別のネットワーク/Secret/Human Gate承認は未検証。オフラインCIは実送信の証拠ではない。
- 次の一件: 実環境の非秘密メタデータと実行境界を読み取りで確認し、審査票の未確認事項を証拠で埋める。ユーザーの具体的な承認が得られるまではGemini実送信を禁止し、MAIN・実DB・決済等も対象外とする。

## 2026-09-27: Gemini実行境界の証拠整理マイルストーン
- ユーザー確認済みRender `My Workspace` の研究用サービスを読み取り。research-lab連携・自動デプロイ・最新デプロイliveを確認。IP許可 `0.0.0.0/0` は公開到達性を示すが、個別の認証入口は未検証。Issue #1: https://github.com/mikan2k88-glitch/warashibe-ai/issues/1#issuecomment-5851975999
- preflight数値型・有限性のfail-closed修正 `6a05ce577327e1405bedbcec923fcc458ab4a6cf` のCI success: https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36288772742 。境界値テスト追加HEAD `19b89c25898b30c374403244f417a0e7c8f565f1` の同一SHA CI success: https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36288873096
- 審査票 `docs/GEMINI_FIRST_SEND_APPROVAL.md` に非秘密の実環境証拠・残課題を追記。commit `0a2ed13e739ca8d75211e3454a011c6c5793305c`、同一SHA CI completed/success: https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36288975551
- 次の一件: 公開WebにGemini送信口を追加せず、認証済み管理実行経路と永続共有・原子的な予約台帳の構成を設計し、オフライン疑似送信で検証する。実環境への設定変更、Secret取得、Gemini課金API送信、MAIN・実DB・決済は未承認・未実行。

## 2026-09-28: 費用込み仮想Campaignの固定fixture回帰マイルストーン
- 費用モデルは明示的な `cost_kwargs` を指定したオフライン研究のみで有効。1品の仕入れ2,400円、初期資本3,000円、仮想売却額3,600円、入荷送料100円、発送送料200円、販売手数料率10%の成功fixtureで、未使用現金500円、費用660円、最終純資本3,540円、初期資本との差+540円を検証した。実市場価格・実利益を示すものではない。
- 単品の `apply_virtual_trade_costs` と `run_virtual_campaign` の同一fixtureで純資本・費用が一致し、外部実行許可はfalse。コミット `81af6d1e909c0478de5a277cc0f4c399f4cbf4c7`、同一SHA CI成功: https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36434553937
- 失敗後に未使用現金500円が残るケースは同じ挑戦の `salvaged` とし、新しい3,000円の挑戦に数えない。費用なしの従来モデルは3,600円、`total_costs=0` を維持。不正な費用設定を拒否する回帰テストを追加。コミット `fc9adc2f688b26d00a87a629a5e176f45e68dc7f`、同一SHA CI成功: https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36436898622
- 独立した商品DDモジュールとの接続、実際の商品データ、実市場手数料、実取引は未検証。次の一件は商品選択根拠と同じfixtureの期待利益・失敗リスク・仮想費用を一つのオフライン評価出力に整理すること。MAIN、DB、Secrets、外部AIの実行は変更しない。
