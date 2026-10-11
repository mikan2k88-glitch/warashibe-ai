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
from .pipeline import run_dropship_decision_pipeline
from .readiness import assess_live_readiness
from .research_cycle import run_research_cycle
from .observations import summarize_observations
from .live_guard import authorize_action
from .dll_registry import find_components
from .duplicate_guard import assess_duplicate_order
from .recovery import classify_recovery
from .audit import create_audit_record
from .burn_in import assess_burn_in
from .evidence_bundle import build_readiness_evidence
from .selection import select_single_candidate
from .maturity import determine_maturity
from .dashboard import build_dashboard_summary
from .controller import run_controller
from .proof import build_proof, build_acceptance
from .snapshot import build_research_snapshot
from .release import build_release_status
from .hq import build_hq_status
from .human_gate import prepare_human_gate_package, verify_human_approval
from .freshness import assess_freshness
from .provider_registry import ProviderRegistry, ProviderDescriptor
from .runtime_controller import run_runtime_controller
from .dll_resilience import fetch_registry_resilient
from .dependency_health import build_dependency_health
from .strategy_experiment import compare_strategies
from .walk_forward import run_walk_forward
from .strategy_promotion import assess_strategy_promotion
from .preflight import run_preflight
from .policy_profile import evaluate_policy_profile


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


@dropship_bp.post("/pipeline/evaluate")
def pipeline_evaluate():
    payload = request.get_json(silent=True) or {}
    offers = payload.get("offers") or []
    return jsonify(run_dropship_decision_pipeline(offers))


@dropship_bp.post("/readiness/assess")
def readiness_assess():
    payload = request.get_json(silent=True) or {}
    return jsonify(assess_live_readiness(payload))


@dropship_bp.post("/research/cycle")
def research_cycle():
    payload = request.get_json(silent=True) or {}
    return jsonify(run_research_cycle(
        payload.get("offers") or [],
        payload.get("historical_observations") or [],
    ))


@dropship_bp.post("/observations/summarize")
def observations_summarize():
    payload = request.get_json(silent=True) or {}
    return jsonify(summarize_observations(payload.get("observations") or []))


@dropship_bp.post("/guard/authorize")
def guard_authorize():
    payload = request.get_json(silent=True) or {}
    return jsonify(authorize_action(
        str(payload.get("action") or ""),
        human_approved=payload.get("human_approved") is True,
    ))


@dropship_bp.post("/dll/search")
def dll_search():
    payload = request.get_json(silent=True) or {}
    try:
        registry = fetch_registry()
        return jsonify({
            "status": "ok",
            "matches": find_components(registry, payload.get("keywords") or []),
        })
    except RuntimeError as exc:
        return jsonify({"status": "unavailable", "error": str(exc)}), 503


@dropship_bp.post("/orders/duplicate-check")
def duplicate_check():
    payload = request.get_json(silent=True) or {}
    return jsonify(assess_duplicate_order(
        payload.get("order") or {},
        payload.get("existing_fingerprints") or [],
    ))


@dropship_bp.post("/recovery/classify")
def recovery_classify():
    payload = request.get_json(silent=True) or {}
    return jsonify(classify_recovery(
        str(payload.get("action") or ""),
        str(payload.get("error_kind") or ""),
        int(payload.get("attempts") or 0),
        int(payload.get("max_attempts") or 3),
    ))


@dropship_bp.post("/audit/record")
def audit_record():
    payload = request.get_json(silent=True) or {}
    return jsonify(create_audit_record(
        str(payload.get("event_type") or "unknown"),
        payload.get("payload") or {},
    ))


@dropship_bp.post("/burn-in/assess")
def burn_in_assess():
    payload = request.get_json(silent=True) or {}
    return jsonify(assess_burn_in(payload))


@dropship_bp.post("/readiness/evidence")
def readiness_evidence():
    payload = request.get_json(silent=True) or {}
    return jsonify(build_readiness_evidence(
        shadow_observations=int(payload.get("shadow_observations") or 0),
        shadow_days=int(payload.get("shadow_days") or 0),
        sandbox_cycles=int(payload.get("sandbox_cycles") or 0),
        evidence_integrity_passed=payload.get("evidence_integrity_passed") is True,
        promotion_gate_passed=payload.get("promotion_gate_passed") is True,
        duplicate_order_guard=payload.get("duplicate_order_guard", True) is True,
        kill_switch_ready=payload.get("kill_switch_ready", True) is True,
        audit_log_ready=payload.get("audit_log_ready", True) is True,
    ))


@dropship_bp.post("/selection/single")
def selection_single():
    payload = request.get_json(silent=True) or {}
    ranking = rank_supplier_offers(payload.get("offers") or [])
    return jsonify(select_single_candidate(
        ranking,
        strategy=str(payload.get("strategy") or "balanced"),
        available_capital=float(payload.get("available_capital") or 0),
    ))


@dropship_bp.post("/maturity/assess")
def maturity_assess():
    payload = request.get_json(silent=True) or {}
    return jsonify(determine_maturity(payload))


@dropship_bp.post("/dashboard/summary")
def dashboard_summary():
    payload = request.get_json(silent=True) or {}
    return jsonify(build_dashboard_summary(payload))


@dropship_bp.post("/controller/run")
def controller_run():
    payload = request.get_json(silent=True) or {}
    return jsonify(run_controller(
        payload.get("offers") or [],
        strategy=str(payload.get("strategy") or "balanced"),
        available_capital=float(payload.get("available_capital") or 3000),
    ))


@dropship_bp.get("/v0.9/proof")
def v09_proof():
    return jsonify(build_proof())


@dropship_bp.get("/v0.9/acceptance")
def v09_acceptance():
    return jsonify(build_acceptance())


@dropship_bp.post("/snapshot/build")
def snapshot_build():
    payload = request.get_json(silent=True) or {}
    return jsonify(build_research_snapshot(payload))


@dropship_bp.get("/v1.0/status")
def v10_status():
    return jsonify(build_release_status())


@dropship_bp.get("/v1.0/proof")
def v10_proof():
    return jsonify(build_proof())


@dropship_bp.get("/v1.0/acceptance")
def v10_acceptance():
    return jsonify(build_acceptance())


@dropship_bp.post("/hq/status")
def hq_status():
    payload = request.get_json(silent=True) or {}
    return jsonify(build_hq_status(payload))


@dropship_bp.post("/human-gate/package")
def human_gate_package():
    payload = request.get_json(silent=True) or {}
    return jsonify(prepare_human_gate_package(payload))


@dropship_bp.post("/human-gate/verify")
def human_gate_verify():
    payload = request.get_json(silent=True) or {}
    return jsonify(verify_human_approval(str(payload.get("code") or "")))


@dropship_bp.post("/freshness/assess")
def freshness_assess():
    payload = request.get_json(silent=True) or {}
    return jsonify(assess_freshness(
        payload.get("observed_at"),
        now=payload.get("now"),
        max_age_hours=float(payload.get("max_age_hours") or 24),
    ))


@dropship_bp.post("/runtime/controller")
def runtime_controller():
    payload = request.get_json(silent=True) or {}
    return jsonify(run_runtime_controller(
        payload.get("offers") or [],
        historical_observations=payload.get("historical_observations") or [],
        max_age_hours=float(payload.get("max_age_hours") or 24),
    ))


@dropship_bp.get("/providers")
def providers():
    registry = ProviderRegistry()
    registry.register(ProviderDescriptor(name="fixture"))
    registry.register(ProviderDescriptor(name="http-json"))
    return jsonify({
        "status": "ok",
        "providers": registry.list(),
        "live_order_provider_registered": False,
    })


@dropship_bp.get("/dll/resilient")
def dll_resilient():
    return jsonify(fetch_registry_resilient())


@dropship_bp.post("/dependencies/health")
def dependencies_health():
    payload = request.get_json(silent=True) or {}
    return jsonify(build_dependency_health(
        dll_status=str(payload.get("dll_status") or "unknown"),
        provider_count=int(payload.get("provider_count") or 0),
    ))


@dropship_bp.post("/strategy/experiment")
def strategy_experiment():
    payload = request.get_json(silent=True) or {}
    return jsonify(compare_strategies(
        payload.get("batches") or [],
        available_capital=float(payload.get("available_capital") or 3000),
    ))


@dropship_bp.post("/strategy/walk-forward")
def strategy_walk_forward():
    payload = request.get_json(silent=True) or {}
    return jsonify(run_walk_forward(
        payload.get("windows") or [],
        strategy=str(payload.get("strategy") or "balanced"),
        available_capital=float(payload.get("available_capital") or 3000),
        min_windows=int(payload.get("min_windows") or 3),
    ))


@dropship_bp.post("/strategy/promotion")
def strategy_promotion():
    payload = request.get_json(silent=True) or {}
    return jsonify(assess_strategy_promotion(
        payload.get("champion") or {},
        payload.get("challenger") or {},
    ))


@dropship_bp.post("/preflight")
def preflight():
    payload = request.get_json(silent=True) or {}
    candidate = payload.get("candidate") or {}
    return jsonify(run_preflight(
        candidate,
        available_capital=float(payload.get("available_capital") or 3000),
        max_age_hours=float(payload.get("max_age_hours") or 24),
        policy_profile=payload.get("policy_profile") or None,
    ))


@dropship_bp.post("/policy/profile")
def policy_profile():
    payload = request.get_json(silent=True) or {}
    economics = evaluate_dropship_economics(payload.get("candidate") or {})
    return jsonify(evaluate_policy_profile(
        payload.get("candidate") or {},
        economics,
        payload.get("profile") or None,
    ))
