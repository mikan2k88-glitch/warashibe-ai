from flask import Blueprint, jsonify, request
from .v69_cost_model import estimate_v69_costs

v69_bp = Blueprint("dropship_v69", __name__, url_prefix="/dropship/v6.9")

@v69_bp.get("/status")
def status():
    return jsonify({"version": "6.9", "mode": "evidence_model_only",
                    "human_gate_required": True, "live_execution_allowed": False})

@v69_bp.post("/estimate")
def estimate():
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return jsonify({"status": "invalid_payload", "live_execution_allowed": False}), 400
    candidate = payload.get("candidate")
    policy = payload.get("return_policy")
    if not isinstance(candidate, dict) or (policy is not None and not isinstance(policy, dict)):
        return jsonify({"status": "invalid_payload", "live_execution_allowed": False}), 400
    return jsonify(estimate_v69_costs(candidate, return_policy=policy))
