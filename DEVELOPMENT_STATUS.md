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

## 2026-09-28: 単品の選択根拠・損益・失敗リスク・仮想費用の同一評価出力
- `research_lab/one_item_scenario_evaluation.py` を追加。既存の `best_candidate` と仮想取引・現金台帳の検証を再利用し、成功/失敗の資本、純利益、仮定した失敗確率、仮想費用、確率加重の期待純利益を一つのread-only出力にまとめる。候補の新しいランキングや独立した商品DDモジュールとの接続ではない。
- 固定fixture: 初期3,000円、仕入2,400円、売却3,600円、入荷送料100円、発送送料200円、手数料率10%、仮定の成功確率75%。成功時3,540円（+540円、費用660円）、失敗時500円（−2,500円、費用100円）、期待純利益−220円。これは仮定に基づくオフライン結果であり実市場の収益・成約確率を実証しない。
- 実装コミット `2d4095083e977bfab86004eeb24ba1a08e971daa` の同一SHA CI成功 https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36437650128 。結合回帰テスト `fa741f2fc9eed43fd2c847d44aae5cb73e31de5a` の同一SHA CI成功 https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36437802146 。外部実行許可はfalse。
- 次の一件: 実データではなく独立した商品DD項目（根拠・送料・売却可能性・回収価値）の入力契約と不足データ時の保留をオフラインで検証。MAIN/DB/Secrets/外部AI実行/実取引は対象外。

## 2026-09-29: 商品DD入力のfail-closedオフラインゲート
- `research_lab/product_dd_input_gate.py` で既存スコアラーの入力9項目と、価格・売却・手数料・送料・清算価値の根拠参照5項目を検証。欠落、空欄、非有限数はスコアを出さず `hold_missing_or_invalid_evidence`。全項目がある場合のみ既存のスコアラーに委譲し、政策上のブロックと比較可能を区別する。
- `test_real_world_candidate_scoring_design.py` に欠落5パターン、NaN、空根拠、非mapping、許可/ブロックの固定fixture回帰を追加。根拠文字列はfixture上の申告であり、実際の外部資料の検証・市場観測を意味しない。選択結果や現金台帳への本番接続は未実施。
- 実装 `0ce074d7874a2d66f755d7a483037437fac26b33` 同一SHA CI成功 https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36507092801 。回帰テスト `1abd0e41507b478bd29a1d5b58520d3ddff8e8bc` 同一SHA CI成功 https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36507170913 。外部実行許可なし。
- 定期監督はOpenAI安全チェックによる `add_comment_to_issue` 拒否の報告を受け、毎時読み取り専用・タスク本文報告に変更。定期タスクからGitHub/Library書き込みは試行しない。チャット中の変更と定期実行成功を混同しない。
- 次の一件: 商品DDのhold/blocked/比較可能を単品シナリオ評価への入力境界で明示し、hold時に損益予測を出さないことをオフライン結合検証する。

## 2026-09-29: 商品DD保留と単品損益予測の結合ゲート
- `research_lab/dd_gated_one_item_scenario.py` を追加。独立した商品DD入力ゲートが `eligible_for_offline_comparison` の場合のみ既存単品シナリオを評価する。根拠不足・不正値・Policyブロックは `scenario=None` で保留。DDと選択済み候補の仕入価格・売却価格・confidenceの不一致も保留する。外部実行許可はfalse。
- 同一fixtureで成功時3,540円・期待純利益−220円を再現し、根拠欠落、NaN、Policyブロック、候補不一致、候補なしでは予測を生成しない回帰テストを既存のend-to-endテストに追加。実装 `3c6f9a371ceeaacd1c3ae62269be91fa4abe40ff` CI success https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36508043289 。回帰 `554d565fbc4528df18ca103546ae85b83e50763e` CI success https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36508132423 。
- この結合はオフライン固定データの契約検証であり、実市場根拠の真偽、実成約確率、実取引、Gemini/Codex実送信を確認したものではない。次の一件はDDと選択候補の同一性を識別子・根拠参照まで拡張するかを検討し、異なる商品を誤接続しない回帰を追加する。

## 2026-09-29: DDと選択候補の商品ID・根拠参照照合
- `evaluate_dd_gated_scenario` で商品IDと5種の根拠参照（価格、売却、手数料、送料、清算価値）を双方必須とし、値の不一致・欠落・空欄では `hold_decision_mismatch` / `scenario=None` とする。価格・確信度の既存照合も維持。
- 同一ID・根拠の固定fixtureで成功時3,540円、期待純利益−220円を維持。商品ID違い、根拠違い、識別子欠落は予測なし。実装 `7b44bf734ded1d925d0a06d902cff6a419197407` の中間CIは旧fixtureとの不一致で失敗したが、回帰更新後の `c32b56250b35edd4b40dd19134c13cb0cda6c293` は同一SHA CI https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36545470717 completed/success。ローカルresearch runnerは226/226通過。
- 根拠参照はfixtureの文字列一致であり、外部資料の真偽や商品IDの実市場照合を示さない。次は実データの出所・取得時刻・鮮度を含む証拠契約をオフラインで定義・検証する。外部AI、MAIN、DB、Secrets、実取引は未実行。

## 2026-09-29: 商品根拠の出所・取得時刻・鮮度のオフラインゲート
- 既存DD評価を再利用する `evaluate_product_dd_with_provenance` を追加。単品損益予測の入口では、5種の根拠に非空の出所とタイムゾーン付きISO取得時刻を必須とし、明示した評価時刻から7日（設定可能）超、未来日付、不正・欠落なら `hold_missing_or_invalid_evidence` / `scenario=None`。評価時刻がない場合も保留。既存DD単独のスコアラーは変更しない。
- 境界日、有効な固定fixture、期限切れ、未来日付、空出所、不正時刻、不正な許容期間をオフラインで回帰。成功時3,540円、仮定に基づく期待純利益−220円を維持。ローカル研究チェック226/226成功。最終コード・回帰コミット `b922eafe12591377d300a97138748bbc4bd8fb8f` の同一SHA CI https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36546612251 completed/success。
- これは申告された出所文字列と日時の形式・鮮度検査であり、外部資料の存在・真正性や実市場観測を実証しない。次の候補は許可した商品データAPIとドメインに限定し、アクセス制限後の迂回・再試行を模擬環境で拒否する検証。MAIN、DB、Secrets、外部AI、実取引は未実行。

## 2026-09-29: eBay Browse検索の外部アクセス境界（オフライン検証）
- `ebay_browse_transport.py` の検索GETを固定HTTPSホスト `api.ebay.com` と `/buy/browse/v1/item_summary/search` のみに制限し、HTTPリダイレクトを追わない専用handlerを使用。Bearerトークンを別ホスト・別経路へ転送しない。
- モックで許可外ホスト、HTTP、別経路、紛らわしいサブドメイン、リダイレクト、403/429時に再試行なしを検証。ローカルresearch runner 226/226成功。最終コード・テストcommit `252814293d083366b5306dbfca7ddd3da0734d24` 同一SHA CI https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36547286165 completed/success。
- eBay Browse検索の既存読み取り経路のみが対象。他の市場アダプター、プロキシ・ネットワーク全体の強制隔離、実HTTP応答、実商品データ取得は検証していない。外部AI、MAIN、DB、Secrets、実売買は未実行。次は市場データ取得経路全体の棚卸しと、同じ境界を共通化する必要性を評価する。

## 2026-09-29: 市場データ取得経路の棚卸し
- [市場データ取得経路の棚卸し](docs/MARKET_DATA_ACCESS_INVENTORY.md)を作成。research-labのPythonコードで市場向けHTTP実装はeBay Browse検索1経路。eBay結果変換、Real Marketの正規化、sandbox市場候補パイプラインは取得済みレコードを受け取るオフライン処理。GitHub Actions/Gemini HTTPは別用途。
- 棚卸しcommit `473360fad6afcadce93ac1466f2953d7033ce7a0` の同一SHA CI https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36547808305 completed/success。現段階では共通市場HTTP層を追加しない。二つ目の市場プロバイダー実装時に同じ許可先・操作・リダイレクト・制限後停止の契約を適用する。外部パッケージ内部や実環境通信の監査ではない。

## 2026-09-29: eBay出品価格だけのDD評価を保留
- eBay Browseの取得済みlistingは `metadata.asking_price_only=True`。DD入口はこの印を持つ候補を、他の仮定値や根拠文字列が揃っていても `hold_missing_or_invalid_evidence` / `asking_price_only` とし、スコア・単品損益予測を出さない。
- eBay adapterから得た固定listingに仮の売却・費用・確率を加えても保留する回帰と、単品シナリオ `scenario=None` の結合回帰を追加。ローカルresearch runner 226/226成功。最終コード・回帰commit `7da59680429d52973cec59b4aabc54ac6f0ba5b6` 同一SHA CI https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36548358348 completed/success。
- この印を落とす別変換まで保護するものではない。出品価格は成約価格や成約確率の証拠ではない。実市場取引、MAIN、DB、Secrets、外部AIは未実行。次は出品データからDDへ渡す明示的な変換契約を設け、印と根拠不足を保持することをオフラインで検証する。

## 2026-09-29: eBay出品観測からDD部分入力への明示変換
- `research_lab/ebay_listing_dd_bridge.py` を追加。取り込み済み `MarketObservation` のeBay出品で `asking_price_only=True`、JPY、正の有限価格、タイムゾーン付き取得時刻を確認し、商品ID・仕入提示価格・価格根拠と出所/時刻・印だけをDD入力に変換する。売却見込み・成約確率・売却根拠は作らない。
- 固定eBay payload→取り込み→変換→DD保留→単品シナリオなしを既存テストに追加。別ソース、印欠落、USD、時刻のタイムゾーン欠落は変換拒否。ローカルresearch runner 226/226成功。最終コード・回帰commit `24b1915a75377a1e55d94f500a0b5898ced2aefb` の同一SHA CI https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36548890899 completed/success。
- この関数を通らない別変換は対象外。実eBay API通信、成約根拠、MAIN、DB、Secrets、外部AI、実売買は未実施。次はこの部分入力を商品評価へ統合する際、独立した成約根拠を補う条件と、出所を混同しない契約をオフラインで定義する。

## 2026-09-29: eBay取り込み済み候補のDD部分入力バッチ
- `build_dd_input_batch` が正常に取り込まれたeBay観測を1行ずつ既存の部分入力変換に渡す。JPYの2件は商品ID・提示価格・価格根拠・asking-price-only印を保持し、USDは独立して変換拒否。元の不正価格行は取り込み段階で拒否される。どのDD部分入力も売却根拠を補わず、評価は保留。
- ローカルresearch runner226/226通過。最終コード・回帰commit `cb97ae91dfcb08fa992ccad03a3b41e6c7f62c8e` の同一SHA GitHub Actions run https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36549401966 は一覧でcompleted successfullyと表示された。GitHub REST APIは一時的に403で、一覧HTMLから実行番号・SHA・成功表示を照合した。
- DD変換拒否は元の取り込み拒否と別集計。実eBay通信や売却根拠取得、MAIN/DB/Secrets/外部AI/実売買は未実施。次は独立した成約根拠を合流させる前に、商品ID・市場・出所・日時の一致条件を設計する。

## 2026-09-29: 独立成約根拠の照合レビューゲート（オフライン）
- `research_lab/sale_evidence_join_gate.py` を追加。出品記録と独立した成約根拠候補について、商品ID・市場一致、別出所・別証拠参照、タイムゾーン付き取得日時と明示的な評価時刻からの鮮度を検査。不一致・欠落・未来・期限切れなら `hold_evidence_join`。通過時も `reviewable_provenance_pair` のみで、`scenario=None`、`asking_price_only=True`、外部実行許可false。独立データの真正性・成約事実を検証したものではない。
- 実装 `8690c745b2d968948590b50ca6a56dceeae33b79` は同一SHA CI https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36551284180 success。9件の回帰テスト `3078ee1962c9ff71373c02a8387795a970b4f255` は https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36552385327 success。ただしこの時点ではrunner未登録。
- `research_lab/runner.py` に `research_lab.test_sale_evidence_join_gate` を登録した `c53a98c9a5ecec5763291c8347e94daf71f90603` は同一SHA CI https://github.com/mikan2k88-glitch/warashibe-ai/actions/runs/36552496976 completed/success。ログ内で `Ran 9 tests ... OK` を確認。これを本マイルストーンの回帰実行証拠とする。
- 次の一件: 出品・成約根拠の両者がレビュー可能でも、eBay出品の `asking_price_only` 印を自動解除せず、独立根拠の真正性・商品同一性を裏付ける追加審査契約をオフラインで定義する。実市場の成約実績・実通信、MAIN、DB、Secrets、外部AI、実売買は未確認・未実施。

## 2026-09-30: AI自己修復ループの実行境界・同一SHA検証マイルストーン
- research-lab内の通常の低リスクなコード修復判断はAIが行い、Human Gateを要求しない方針に更新。対象は1サイクル最大1件、原則 research_lab/ 配下のPython 1ファイルのみ。MAIN/production、Secrets/認証情報、実DB、実取引・決済、課金、権限拡張、外部AI実行、破壊的操作は自動修復対象外。
- problem_guardrail_candidate.py → problem_guardrail_recurrence.py → problem_repair_candidate.py → problem_repair_ai_decision.py → problem_repair_execution_boundary.py → problem_repair_validation_gate.py の段階ゲートを構築。問題から修復候補を作り、AIが可否判断し、書込み範囲を制限し、書込み後は同一SHAのCIだけで成功判定する。
- problem_repair_validation_gate.py はSHA不一致、CI未完了、未知の結論をfail-closedで停止。CI successのみ repair_validated_success。failure/cancelled/timed_out/action_required は rollback_candidate=True とするが、自動再試行・自動ロールバック・外部実行は許可しない。
- 実行境界までの定常回帰は commit b171fadd304fb3e51a9da51f50168a2bd55c0f6f、同一SHA CI #902 success。exact-SHA検証ゲート実装 d849e7588f9422d88c0359db6d5bf04df12f1997 は CI #903 success、回帰テスト 0a00f8d73f42feedab51e3f815cbcb47b7e8eb12 は CI #904 success、定常CI登録 e444701e8724c85d0f4c58a4d6431c20e9da7a7f は CI #905 success。
- これにより「問題検出 → ガードレール候補 → 再発判定 → 修復候補 → AI修復判断 → 実行境界 → 同一SHA CI検証」までの制御ループをresearch-labで回帰できるマイルストーンに到達。まだ一般目的の自動パッチ生成器、失敗時の自動ロールバック実行、MAIN昇格、実取引・外部サービス操作を有効化したものではない。
- 次の候補は、許可済みの単一ファイル修復に対して「変更前SHA・変更後SHA・対象パス・期待テスト・CI結果」を監査記録として一つに束ね、成功/失敗を再現可能に追跡すること。

## 2026-09-30: AI修復監査記録マイルストーン
- research_lab/problem_repair_audit_record.py を追加し、1件のAI修復について repair_id、変更前SHA、変更後SHA、対象Pythonファイル、期待テスト、exact-SHA CI検証結果を1つの監査記録に束ねる契約を定義。
- 対象は research_lab/ 配下のPython 1ファイルに限定。同一SHAのまま、非終端のCI検証結果、範囲外パス、不正入力は fail-closed で監査記録を作らない。
- 成功修復と失敗修復の両方を監査可能。失敗時は rollback_candidate を記録するが、自動ロールバック、自動再試行、外部実行は引き続き許可しない。
- 実装 commit 295ce7da7bee91514f0c7eaf79ef1971867028dd は CI #907 success。回帰テスト commit ca2901d3a4219b7bdfd998b8e2654017adaa7035 は CI #908 success。定常CI登録 commit 4565909f5ded63d38b550c0edd17fc6d84ad58b4 は CI #909 success。
- これにより「問題検出 → 修復判断 → 単一ファイル実行境界 → exact-SHA CI検証 → 再現可能な監査記録」までを research-lab の定常回帰で追跡できるマイルストーンに到達。
- 次の候補は、監査記録を1サイクル分の repair ledger に集約し、同一 repair_id の重複、複数修復、前後SHAの連鎖不整合を拒否するオフライン台帳ゲートを追加すること。
\n## 2026-09-30: AI修復サイクル台帳マイルストーン\n- research_lab/problem_repair_ledger.py を追加し、1サイクルに受け入れるAI修復を最大1件へ固定する fail-closed 台帳ゲートを実装。\n- 台帳は cycle_id、repair_id、変更前SHA、変更後SHA、対象範囲、検証状態を保持し、同一 repair_id の重複、複数修復、前後SHAが変化しない記録、research-lab外の範囲、非終端の検証結果を拒否する。\n- 既存台帳への追加要求では、重複 repair_id を duplicate_repair_id、前後SHAの連鎖不一致を sha_chain_mismatch として識別した上で、最終的に1サイクル複数修復を許可しない。\n- 実装 commit 859af2dd8fc0fcc2f7ecda179c1ce15166871f8f は CI #911 success。回帰テスト commit 30e267cc3ef684a0b4f7b192b2ff03e3885dcf10 は CI #912 success。定常CI登録 commit 6e84be45f95d58e4f6c5977bd4b1fb67ada10f32 は CI #913 success。\n- これにより「問題検出 → AI修復判断 → 単一ファイル実行境界 → exact-SHA CI検証 → 監査記録 → 1サイクル修復台帳」までを research-lab の定常回帰で追跡できるマイルストーンに到達。\n- 自動ロールバック、自動再試行、MAIN昇格、実取引・決済、実DB、Secrets、外部AI実行、権限拡張はこのマイルストーンに含めず、引き続き自動修復対象外。\n- 次の候補は、連続する複数サイクル間で head_after → 次cycleの head_before が一致することを確認する cross-cycle continuity gate を追加し、履歴の分岐・抜け・巻き戻りを fail-closed で検出すること。\n\n## 2026-09-30: AI修復クロスサイクル連続性マイルストーン\n- research_lab/problem_repair_cross_cycle.py を追加し、連続する修復サイクル間で前cycleの head_after と次cycleの head_before が一致することを必須化。\n- SHA連鎖の不一致は sha_chain_mismatch として fail-closed。重複 cycle_id、重複 repair_id、同一SHAの自己リンク、research-lab外のscope、1cycle複数repair ID、2cycle未満の不十分な履歴も拒否する。\n- このゲートは履歴の分岐・抜け・巻き戻りを検出するためのオフライン契約であり、Git書込み、自動再試行、自動ロールバック、外部実行を行わない。\n- 実装 commit a79ce2090a1be777d0421670a91c61352fdca9bd は CI #915 success。回帰テスト commit ab46bdffd55b09d9d2178f08190d1f71ad2f75e3 は CI #916 success。定常CI登録 commit 9986c1cbbb57b35aa8a9090ab68ddd2335bd2d39 は CI #917 success。\n- これにより「問題検出 → AI修復判断 → 単一ファイル実行境界 → exact-SHA CI検証 → 監査記録 → 1サイクル修復台帳 → 複数サイクルSHA連続性」の制御ループを research-lab の定常回帰で検証できるマイルストーンに到達。\n- 次の候補は、各cycle ledgerとcross-cycle判定をまとめた履歴スナップショットを生成し、履歴全体の先頭SHA・末尾SHA・cycle数・成功/失敗数を固定出力して監査可能にすること。\n\n## 2026-09-30: AI修復履歴スナップショット・マイルストーン\n- research_lab/problem_repair_history_snapshot.py を追加し、cross-cycle continuity を通過した複数cycleのrepair ledgerから、監査用の固定スナップショットを生成する契約を実装。\n- スナップショットは scope、cycle_count、repair_count、success_count、failure_count、head_start、head_end、continuous、各cycleの cycle_id / repair_id / before/after SHA / validation_status を固定出力する。\n- cross-cycle continuity未通過、ledger内record欠落、非終端validationは fail-closed でスナップショットを作らない。Git書込み、自動再試行、自動ロールバック、外部実行は行わない。\n- 実装 commit 852ab53cf19da6aabb3c7202eda8b253cd5e5c10 は CI #919 success。回帰テスト commit 79fe57ec3582acdee0b9cd0c5b635f2eba580fa7 は CI #920 success。定常CI登録 commit 42d469dd66cdeebabe405120268e2101da2b382e は CI #921 success。\n- これにより「問題検出 → AI修復判断 → 単一ファイル実行境界 → exact-SHA CI検証 → 監査記録 → 1サイクル修復台帳 → 複数サイクル連続性 → 履歴全体スナップショット」までを research-lab の定常回帰で監査可能にするマイルストーンに到達。\n- 次の候補は、この履歴スナップショット自体に決定論的なdigestを付与し、同じ履歴から同じdigestが得られること、1フィールド変更でdigestが変わることをオフラインで検証する履歴完全性ゲート。\n