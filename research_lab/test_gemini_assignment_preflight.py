"""No-network checks for future Gemini assignment approval and budget review."""
from research_lab.gemini_assignment_preflight import review_assignment_preflight


def run_tests():
    valid = {
        "sandbox_only": True, "latest_ci_green": True, "ci_sha_matches_head": True,
        "authenticated_entry": True, "durable_shared_ledger_verified": True,
        "network_gate_approved": True, "secret_read_gate_approved": True,
        "human_gate_approved": True, "structured_output_ready": True,
        "assignment_id": "offline-assignment", "source_run_id": "offline-run",
        "max_requests": 1, "max_input_tokens": 2000, "max_output_tokens": 512,
        "max_cost_usd": 0.10, "estimated_cost_usd": 0.01,
        "requested_capabilities": [],
    }
    good = review_assignment_preflight(valid)
    assert good["ready_for_separate_runtime_review"] is True
    assert all(good[key] is False for key in (
        "gemini_api_call_authorized", "network_execution_authorized",
        "secret_read_authorized", "codex_execution_authorized",
        "main_write_authorized", "commerce_authorized",
    ))
    cases = (
        ("human_gate_approved", False),
        ("latest_ci_green", False),
        ("ci_sha_matches_head", False),
        ("authenticated_entry", False),
        ("durable_shared_ledger_verified", False),
        ("network_gate_approved", False),
        ("secret_read_gate_approved", False),
        ("max_requests", 2),
        ("max_input_tokens", 2001),
        ("max_output_tokens", 513),
        ("max_cost_usd", 0.11),
        ("estimated_cost_usd", 0.11),
        ("estimated_cost_usd", None),
        ("requested_capabilities", ["modify_main_branch"]),
        ("assignment_id", ""),
        ("max_requests", "1"),
        ("max_requests", True),
        ("max_requests", 1.0),
        ("max_input_tokens", "2000"),
        ("max_input_tokens", 2000.0),
        ("max_output_tokens", float("inf")),
        ("max_output_tokens", float("nan")),
        ("max_cost_usd", "0.10"),
        ("max_cost_usd", float("nan")),
        ("max_cost_usd", float("inf")),
        ("max_cost_usd", float("-inf")),
        ("max_cost_usd", True),
        ("max_cost_usd", 0),
        ("estimated_cost_usd", "0.01"),
        ("estimated_cost_usd", float("nan")),
        ("estimated_cost_usd", float("inf")),
        ("estimated_cost_usd", -0.01),
    )
    for key, value in cases:
        state = dict(valid, **{key: value})
        result = review_assignment_preflight(state)
        assert result["ready_for_separate_runtime_review"] is False, (key, result)
        assert result["gemini_api_call_authorized"] is False
    assert review_assignment_preflight(None)["ready_for_separate_runtime_review"] is False


if __name__ == "__main__":
    run_tests()
    print("Gemini offline preflight tests passed; no external execution authorized")
