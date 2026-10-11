from __future__ import annotations

from flask import Blueprint, jsonify, request

from . import DROPSHIP_VERSION
from .dll_concierge_client import fetch_registry
from .economics import evaluate_dropship_economics
from .policy import evaluate_dropship_policy
from .sandbox import run_sandbox_cycle


dropship_bp = Blueprint("dropship", __name__, url_prefix="/dropship")


@dropship_bp.get("/status")
def status():
    return jsonify({
        "service": "warashibe-dropshipping",
        "version": DROPSHIP_VERSION,
        "mode": "sandbox_only",
        "live_execution_allowed": False,
        "human_gate_required_for_live": True,
    })


@dropship_bp.get("/dll/registry")
def dll_registry():
    try:
        registry = fetch_registry()
        return jsonify({
            "status": "ok",
            "source": "dll-concierge-v5.3",
            "registry": registry,
        })
    except RuntimeError as exc:
        return jsonify({
            "status": "unavailable",
            "source": "dll-concierge-v5.3",
            "error": str(exc),
        }), 503


@dropship_bp.post("/evaluate")
def evaluate():
    payload = request.get_json(silent=True) or {}
    economics = evaluate_dropship_economics(payload)
    policy = evaluate_dropship_policy(payload, economics)
    return jsonify({
        "status": "allowed" if policy["allowed"] else "blocked",
        "economics": economics,
        "policy": policy,
    })


@dropship_bp.post("/sandbox/cycle")
def sandbox_cycle():
    payload = request.get_json(silent=True) or {}
    return jsonify(run_sandbox_cycle(payload))
