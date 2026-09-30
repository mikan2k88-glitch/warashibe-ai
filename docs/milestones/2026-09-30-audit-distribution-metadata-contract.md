# 2026-09-30: 監査成果物の配布メタデータ契約マイルストーン

## 目的
固定JSON `audit package` を成果物として保存・配布するときに、成果物名・生成時刻・対象SHA・package digest・artifact識別子を固定契約で結び付け、後から同じ成果物を一意に照合できる状態にする。

## 実装
- `research_lab/problem_repair_audit_distribution_metadata.py` を追加。
- metadata schema version `1.0` と metadata type `warashibe-ai-public-repair-audit-distribution` を固定。
- `artifact_name` は `public-repair-audit-{target_sha}.json` に固定し、対象SHAとの不一致を拒否。
- `generated_at` は UTC の秒精度RFC3339相当 `YYYY-MM-DDTHH:MM:SSZ` に固定。
- `target_sha`、`package_schema_version`、`package_digest_algorithm`、`package_digest` をpackageの検証済み結果から束ねる。
- `artifact_id` は metadata の固定フィールドをcanonical JSON化してSHA-256を計算し、同じ入力から同じ識別子を生成。
- 検証時は未知/欠落フィールド、不正時刻、不正artifact名、対象SHA不一致、package digest不一致、artifact id不一致をfail-closed。
- 外部アップロード、Git書込み、Secret取得、再試行、ロールバック、実取引は行わない。

## TDD / 回帰
- 初回CI #973 は、artifact名fixtureが1文字多い不備により8テスト中5件が失敗。実装側ではなくテストfixtureの命名契約が原因だった。
- ログで `invalid_artifact_name` を確認し、fixtureを `public-repair-audit-{40hex}.json` に修正。
- 修正後のCI #974 は success。
- #974では既存の公開監査summary、summary digest、audit package、JSON roundtripに加えて、新規distribution metadata testも成功。

## 検証結果
- 実装 commit: `64a81af27f78f4e27ec05fe8482767580b8a9e89`
- CI登録 commit: `a6d478b96dacd67fd1372c730a880dc1088c40e9`
- fixture修正 commit: `27b14be6be1d4912bc9edcdd694f176c4e0df771`
- 最終検証CI: GitHub Actions Research Lab **#974: success**。
- 新規 distribution metadata test: **8 tests / OK**。

## 到達点
監査証明は、

`final attestation → public read-only summary → summary digest → fixed audit package → JSON transport → re-verify → distribution metadata`

まで一貫して照合可能になった。

## 次の候補
配布メタデータを実際のartifact保存処理へ接続する前に、**package JSON本体とdistribution metadataを1つの配布bundleとしてcanonical化し、bundle digestまで検証する**。実際の外部ストレージへのアップロードは行わず、まずオフラインの保存・復元・改変検出だけを完成させる。
