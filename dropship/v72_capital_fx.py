"""JPY capital constraint for a USD-denominated one-item research decision.

An FX observation is required; no exchange rate is silently assumed.
The module is intentionally read-only and cannot authorize purchases.
"""
from __future__ import annotations
from decimal import Decimal, InvalidOperation

def _positive(value):
    try:
        result = Decimal(str(value))
        return result if result.is_finite() and result > 0 else None
    except (ValueError, TypeError, InvalidOperation):
        return None

def assess_funding_jpy(*, available_jpy, usd_jpy_rate=None, rate_source=None,
                       rate_observed_at=None, item_usd=None, freight_usd=None,
                       reserve_usd=None):
    amount = _positive(available_jpy)
    rate = _positive(usd_jpy_rate)
    fields = {"available_jpy": amount, "usd_jpy_rate": rate,
              "item_usd": _positive(item_usd), "freight_usd": _positive(freight_usd)}
    missing = [key for key, value in fields.items() if value is None]
    if not rate_source or not rate_observed_at:
        missing.append("verified_fx_source_timestamp")
    # Reserve can be zero, but only with a documented explicit value.
    try:
        reserve = Decimal(str(reserve_usd))
        if not reserve.is_finite() or reserve < 0:
            reserve = None
    except (InvalidOperation, ValueError, TypeError):
        reserve = None
    if reserve is None:
        missing.append("refund_reserve_usd")
    output = {"version": "7.2", "status": "blocked_incomplete_evidence",
              "unknown_fields": missing, "required_jpy": None, "capital_sufficient": None,
              "one_item_only": True, "human_gate_ready": False,
              "live_execution_allowed": False}
    if missing:
        return output
    # This omits actual card settlement and conversion charges unless separately
    # included in the verified reserve/cost basis; this is not a live approval.
    requirement = (fields["item_usd"] + fields["freight_usd"] + reserve) * rate
    output.update({"status": "research_estimate_only",
                   "required_jpy": float(requirement),
                   "capital_sufficient": amount >= requirement,
                   "fx_source": str(rate_source), "fx_observed_at": str(rate_observed_at)})
    return output
