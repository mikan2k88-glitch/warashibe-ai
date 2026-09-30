# Public Repair Audit Package Schema

Schema version: `1.0`

## Purpose

This is the fixed, single-object, read-only distribution format for the public repair audit result.
The package is informational only. It authorizes no Git write, external runtime action, retry, rollback, payment, or real-market operation.

## Exact top-level fields

The package MUST contain exactly these fields and no others:

- `package_schema_version`: string, exactly `1.0`
- `package_type`: string, exactly `warashibe-ai-public-repair-audit`
- `target_sha`: non-empty string identifying the verified repair target
- `summary_digest_algorithm`: string, exactly `sha256`
- `summary_digest`: lowercase hexadecimal SHA-256 digest of the canonical public summary
- `package_digest_algorithm`: string, exactly `sha256`
- `summary`: object defined by the fixed public summary field set below
- `package_digest`: lowercase hexadecimal SHA-256 digest of the canonical package payload excluding `package_digest`

Unknown or missing top-level fields MUST fail closed.

## Exact public summary fields

`summary` MUST contain exactly these fields and no others:

- `schema_version`: string, exactly `1.0`
- `scope`: string, exactly `research-lab`
- `target_sha`: non-empty string; MUST equal the package `target_sha`
- `verification_status`: string, exactly `verified`
- `integrity_status`: string, exactly `verified`
- `attestation_digest_algorithm`: string, exactly `sha256`
- `attestation_digest`: lowercase hexadecimal SHA-256 digest
- `read_only`: boolean, exactly `true`
- `contains_secrets`: boolean, exactly `false`
- `contains_internal_execution_details`: boolean, exactly `false`

Unknown or missing summary fields MUST fail closed.

## Digest rules

1. The public summary is canonicalized as UTF-8 JSON with sorted keys, compact separators, `ensure_ascii=false`, and `allow_nan=false`.
2. `summary_digest` is SHA-256 of that canonical summary JSON.
3. The package digest payload contains all top-level package fields except `package_digest`.
4. The package digest payload is canonicalized with the same JSON rules.
5. `package_digest` is SHA-256 of that canonical package payload.
6. Verification recomputes both digests and rejects any mismatch.

## Security boundary

A valid package proves only that the supplied public audit information is internally consistent with its recorded digests and target SHA. It does not authorize execution and does not prove that a real-world transaction occurred.

Any malformed, incomplete, extended, unverified, or non-read-only package MUST be rejected rather than repaired implicitly.
