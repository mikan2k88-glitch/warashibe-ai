"""Read-only/proposal-only API bridge for Warashibe AI real-world mode."""

from flask import Blueprint, jsonify, request

from real_world_engine import (
    build_real_world_engine_snapshot,
    prepare_real_world_candidate,
    select_real_world_candidate,
)

real_world_bp = Blueprint("real_world", __name__)


@real_world_bp.get("/real-world/status")
def real_world_status():
    return jsonify(build_real_world_engine_snapshot())


@real_world_bp.post("/real-world/evaluate")
def real_world_evaluate():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({
            "status": "invalid_request",
            "reason": "json_object_required",
            "execution_authorized": False,
            "commerce_authorized": False,
        }), 400

    if "candidates" in payload:
        candidates = payload.get("candidates")
        if not isinstance(candidates, list):
            return jsonify({
                "status": "invalid_request",
                "reason": "candidates_must_be_list",
                "execution_authorized": False,
                "commerce_authorized": False,
            }), 400
        return jsonify(select_real_world_candidate(candidates))

    return jsonify(prepare_real_world_candidate(payload))
