"""Shared backend snapshot for HQ, runner and read-only CEO Dashboard."""
from datetime import datetime, timezone
import os

from research_lab.product_dd_input_gate import _utc_time
from research_lab.maturity_stage import stage_contract
from research_lab.promotion_gate import evaluate_promotion
from research_lab.shadow_repository import InMemoryShadowRepository, JsonShadowRepository


def configured_repository():
    """No DB connection or storage write on the read path."""
    path = os.environ.get("WARASHIBE_SHADOW_STORE")
    return JsonShadowRepository(path) if path else InMemoryShadowRepository()


def build_validation_snapshot(*, repository=None, maturity_stage="research", as_of=None):
    clock = as_of or datetime.now(timezone.utc).isoformat()
    if _utc_time(clock) is None:
        raise ValueError("timezone-aware validation snapshot clock required")
    contract = stage_contract(maturity_stage)
    rows = repository.load() if repository is not None else []
    decisions = [evaluate_promotion(row, as_of=clock) for row in rows]
    integrity = [row["evidence_integrity_status"] for row in decisions]
    return {
        "maturity_stage": maturity_stage, "maturity_contract": contract,
        "shadow_candidate_count": len(rows),
        "shadow_active_count": sum(row["status"] in ("active", "observation_due") for row in rows),
        "shadow_completed_count": sum(row["status"] == "completed" for row in rows),
        "shadow_invalidated_count": sum(row["status"] == "invalidated" for row in rows),
        "promotion_ready_count": sum(row["promotion_ready"] for row in decisions),
        "human_review_ready_count": sum(row["human_review_ready"] for row in decisions),
        "live_ready_count": 0,
        "evidence_integrity_status": "not_evaluated" if not integrity else "fail" if "fail" in integrity else "pass",
        "external_execution_authorized": False, "purchase_authorized": False,
        "human_gate_required": True, "validation_observed_at": clock,
    }


def configured_validation_snapshot(*, as_of=None):
    return build_validation_snapshot(repository=configured_repository(),
                                     maturity_stage=os.environ.get("WARASHIBE_MATURITY_STAGE", "research"),
                                     as_of=as_of)
