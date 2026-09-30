# 2026-09-30: 公開監査パッケージ JSON ラウンドトリップ・マイルストーン

## 目的
公開用 `audit package` を JSON として受け渡しても、受け手側で同一の検証結果を再現できる状態にする。

## 実装
- `research_lab/problem_repair_public_audit_roundtrip.py` を追加。
- `serialize_public_repair_audit_package()` は、既に検証済みの package のみを決定論的 JSON にシリアライズする。
- `deserialize_public_repair_audit_package()` は JSON を read-only で復元し、JSON不正・配列などの非object入力を fail-closed で拒否する。
- `verify_serialized_public_repair_audit_package()` は復元後に既存の `verify_public_repair_audit_package()` を再実行し、受け渡し後も target SHA、summary digest、package digest、固定schemaを検証する。
- シリアライズは `sort_keys=True`、固定 separators、UTF-8、NaN禁止として決定論的に固定。
- Git書込み、外部実行、自動再試行、自動ロールバック、Secrets取得、実取引は行わない。

## TDD / 回帰
- まずラウンドトリップ契約テストを追加し、CIで1件の意図的な失敗を確認。
- 初回CI #968 では、改変されたsummaryについて実装が先に `summary_digest_mismatch` を返す仕様と、テストの `target_sha_mismatch` 期待が不一致となった。
- その差分を修正し、digest-first のfail-closed検証契約にテストを合わせた。
- 修正後のテストでは以下を確認。
  - 正常な serialize → deserialize → verify が成功する。
  - JSONシリアライズ結果が決定論的である。
  - 非object JSONを拒否する。
  - 不正JSONを拒否する。
  - 未知フィールドを拒否する。
  - 受け渡し後のsummary改変をdigest不一致として検出する。
  - すべての拒否経路で外部実行・再試行・ロールバック権限がfalse。

## 検証結果
- 最終HEAD: `ae6c36292e0c94a16e8b70201abc920d2642ba6c`
- `research-lab` HEAD はこのSHAと完全一致。
- GitHub Actions Research Lab **#969: success**。
- `test_problem_repair_public_audit_roundtrip` は **6 tests / OK**。
- 同一CIで、既存の公開監査サマリー、公開digest、audit packageの回帰もすべてsuccess。

## 到達点
これで監査証明は、

`final attestation → public read-only summary → summary digest → fixed audit package → JSON transport → deserialize → re-verify`

まで一貫して検証可能になった。

## 次の候補
固定JSON packageを実際の成果物として保存・配布する際の、**package artifactの命名・生成時刻・対象SHA・package digestを含む配布メタデータ契約**を追加し、同じ成果物を後から一意に照合できる状態にする。
