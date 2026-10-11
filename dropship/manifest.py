from __future__ import annotations


V2_ENDPOINTS = [
    {"method": "GET", "path": "/dropship/health", "purpose": "lightweight wake and health"},
    {"method": "GET", "path": "/dropship/status", "purpose": "research service status"},
    {"method": "GET", "path": "/dropship/providers", "purpose": "registered read-only provider types"},
    {"method": "GET", "path": "/dropship/dll/registry", "purpose": "DLL Concierge v5.3 Registry read"},
    {"method": "GET", "path": "/dropship/dll/resilient", "purpose": "DLL Registry degraded/cache read"},
    {"method": "POST", "path": "/dropship/supplier/evaluate", "purpose": "supplier offer evaluation"},
    {"method": "POST", "path": "/dropship/supplier/rank", "purpose": "supplier ranking"},
    {"method": "POST", "path": "/dropship/selection/single", "purpose": "one-item capital-aware selection"},
    {"method": "POST", "path": "/dropship/preflight", "purpose": "freshness/economics/policy/capital preflight"},
    {"method": "POST", "path": "/dropship/shadow/evaluate", "purpose": "shadow evaluation"},
    {"method": "POST", "path": "/dropship/promotion/assess", "purpose": "promotion gate"},
    {"method": "POST", "path": "/dropship/sandbox/cycle", "purpose": "sandbox commerce lifecycle"},
    {"method": "POST", "path": "/dropship/controller/run", "purpose": "single decision controller"},
    {"method": "POST", "path": "/dropship/orchestrator/run", "purpose": "research orchestration"},
    {"method": "POST", "path": "/dropship/strategy/experiment", "purpose": "strategy comparison"},
    {"method": "POST", "path": "/dropship/strategy/walk-forward", "purpose": "walk-forward validation"},
    {"method": "POST", "path": "/dropship/campaign/run", "purpose": "sandbox campaign"},
    {"method": "POST", "path": "/dropship/learning/summarize", "purpose": "outcome learning"},
    {"method": "POST", "path": "/dropship/research/plan", "purpose": "next research plan"},
    {"method": "GET", "path": "/dropship/v2.0/proof", "purpose": "deterministic v2 proof"},
    {"method": "GET", "path": "/dropship/v2.0/acceptance", "purpose": "v2 acceptance"},
]


def build_manifest() -> dict:
    return {
        "service": "warashibe-dropshipping",
        "version": "2.0",
        "mode": "research",
        "endpoint_count": len(V2_ENDPOINTS),
        "endpoints": V2_ENDPOINTS,
        "live_execution_allowed": False,
    }
