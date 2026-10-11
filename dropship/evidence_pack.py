from __future__ import annotations

from .run_record import build_research_run_record
from .shadow_gate import assess_shadow_gate
from .shadow_metrics import build_shadow_metrics


def build_real_read_evidence_pack(
    run_result: dict,
    observations: list[dict],
    *,
    mode: str,
    thresholds: dict | None = None,
) -> dict:
    record = build_research_run_record(run_result, mode=mode)
    metrics = build_shadow_metrics(observations)
    product_gates = []
    for product in metrics["products"]:
        product_gates.append({
            "product_key": product["product_key"],
            "gate": assess_shadow_gate(product, thresholds),
            "metrics": product,
        })
    passed_products = [
        row["product_key"] for row in product_gates if row["gate"]["passed"]
    ]
    return {
        "status": "evidence_pack_ready",
        "run_record": record,
        "shadow_metrics": metrics,
        "product_gates": product_gates,
        "shadow_gate_passed_products": passed_products,
        "promotion_review_candidates": passed_products,
        "commerce_external_writes": False,
        "live_execution_allowed": False,
    }
