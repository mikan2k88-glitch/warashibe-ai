from __future__ import annotations

from .evidence_pack import build_real_read_evidence_pack


def record_evidence_pack(
    run_result: dict,
    observations: list[dict],
    *,
    mode: str,
    run_repository=None,
    thresholds: dict | None = None,
) -> dict:
    pack = build_real_read_evidence_pack(
        run_result,
        observations,
        mode=mode,
        thresholds=thresholds,
    )
    persisted = False
    if run_repository is not None:
        run_repository.append(pack["run_record"])
        persisted = True

    return {
        **pack,
        "run_record_persisted": persisted,
        "research_repository_write": persisted,
        "commerce_external_writes": False,
        "live_execution_allowed": False,
    }
