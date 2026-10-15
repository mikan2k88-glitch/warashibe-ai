"""v7.4 combined preflight research review. No commerce authority."""
from flask import Blueprint, jsonify, request
from .v610_single_candidate import evaluate_one
from .v72_capital_fx import assess_funding_jpy

v74_bp=Blueprint("dropship_v74",__name__,url_prefix="/dropship/v7.4")

@v74_bp.get("/endpoint")
def endpoint():
    return jsonify({"version":"7.4","status":"research_preflight_implemented",
                    "operational_acceptance":"pending_verified_fee_return_and_shadow",
                    "human_gate_ready":False,"live_execution_allowed":False})

@v74_bp.post("/review")
def review():
    payload=request.get_json(silent=True)
    if not isinstance(payload,dict) or not isinstance(payload.get("candidate"),dict):
        return jsonify({"error":"invalid_candidate","live_execution_allowed":False}),400
    policy=payload.get("return_policy")
    funding=payload.get("funding")
    if (policy is not None and not isinstance(policy,dict)) or (funding is not None and not isinstance(funding,dict)):
        return jsonify({"error":"invalid_evidence","live_execution_allowed":False}),400
    economics=evaluate_one(payload["candidate"],return_policy=policy)
    if funding is None:
        capital={"status":"blocked_incomplete_evidence",
                 "unknown_fields":["verified_funding_evidence"],"capital_sufficient":None}
    else:
        allowed={"available_jpy","usd_jpy_rate","rate_source","rate_observed_at",
                 "item_usd","freight_usd","reserve_usd"}
        capital=assess_funding_jpy(available_jpy=funding.get("available_jpy"),
                                  **{k:v for k,v in funding.items() if k in allowed and k!="available_jpy"})
    blockers=list(economics["unknown_fields"])
    blockers.extend(capital["unknown_fields"])
    if capital.get("capital_sufficient") is False:
        blockers.append("insufficient_capital")
    if economics["profit_usd"] is not None and economics["profit_usd"] <= 0:
        blockers.append("nonpositive_expected_profit")
    return jsonify({
        "version":"7.4","readiness":"blocked" if blockers else "research_evidence_complete",
        "blocking_reasons":sorted(set(blockers)),
        "economics":economics,"funding":capital,
        "one_item_only":True,"human_gate_required":True,
        "human_gate_ready":False,"live_execution_allowed":False})
