"""Warashibe AI core mode boundary.

This module introduces a stable core boundary between the existing simulation
engine and the future real-world engine. Real-world mode is intentionally
proposal-only: it may normalize and score candidates, but it cannot purchase,
list, pay, refund, or modify production state.
"""

CORE_MODE_VERSION = "0.1"

MODE_SIMULATION = "simulation"
MODE_REAL_WORLD = "real_world"
SUPPORTED_MODES = (MODE_SIMULATION, MODE_REAL_WORLD)

REAL_WORLD_START_CAPITAL_MIN_JPY = 2500
REAL_WORLD_START_CAPITAL_TARGET_JPY = 3000
REAL_WORLD_START_CAPITAL_MAX_JPY = 3500

REAL_WORLD_FLOW = (
    "market_discovery",
    "candidate_normalization",
    "policy_filter",
    "capital_filter",
    "candidate_scoring",
    "route_evaluation",
    "human_gate",
    "bounded_execution",
    "ledger_update",
)


def normalize_mode(mode):
    if mode is None:
        return MODE_SIMULATION
    if not isinstance(mode, str):
        return None
    normalized = mode.strip().lower()
    if normalized in SUPPORTED_MODES:
        return normalized
    return None


def build_core_mode_snapshot(mode=MODE_SIMULATION):
    normalized = normalize_mode(mode)
    if normalized is None:
        return {
            "valid": False,
            "mode": None,
            "errors": ("unsupported_mode",),
            "execution_authorized": False,
        }

    if normalized == MODE_SIMULATION:
        return {
            "valid": True,
            "version": CORE_MODE_VERSION,
            "mode": MODE_SIMULATION,
            "engine": "simulation_engine",
            "uses_existing_start_capital": True,
            "real_world_start_capital_jpy": None,
            "human_gate_required": False,
            "network_execution_authorized": False,
            "commerce_authorized": False,
            "production_change_authorized": False,
            "execution_authorized": True,
        }

    return {
        "valid": True,
        "version": CORE_MODE_VERSION,
        "mode": MODE_REAL_WORLD,
        "engine": "real_world_engine",
        "uses_existing_start_capital": False,
        "real_world_start_capital_jpy": {
            "min": REAL_WORLD_START_CAPITAL_MIN_JPY,
            "target": REAL_WORLD_START_CAPITAL_TARGET_JPY,
            "max": REAL_WORLD_START_CAPITAL_MAX_JPY,
        },
        "one_item_only": True,
        "flow": REAL_WORLD_FLOW,
        "human_gate_required": True,
        "network_execution_authorized": False,
        "purchase_authorized": False,
        "listing_authorized": False,
        "payment_authorized": False,
        "refund_authorized": False,
        "secret_change_authorized": False,
        "production_change_authorized": False,
        "main_branch_change_authorized": False,
        "commerce_authorized": False,
        "execution_authorized": False,
    }


def validate_real_world_candidate_for_core(candidate):
    """Fail-closed boundary check before a candidate can enter real-world flow."""
    if not isinstance(candidate, dict):
        return {
            "valid": False,
            "errors": ("candidate_not_mapping",),
            "execution_authorized": False,
        }

    required = (
        "item_id",
        "provider",
        "purchase_price_jpy",
        "estimated_sale_price_jpy",
        "estimated_fees_jpy",
        "estimated_shipping_jpy",
        "estimated_days_to_sell",
        "liquidation_value_jpy",
        "confidence",
    )
    errors = [f"missing_{field}" for field in required if field not in candidate]

    total_cost = None
    if not errors:
        values = (
            candidate["purchase_price_jpy"],
            candidate["estimated_fees_jpy"],
            candidate["estimated_shipping_jpy"],
        )
        if not all(isinstance(v, int) and not isinstance(v, bool) and v >= 0 for v in values):
            errors.append("invalid_cost_field")
        else:
            total_cost = sum(values)
            if not REAL_WORLD_START_CAPITAL_MIN_JPY <= total_cost <= REAL_WORLD_START_CAPITAL_MAX_JPY:
                errors.append("outside_initial_capital_band")

    return {
        "valid": not errors,
        "errors": tuple(errors),
        "total_cost_jpy": total_cost,
        "human_gate_required": True,
        "execution_authorized": False,
        "commerce_authorized": False,
    }
