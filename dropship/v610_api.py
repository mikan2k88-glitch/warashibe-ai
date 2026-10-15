from flask import Blueprint, jsonify, request
from .v610_single_candidate import evaluate_one

v610_bp = Blueprint("dropship_v610", __name__, url_prefix="/dropship/v6.10")

@v610_bp.get("/status")
def status():
    return jsonify({"version": "6.10", "mode": "single_candidate_research_only",
                    "human_gate_required": True, "live_execution_allowed": False})

@v610_bp.post("/evaluate")
def evaluate():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not isinstance(payload.get("candidate"), dict):
        return jsonify({"status": "invalid_payload", "live_execution_allowed": False}), 400
    if payload.get("return_policy") is not None and not isinstance(payload["return_policy"], dict):
        return jsonify({"status": "invalid_payload", "live_execution_allowed": False}), 400
    return jsonify(evaluate_one(payload["candidate"],
                               return_policy=payload.get("return_policy"),
                               capital_usd=payload.get("capital_usd")))
