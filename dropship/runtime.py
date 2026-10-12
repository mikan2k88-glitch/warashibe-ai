from __future__ import annotations


def build_runtime_status(*, dll_registry_ok: bool | None = None) -> dict:
    checks = {
        "sandbox_only": True,
        "live_execution_disabled": True,
        "human_gate_required": True,
        "dll_registry_reachable": dll_registry_ok,
    }
    degraded = dll_registry_ok is False
    return {
        "service": "warashibe-dropshipping",
        "version": "0.2",
        "maturity_stage": "shadow_sandbox",
        "status": "degraded" if degraded else "healthy",
        "checks": checks,
        "external_writes_enabled": False,
        "live_execution_allowed": False,
    }
