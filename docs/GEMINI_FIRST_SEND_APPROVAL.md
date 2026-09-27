# Gemini初回実送信 — Human Gate審査票（未承認）

この文書は research-lab の審査準備用。作成・CI成功・チェック欄の記入だけでは送信を許可しない。初回送信はSandboxで研究課題1件のみ。

## 現在の実証
- オフライン永続ゲート結合テスト: [run 36287976148](https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36287976148) completed/success（SHA `5fb0e7bfb90819403ab09ea4eb7213ee57d5571a`）。
- オフライン事前審査テスト: [run 36288120655](https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36288120655) completed/success（SHA `c6bc3f76454c48b464e312bbad1915b6e534626b`）。
- 進捗文書反映: [run 36288272852](https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36288272852) completed/success（SHA `a10a4a530eabb47ae2eabd5985192abbab00a5c3`）。
- いずれもGeminiへの実送信を証明しない。

## 実行前に個別確認する項目（未確認）
- [ ] 研究用サービスの認証された非公開入口を確認。公開Webの無認証呼び出しを作らない。
- [ ] 再起動・複数プロセス間でも同じ台帳を使う永続共有ストレージと原子的な一回限り予約を実環境で検証。Renderの一時ファイルに依存しない。
- [ ] 使用モデルID、現在の提供状況と価格、最大入力・出力トークン、費用見積もりと実際の課金上限を確認。設計上の例示上限（1回、入力2000、出力512、見積もりUS$0.10以下）は実際のプロバイダー請求上限を保証しない。
- [ ] 最新HEADと同一SHAの必要なCI成功、対象 `assignment_id` と `source_run_id`、Sandbox研究課題本文、停止・再試行禁止条件を確定。
- [ ] ネットワーク使用、研究用Secret読取、Geminiへの課金対象API送信について、ユーザーの具体的な明示承認を別途取得。
- [ ] 実行後は応答ID、トークン数、結果と同じIDのみを記録し、キー・機密情報を残さない。通信失敗の結果が不明なら自動再送しない。

## 許可範囲
この文書の現時点の状態: **未承認・実送信禁止**。Geminiの応答を受けてもCodex起動、MAIN変更、production、実DB変更、仕入・販売・決済は許可しない。

次のHuman Gateで確認する具体的な依頼: 「上記の実環境証拠と費用上限を提示したうえで、指定した1件のSandbox研究指示をGeminiへ一度だけ送信してよいか」。一般的な『次へ』はこの承認の代わりにしない。

## 2026-09-27 実環境境界の読み取り確認（送信許可ではない）
- ユーザーがRenderの `My Workspace` を確認後、研究用Web Service `warashibe-ai-research-lab` の非秘密メタデータを読み取り。GitHub `research-lab` に接続、commit自動デプロイ、起動コマンド `gunicorn app:app`。デプロイ `dep-das7t2ou01pc73eq90ig` はSHA `58b2e94e2d6c6ea87d9d8a987b86e5a234735cdc` でlive。同一SHAの[CI run 36288459515](https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36288459515) はsuccess。
- IP allow listは `0.0.0.0/0`。これはWebサービスが公開到達可能であることを示すだけで、内部の個別ルートの認証有無は証明しない。Gemini実送信の入口としては未認証・未検証扱いを維持する。
- 不正な数値を拒否するオフラインpreflight修正 `6a05ce577327e1405bedbcec923fcc458ab4a6cf`、同一SHAの[CI run 36288772742](https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36288772742) success。文字列、bool、非有限値、負値等の境界値テストを追加した次のHEAD `19b89c25898b30c374403244f417a0e7c8f565f1` も[CI run 36288873096](https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36288873096) success。
- 次の設計審査: 公開Webに送信エンドポイントを設けず、認証済みの管理実行経路と再起動を跨ぐ共有・原子的予約台帳を具体化し、疑似送信で検証する。Renderの一時SQLiteだけでは共有永続性の証拠にならない。設定・Secret・実DB・課金APIは今回変更しない。
