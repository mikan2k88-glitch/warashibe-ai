"""v7.3 interim read-only research endpoint. No credentials or commerce writes."""
from __future__ import annotations
from flask import Blueprint, jsonify, request
from .v611_evidence_mapping import assess_observed_candidate
from .v72_capital_fx import assess_funding_jpy

v73_bp = Blueprint("dropship_v73", __name__, url_prefix="/dropship/v7.3")

@v73_bp.get("/endpoint")
def endpoint():
    return jsonify({
        "version":"7.3", "endpoint":"research_read_only_complete",
        "operational_acceptance":"pending_actual_fee_returns_and_shadow_evidence",
        "components":{"cj_market_read":True,"ebay_browse_read":True,
                      "single_item_evidence":True,"capital_fx_check":True,
                      "automatic_live_trading":False},
        "human_gate_required":True,"human_gate_ready":False,
        "live_execution_allowed":False})

@v73_bp.post("/evaluate")
def evaluate():
    payload=request.get_json(silent=True)
    if not isinstance(payload,dict) or not isinstance(payload.get("observation"),dict):
        return jsonify({"error":"invalid_observation","live_execution_allowed":False}),400
    obs=payload["observation"]
    if not isinstance(obs.get("evidence",{}),dict):
        return jsonify({"error":"invalid_evidence","live_execution_allowed":False}),400
    report=assess_observed_candidate(obs)
    fx=payload.get("funding")
    if fx is None:
        funding={"status":"blocked_incomplete_evidence","unknown_fields":["verified_funding_evidence"],
                 "human_gate_ready":False,"live_execution_allowed":False}
    elif not isinstance(fx,dict):
        return jsonify({"error":"invalid_funding","live_execution_allowed":False}),400
    else:
        allowed={"available_jpy","usd_jpy_rate","rate_source","rate_observed_at",
                 "item_usd","freight_usd","reserve_usd"}
        funding=assess_funding_jpy(**{k:v for k,v in fx.items() if k in allowed})
    return jsonify({"version":"7.3","research":report,"funding":funding,
                    "acceptance":"pending_actual_fee_returns_and_shadow_evidence",
                    "one_item_only":True,"human_gate_required":True,
                    "human_gate_ready":False,"live_execution_allowed":False})
