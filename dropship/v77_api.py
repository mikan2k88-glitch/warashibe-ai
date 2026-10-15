from flask import Blueprint, jsonify, request
from .v77_shadow_audit import summarize_observations
v77_bp=Blueprint("dropship_v77",__name__,url_prefix="/dropship/v7.7")
@v77_bp.get("/endpoint")
def status():
    return jsonify({"version":"7.7","status":"shadow_audit_ready",
                    "actual_shadow_acceptance":"pending",
                    "human_gate_ready":False,"live_execution_allowed":False})
@v77_bp.post("/audit")
def audit():
    data=request.get_json(silent=True)
    if not isinstance(data,dict) or not isinstance(data.get("observations"),list):
        return jsonify({"error":"invalid_observations","live_execution_allowed":False}),400
    try:
        return jsonify(summarize_observations(data["observations"]))
    except ValueError:
        return jsonify({"error":"invalid_observations","live_execution_allowed":False}),400
