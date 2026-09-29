"""Fail-closed offline bridge: DD evidence must pass before scenario arithmetic."""

from research_lab.product_dd_input_gate import EVIDENCE_FIELDS, evaluate_product_dd_with_provenance
from research_lab.one_item_scenario_evaluation import evaluate_one_item_scenario


def evaluate_dd_gated_scenario(candidate, decision, *, cost_kwargs=None, as_of=None, max_age_days=7):
    """Use an existing one-item decision only when its DD inputs are eligible and match."""
    dd = evaluate_product_dd_with_provenance(candidate, as_of=as_of, max_age_days=max_age_days)
    base = {"dd_status": dd["status"], "dd_reasons": dd["reasons"],
            "scenario": None, "one_item_only": True, "scenario_only": True,
            "external_action_authorized": False}
    if dd["status"] != "eligible_for_offline_comparison":
        return base
    if not isinstance(decision, dict) or not isinstance(decision.get("best_candidate"), dict):
        return dict(base, dd_status="hold_decision_mismatch", dd_reasons=("missing_decision_candidate",))
    selected = decision["best_candidate"]
    pairs = (("purchase_price_jpy", "purchase_price"),
             ("estimated_sale_price_jpy", "expected_sale_price"),
             ("confidence", "confidence"))
    if any(selected.get(right) != candidate[left] for left, right in pairs):
        return dict(base, dd_status="hold_decision_mismatch", dd_reasons=("dd_decision_values_differ",))
    identity_fields = ("item_id",) + EVIDENCE_FIELDS
    if any(not isinstance(candidate.get(field), str)
           or not candidate[field].strip()
           or not isinstance(selected.get(field), str)
           or not selected[field].strip()
           or selected[field] != candidate[field] for field in identity_fields):
        return dict(base, dd_status="hold_decision_mismatch",
                    dd_reasons=("dd_decision_identity_or_evidence_differ",))
    scenario = evaluate_one_item_scenario(decision, cost_kwargs=cost_kwargs)
    return dict(base, scenario=scenario)
