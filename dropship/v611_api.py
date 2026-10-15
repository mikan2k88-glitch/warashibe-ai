from flask import Blueprint, jsonify, request
from .v611_evidence_mapping import assess_observed_candidate

v611_bp = Blueprint("dropship_v611", __name__, url_prefix="/dropship/v6.11")

@v611_bp.get("/status")
def status():
    return jsonify({"version": "6.11", "mode": "read_only_evidence_mapping",
                    "human_gate_ready": False, "live_execution_allowed": False})

@v611_bp.post("/assess")
def assess():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not isinstance(payload.get("observation"), dict):
        return jsonify({"status": "invalid_payload", "live_execution_allowed": False}), 400
    if not isinstance(payload["observation"].get("evidence", {}), dict):
        return jsonify({"status": "invalid_evidence", "live_execution_allowed": False}), 400
    return jsonify(assess_observed_candidate(payload["observation"],
                                              capital_usd=payload.get("capital_usd")))
