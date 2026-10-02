from capital_filter import evaluate_capital_fit
from research_lab.repair_execution_controller import control_repair_execution


def main():
    planned = control_repair_execution(
        state="plan",
        planning={
            "recurrence_result": {
                "status": "recurrence_not_contained",
                "guardrail_effective": False,
            },
            "repair_kind": "tighten_gate",
            "target": "capital filter product policy",
            "rationale": "align candidate capital rule with the product policy",
            "path": "capital_filter.py",
            "change_summary": "require exact full-capital fit for one candidate",
            "expected_test": "research_lab.test_product_capital_policy",
        },
    )
    assert planned["controller_state"] == "write"
    assert planned["next_action"] == "execute_single_file_git_write"
    assert planned["execution_plan"]["path"] == "capital_filter.py"

    # PG-006 targeted RED: candidate selection must expose one common
    # selection record that can be persisted/audited by later product stages.
    from candidate_engine import create_candidate
    from candidate_pipeline import evaluate_candidates

    candidate = create_candidate(
        name="PG-006 exact-capital candidate",
        purchase_price=10_000,
        expected_sale_price=12_000,
        source="product_test",
        category="book",
        confidence=0.9,
        success_probability=0.8,
    )
    selection = evaluate_candidates([candidate], 10_000)
    record = selection["selection_record"]
    assert record["selected_candidate"] == selection["best_candidate"]
    assert record["selection_reason"]
    assert record["strategy_result"] is not None
    assert "simulation_result" in record

    # PG-007 targeted RED: the product selection record must have a
    # server-side Supabase repository contract that can write, read back,
    # and reject duplicate record keys.
    from research_lab.supabase_selection_record_repository import (
        SupabaseSelectionRecordRepository,
    )

    class _Response:
        def __init__(self, data=None):
            self.data = data or []

    class _Table:
        def __init__(self):
            self.rows = []
            self._op = None
            self._payload = None
            self._key = None

        def insert(self, payload):
            self._op = "insert"
            self._payload = dict(payload)
            return self

        def select(self, _fields):
            self._op = "select"
            return self

        def eq(self, key, value):
            self._key = (key, value)
            return self

        def limit(self, _count):
            return self

        def execute(self):
            if self._op == "insert":
                key = self._payload["record_key"]
                if any(row["record_key"] == key for row in self.rows):
                    raise ValueError("duplicate")
                self.rows.append(dict(self._payload))
                return _Response([dict(self._payload)])
            rows = list(self.rows)
            if self._key is not None:
                key, value = self._key
                rows = [row for row in rows if row.get(key) == value]
            return _Response([dict(row) for row in rows])

    class _Client:
        def __init__(self):
            self.selection_records = _Table()

        def table(self, name):
            assert name == "warashibe_selection_records"
            return self.selection_records

    repository = SupabaseSelectionRecordRepository(_Client())
    stored = repository.append("pg007-test-record", record)
    loaded = repository.get("pg007-test-record")
    assert stored["record_key"] == "pg007-test-record"
    assert loaded["selection_record"] == record

    try:
        repository.append("pg007-test-record", record)
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate record_key must fail closed")

    # PG-008 targeted RED: GPT scheduled supervision needs one deterministic
    # contract for classifying GitHub/Supabase/Render operational health.
    from research_lab.system_health_contract import evaluate_system_health

    healthy = evaluate_system_health({
        "github": {
            "head_sha": "abc",
            "ci_head_sha": "abc",
            "ci_status": "completed",
            "ci_conclusion": "success",
        },
        "supabase": {
            "read_ok": True,
            "write_ok": True,
            "stale_pending_count": 0,
        },
        "render": {"deploy_status": "live"},
        "product": {"next_gap": "PG-008"},
    })
    assert healthy["status"] == "healthy"
    assert healthy["next_action"] == "continue_product_gap"
    assert healthy["anomalies"] == []

    broken_ci = evaluate_system_health({
        "github": {
            "head_sha": "abc",
            "ci_head_sha": "abc",
            "ci_status": "completed",
            "ci_conclusion": "failure",
        },
        "supabase": {
            "read_ok": True,
            "write_ok": True,
            "stale_pending_count": 0,
        },
        "render": {"deploy_status": "live"},
        "product": {"next_gap": "PG-008"},
    })
    assert broken_ci["status"] == "blocked"
    assert broken_ci["next_action"] == "repair_current_problem"
    assert "github_ci_failure" in broken_ci["anomalies"]

    stale_queue = evaluate_system_health({
        "github": {
            "head_sha": "abc",
            "ci_head_sha": "abc",
            "ci_status": "completed",
            "ci_conclusion": "success",
        },
        "supabase": {
            "read_ok": True,
            "write_ok": True,
            "stale_pending_count": 1,
        },
        "render": {"deploy_status": "live"},
        "product": {"next_gap": "PG-008"},
    })
    assert stale_queue["status"] == "degraded"
    assert stale_queue["next_action"] == "inspect_queue"

    # PG-009 targeted RED: one read-only call must be able to fetch
    # an eBay Browse payload and ingest it into canonical market evidence.
    from research_lab.ebay_browse_ingestion_bridge import (
        fetch_and_ingest_browse_search,
    )

    fetch_calls = []
    def _fake_fetch(query, access_token, *, marketplace_id, limit, timeout):
        fetch_calls.append({
            "query": query,
            "token": access_token,
            "marketplace_id": marketplace_id,
            "limit": limit,
            "timeout": timeout,
        })
        return {
            "itemSummaries": [{
                "itemId": "pg009|1",
                "title": "PG-009 Used Camera",
                "price": {"value": "3000", "currency": "JPY"},
                "categories": [{"categoryName": "Digital Cameras"}],
            }]
        }

    pg009 = fetch_and_ingest_browse_search(
        "used camera",
        "test-token",
        marketplace_id="EBAY_JP",
        limit=5,
        timeout=3,
        fetch_payload=_fake_fetch,
        observed_at="2026-10-02T00:00:00+00:00",
    )
    assert fetch_calls == [{
        "query": "used camera",
        "token": "test-token",
        "marketplace_id": "EBAY_JP",
        "limit": 5,
        "timeout": 3,
    }]
    assert pg009.accepted_count == 1
    assert pg009.accepted[0].external_id == "pg009|1"
    assert pg009.accepted[0].source == "ebay_browse"
    assert pg009.accepted[0].purchase_price == 3000
    assert pg009.accepted[0].metadata["asking_price_only"] is True

    from research_lab.ebay_browse_ingestion_bridge import (
        fetch_and_ingest_browse_from_environment,
    )
    runtime_calls = []
    def _runtime_fetch(query, access_token, *, marketplace_id, limit, timeout):
        runtime_calls.append((query, access_token, marketplace_id, limit, timeout))
        return {
            "itemSummaries": [{
                "itemId": "pg009|runtime",
                "title": "PG-009 Runtime Camera",
                "price": {"value": "3000", "currency": "JPY"},
                "categories": [{"categoryName": "Digital Cameras"}],
            }]
        }

    runtime = fetch_and_ingest_browse_from_environment(
        "used camera",
        environ={"EBAY_BROWSE_ACCESS_TOKEN": "runtime-token"},
        marketplace_id="EBAY_JP",
        limit=3,
        timeout=4,
        fetch_payload=_runtime_fetch,
        observed_at="2026-10-02T00:00:00+00:00",
    )
    assert runtime.accepted_count == 1
    assert runtime_calls == [("used camera", "runtime-token", "EBAY_JP", 3, 4)]

    try:
        fetch_and_ingest_browse_from_environment(
            "used camera",
            environ={},
            fetch_payload=_runtime_fetch,
        )
    except RuntimeError as exc:
        assert str(exc) == "eBay Browse access token is not configured"
    else:
        raise AssertionError("missing eBay token must fail closed")

    exact = evaluate_capital_fit(
        10_000,
        {"purchase_price": 10_000},
    )
    assert exact["allowed"] is True

    under = evaluate_capital_fit(
        10_000,
        {"purchase_price": 8_000},
    )
    assert under["allowed"] is False
    assert under["capital_usage_rate"] == 0.8
    assert under["reasons"]

    over = evaluate_capital_fit(
        10_000,
        {"purchase_price": 12_000},
    )
    assert over["allowed"] is False

    zero = evaluate_capital_fit(
        10_000,
        {"purchase_price": 0},
    )
    assert zero["allowed"] is False

    repair = control_repair_execution(
        state="ci",
        write_evidence={
            "before_sha": "f395cf00c46106f69a36bb02ce82d354d1962bc3",
            "after_sha": "8f4480fe46c2737ac28d8e5873ed6f54c0b145d8",
            "path": "capital_filter.py",
            "expected_test": "research_lab.test_product_capital_policy",
        },
        ci_evidence={
            "cycle_id": "product-gap-pg001-1035",
            "repair_id": "pg001-full-capital-policy",
            "observed_sha": "8f4480fe46c2737ac28d8e5873ed6f54c0b145d8",
            "ci_status": "completed",
            "ci_conclusion": "success",
        },
    )
    assert repair["status"] == "repair_pipeline_complete"
    assert repair["milestone_reached"] is True
    assert repair["next_action"] == "advance_problem_queue"
    assert repair["result"]["audit"]["status"] == "repair_audit_record_ready"
    assert repair["result"]["ledger"]["status"] == "repair_ledger_ready"


if __name__ == "__main__":
    main()
