"""Design offline benchmarks for Gemini model routing in Warashibe AI.

This module defines benchmark cases and metrics only. It performs no network
calls and does not access secrets.
"""

GEMINI_SANDBOX_BENCHMARK_DESIGN_VERSION = "0.1"

BENCHMARK_MODELS = (
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.5-flash",
)

BENCHMARK_TASKS = (
    "minimal_health_response",
    "structured_json_candidate_evaluation",
    "market_summary",
    "risk_classification",
    "stop_loss_decision",
    "fallback_error_handling",
)

BENCHMARK_METRICS = (
    "success_rate",
    "schema_valid_rate",
    "latency_ms",
    "fallback_rate",
    "consistency_rate",
    "warashibe_task_score",
    "estimated_cost",
)


def build_gemini_sandbox_benchmark_design():
    return {
        "version": GEMINI_SANDBOX_BENCHMARK_DESIGN_VERSION,
        "mode": "offline_design",
        "models": BENCHMARK_MODELS,
        "tasks": BENCHMARK_TASKS,
        "metrics": BENCHMARK_METRICS,
        "repeat_count_per_case": 5,
        "requires_deterministic_fixtures": True,
        "requires_failure_injection": True,
        "requires_result_comparison": True,
        "requires_router_recommendation": True,
        "network_execution_authorized": False,
        "secret_access_authorized": False,
        "production_change_authorized": False,
        "external_action_authorized": False,
        "live_execution_requires_human_gate": True,
        "benchmark_flow": (
            "load_fixture",
            "simulate_model_result",
            "parse_result",
            "validate_schema",
            "inject_failure_case",
            "score_case",
            "aggregate_metrics",
            "recommend_router_policy",
        ),
    }


def validate_gemini_sandbox_benchmark_design():
    design = build_gemini_sandbox_benchmark_design()
    assert design["mode"] == "offline_design"
    assert design["models"][0] == "gemini-3.8-flash"
    assert design["repeat_count_per_case"] >= 3
    assert "fallback_rate" in design["metrics"]
    assert "warashibe_task_score" in design["metrics"]
    assert design["requires_failure_injection"] is True
    assert design["requires_router_recommendation"] is True
    assert design["network_execution_authorized"] is False
    assert design["secret_access_authorized"] is False
    assert design["production_change_authorized"] is False
    assert design["external_action_authorized"] is False
    assert design["live_execution_requires_human_gate"] is True
    return True
