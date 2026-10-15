"""v6.9 conservative, evidence-gated eBay fee/returns estimation.

Never infer seller, category, tax, or return rates. Values are USD and
simulation-only; the resulting evidence cannot authorize real commerce.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation

FEE_SOURCE = "https://www.ebay.com/help/selling/fees-credits-invoices/fee-tables?id=4822"

def _number(value):
    try:
        number = Decimal(str(value))
        if not number.is_finite() or number < 0:
            return None
        return number
    except (InvalidOperation, TypeError, ValueError):
        return None

def _unknown(reason):
    return {"status": "unknown", "reason": reason}

def estimate_v69_costs(candidate: dict, *, return_policy: dict | None = None) -> dict:
    """All assumptions must be explicit and supported by operator evidence."""
    price = _number(candidate.get("sale_total_usd"))
    rate = _number(candidate.get("verified_final_value_fee_rate"))
    category = candidate.get("verified_ebay_category_id")
    fee_version = candidate.get("fee_schedule_verified_at")
    verified_seller = candidate.get("seller_fee_tier_verified") is True
    extras_verified = candidate.get("all_additional_fees_verified") is True
    if (price is None or rate is None or rate > 1 or not category
            or not fee_version or not verified_seller or not extras_verified):
        fee = _unknown("category_seller_tier_total_and_all_fee_evidence_required")
    else:
        fixed = Decimal("0.30") if price <= Decimal("10") else Decimal("0.40")
        # Additional international, currency, tax, ads and regulatory costs
        # must be covered by explicitly verified all_additional_fees_verified.
        variable = price * rate
        fee = {"status": "known", "amount_usd": float(variable + fixed),
               "final_value_fee_rate": float(rate),
               "per_order_fee_usd": float(fixed),
               "source": FEE_SOURCE, "category_id": str(category),
               "fee_schedule_verified_at": str(fee_version),
               "evidence_kind": "operator_verified_estimate"}

    policy = return_policy or {}
    observed_rate = _number(candidate.get("historical_return_probability"))
    nonrecoverable = _number(candidate.get("verified_nonrecoverable_return_cost_usd"))
    if (policy.get("status") != "confirmed"
            or not policy.get("return_policy_id")
            or observed_rate is None or observed_rate > 1 or nonrecoverable is None
            or candidate.get("return_loss_model_verified") is not True):
        return_cost = _unknown("confirmed_policy_observed_rate_and_loss_model_required")
    else:
        return_cost = {"status": "known",
                       "amount_usd": float(observed_rate * nonrecoverable),
                       "model": "observed_probability_times_verified_loss",
                       "evidence_kind": "model_estimate"}

    reserve_rate = _number(candidate.get("verified_refund_reserve_rate"))
    reserve_basis = _number(candidate.get("refund_reserve_basis_usd"))
    if (reserve_rate is None or reserve_rate > 1 or reserve_basis is None
            or candidate.get("reserve_policy_verified") is not True):
        reserve = _unknown("documented_reserve_rate_and_basis_required")
    else:
        reserve = {"status": "known", "amount_usd": float(reserve_rate * reserve_basis),
                   "evidence_kind": "documented_reserve_model"}

    return {"version": "6.9", "platform_fee": fee,
            "expected_return_cost": return_cost, "refund_reserve": reserve,
            "complete": all(x["status"] == "known" for x in (fee, return_cost, reserve)),
            "human_gate_required": True, "live_execution_allowed": False}
