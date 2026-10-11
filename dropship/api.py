from __future__ import annotations

from flask import Blueprint, jsonify, request

from . import DROPSHIP_VERSION
from .dll_concierge_client import fetch_registry
from .economics import evaluate_dropship_economics
from .policy import evaluate_dropship_policy
from .sandbox import run_sandbox_cycle
from .shadow import evaluate_shadow_candidate
from .promotion import assess_promotion
from .runtime import build_runtime_status
from .supplier import evaluate_supplier_offer
from .ranking import rank_supplier_offers
from .commerce import build_sandbox_commerce_plan
from .stop_loss import assess_listing_stop_loss


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


@dropship_bp.post("/shadow/evaluate")
def shadow_evaluate():
    payload = request.get_json(silent=True) or {}
    return jsonify(evaluate_shadow_candidate(payload))


@dropship_bp.post("/promotion/assess")
def promotion_assess():
    payload = request.get_json(silent=True) or {}
    shadow_result = evaluate_shadow_candidate(payload)
    return jsonify(assess_promotion(shadow_result))


@dropship_bp.get("/runtime/status")
def runtime_status():
    return jsonify(build_runtime_status())


@dropship_bp.post("/supplier/evaluate")
def supplier_evaluate():
    payload = request.get_json(silent=True) or {}
    return jsonify(evaluate_supplier_offer(payload))


@dropship_bp.post("/supplier/rank")
def supplier_rank():
    payload = request.get_json(silent=True) or {}
    offers = payload.get("offers") or []
    return jsonify(rank_supplier_offers(offers))


@dropship_bp.post("/commerce/plan")
def commerce_plan():
    payload = request.get_json(silent=True) or {}
    offers = payload.get("offers") or []
    return jsonify(build_sandbox_commerce_plan(offers))


@dropship_bp.post("/listing/stop-loss")
def listing_stop_loss():
    payload = request.get_json(silent=True) or {}
    return jsonify(assess_listing_stop_loss(
        payload,
        ad_cost_cap=float(payload.get("ad_cost_cap") or 1000.0),
    ))
