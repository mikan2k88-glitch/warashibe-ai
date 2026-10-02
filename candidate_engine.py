# Warashibe AI v1.2
# Candidate Engine

from demand_engine import get_demand
from value_engine import get_value_transformation
from research_lab.initial_physical_operation_policy import evaluate_initial_physical_fit

CANDIDATE_VERSION = "1.4"


def create_candidate(
    name,
    purchase_price,
    expected_sale_price,
    source,
    category="unknown",
    confidence=0.0,
    success_probability=None,
    metadata=None,
    liquidity_score=None,
    estimated_days_to_sell=None,
    estimated_fees=None,
    authenticity_status="unassessed",
    return_risk="unassessed",
    package_size_class=None,
    weight_grams=None,
    shipping_cost_jpy=None,
    fragility_score=None,
    storage_score=None,
    domestic_shipping=None,
):
    if metadata is None:
        metadata = {}

    expected_profit = expected_sale_price - purchase_price
    expected_profit_rate = expected_profit / purchase_price if purchase_price > 0 else 0

    asset = {
        "name": name,
        "value": expected_sale_price,
        "category": category,
    }

    physical_input = {
        "package_size_class": package_size_class,
        "weight_grams": weight_grams,
        "shipping_cost_jpy": shipping_cost_jpy,
        "fragility_score": fragility_score,
        "storage_score": storage_score,
        "domestic_shipping": domestic_shipping,
    }
    physical_policy = evaluate_initial_physical_fit(physical_input)

    evaluation = {
        "purchase_price": purchase_price,
        "expected_sale_price": expected_sale_price,
        "liquidity_score": liquidity_score,
        "estimated_days_to_sell": estimated_days_to_sell,
        "estimated_fees": estimated_fees,
        "authenticity_status": authenticity_status,
        "return_risk": return_risk,
        "physical": {
            **physical_input,
            "policy": physical_policy,
        },
    }

    return {
        "candidate_version": CANDIDATE_VERSION,
        "name": name,
        "category": category,
        "source": source,
        "purchase_price": purchase_price,
        "expected_sale_price": expected_sale_price,
        "expected_profit": expected_profit,
        "expected_profit_rate": expected_profit_rate,
        "confidence": confidence,
        "success_probability": success_probability,
        "demand": get_demand(asset),
        "value_transformation": get_value_transformation(asset),
        "evaluation": evaluation,
        "metadata": metadata,
    }
