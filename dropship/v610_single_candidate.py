"""v6.10 single-candidate research economics. Never authorizes commerce."""
from __future__ import annotations
from decimal import Decimal, InvalidOperation
from .v69_cost_model import estimate_v69_costs

def decimal_nonnegative(value):
    try:
        d = Decimal(str(value))
        return d if d.is_finite() and d >= 0 else None
    except (InvalidOperation, ValueError, TypeError):
        return None

def evaluate_one(candidate: dict, *, return_policy=None, capital_usd=None) -> dict:
    evidence = estimate_v69_costs(candidate, return_policy=return_policy)
    required = {
        "sale_total_usd": decimal_nonnegative(candidate.get("sale_total_usd")),
        "supplier_cost_usd": decimal_nonnegative(candidate.get("supplier_cost_usd")),
        "supplier_shipping_usd": decimal_nonnegative(candidate.get("supplier_shipping_usd")),
        "other_verified_costs_usd": decimal_nonnegative(candidate.get("other_verified_costs_usd")),
    }
    missing = [k for k,v in required.items() if v is None]
    missing += [k for k in ("platform_fee", "expected_return_cost", "refund_reserve")
                if evidence[k]["status"] != "known"]
    if capital_usd is not None and decimal_nonnegative(capital_usd) is None:
        missing.append("valid_capital_usd")
    result = {
        "version": "6.10", "evaluation": "blocked_incomplete_evidence",
        "unknown_fields": missing, "cost_evidence": evidence,
        "profit_usd": None, "capital_sufficient": None,
        "one_item_only": True, "human_gate_ready": False,
        "human_gate_required": True, "live_execution_allowed": False,
    }
    if missing:
        return result
    fee = decimal_nonnegative(evidence["platform_fee"]["amount_usd"])
    ret = decimal_nonnegative(evidence["expected_return_cost"]["amount_usd"])
    reserve = decimal_nonnegative(evidence["refund_reserve"]["amount_usd"])
    if any(v is None for v in (fee,ret,reserve)):
        result["unknown_fields"] = ["invalid_model_output"]
        return result
    total_cost = required["supplier_cost_usd"] + required["supplier_shipping_usd"] + required["other_verified_costs_usd"] + fee + ret + reserve
    minimum_capital = required["supplier_cost_usd"] + required["supplier_shipping_usd"] + reserve
    profit = required["sale_total_usd"] - total_cost
    sufficient = (decimal_nonnegative(capital_usd) >= minimum_capital) if capital_usd is not None else None
    result.update({
        "evaluation": "research_estimate_only",
        "profit_usd": float(profit),
        "total_cost_usd": float(total_cost),
        "minimum_capital_usd": float(minimum_capital),
        "capital_sufficient": sufficient,
        "human_gate_ready": False,
    })
    return result
