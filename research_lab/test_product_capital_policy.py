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

    # PG-010 targeted RED: real commerce must have one common fail-closed
    # execution gate and produce an auditable dry-run plan without moving money.
    from research_lab.commerce_execution_gate import (
        prepare_commerce_execution,
    )

    pg010 = prepare_commerce_execution(
        {
            "trade_id": "pg010-trade-001",
            "operation": "purchase",
            "item_id": "pg010-item-001",
            "amount_jpy": 3000,
            "capital_before_jpy": 3000,
            "idempotency_key": "pg010-trade-001-purchase",
        },
        human_approved=False,
        dry_run=True,
    )
    assert pg010["status"] == "human_gate_required"
    assert pg010["dry_run"] is True
    assert pg010["external_action_authorized"] is False
    assert pg010["audit_record"]["trade_id"] == "pg010-trade-001"

    pg010_ready = prepare_commerce_execution(
        {
            "trade_id": "pg010-trade-002",
            "operation": "sale",
            "item_id": "pg010-item-002",
            "amount_jpy": 4500,
            "capital_before_jpy": 3000,
            "idempotency_key": "pg010-trade-002-sale",
        },
        human_approved=True,
        dry_run=True,
    )
    assert pg010_ready["status"] == "dry_run_ready"
    assert pg010_ready["external_action_authorized"] is False
    assert pg010_ready["execution_plan"]["operation"] == "sale"

    pg010_live_blocked = prepare_commerce_execution(
        {
            "trade_id": "pg010-trade-live",
            "operation": "purchase",
            "item_id": "pg010-item-live",
            "amount_jpy": 3000,
            "capital_before_jpy": 3000,
            "idempotency_key": "pg010-trade-live-purchase",
        },
        human_approved=True,
        dry_run=False,
    )
    assert pg010_live_blocked["status"] == "live_execution_blocked"
    assert pg010_live_blocked["external_action_authorized"] is False
    assert pg010_live_blocked["purchase_authorized"] is False
    assert pg010_live_blocked["payment_authorized"] is False
    assert pg010_live_blocked["sale_authorized"] is False

    try:
        prepare_commerce_execution(
            {
                "trade_id": "pg010-trade-003",
                "operation": "payment",
                "item_id": "pg010-item-003",
                "amount_jpy": 3001,
                "capital_before_jpy": 3000,
                "idempotency_key": "pg010-trade-003-payment",
            },
            human_approved=True,
            dry_run=True,
        )
    except ValueError as exc:
        assert "amount exceeds available capital" in str(exc)
    else:
        raise AssertionError("over-capital commerce request must fail closed")

    # PG-011 targeted RED: initial real-world operation must enforce
    # Tokyo/small-parcel physical constraints and classify domestic data sources.
    from research_lab.initial_physical_operation_policy import (
        evaluate_initial_physical_fit,
        domestic_market_access_snapshot,
    )

    small = evaluate_initial_physical_fit({
        "package_size_class": "compact",
        "weight_grams": 350,
        "fragility_score": 0.1,
        "storage_score": 0.9,
        "domestic_shipping": True,
        "shipping_cost_jpy": 450,
    })
    assert small["allowed"] is True
    assert small["physical_fit"] == "preferred"

    large = evaluate_initial_physical_fit({
        "package_size_class": "large",
        "weight_grams": 8000,
        "fragility_score": 0.2,
        "storage_score": 0.2,
        "domestic_shipping": True,
        "shipping_cost_jpy": 2200,
    })
    assert large["allowed"] is False
    assert "package_too_large" in large["reasons"]

    unknown = evaluate_initial_physical_fit({
        "package_size_class": None,
        "weight_grams": None,
        "fragility_score": None,
        "storage_score": None,
        "domestic_shipping": None,
        "shipping_cost_jpy": None,
    })
    assert unknown["allowed"] is False
    assert unknown["physical_fit"] == "insufficient_data"

    physical_candidate = create_candidate(
        name="PG-011 compact candidate",
        purchase_price=3000,
        expected_sale_price=4200,
        source="domestic_fixture",
        category="small_electronics",
        confidence=0.8,
        success_probability=0.7,
        package_size_class="compact",
        weight_grams=350,
        shipping_cost_jpy=450,
        fragility_score=0.1,
        storage_score=0.9,
        domestic_shipping=True,
    )
    physical_eval = physical_candidate["evaluation"]["physical"]
    assert physical_eval["package_size_class"] == "compact"
    assert physical_eval["weight_grams"] == 350
    assert physical_eval["shipping_cost_jpy"] == 450
    assert physical_eval["fragility_score"] == 0.1
    assert physical_eval["storage_score"] == 0.9
    assert physical_eval["domestic_shipping"] is True
    assert physical_eval["policy"]["allowed"] is True

    markets = domestic_market_access_snapshot()
    assert markets["target_region"] == "Tokyo, Japan"
    assert markets["initial_package_policy"] == "small_first"
    assert markets["providers"]["rakuten_ichiba"]["access"] == "official_read_only_api"
    assert markets["providers"]["yahoo_shopping"]["access"] == "official_read_only_api"
    assert markets["providers"]["ebay_browse"]["role"] == "comparison_market"
    assert markets["providers"]["mercari"]["access"] == "research_only_until_official_path_confirmed"
    assert markets["providers"]["yahoo_auctions"]["access"] == "research_only_until_official_path_confirmed"
    assert markets["commerce_authorized"] is False

    # PG-012 targeted RED: Yahoo! Shopping official read-only search
    # must flow into MarketObservation -> Candidate -> PG-011 physical policy.
    from research_lab.yahoo_shopping_ingestion_bridge import (
        fetch_and_ingest_yahoo_shopping_from_environment,
        yahoo_observation_to_candidate,
    )

    yahoo_calls = []
    def _fake_yahoo_fetch(query, appid, *, results, condition, timeout):
        yahoo_calls.append((query, appid, results, condition, timeout))
        return {
            "hits": [{
                "code": "seller:item-001",
                "name": "PG-012 Compact Item",
                "price": 3000,
                "condition": "used",
                "url": "https://shopping.yahoo.co.jp/products/example",
                "seller": {"name": "fixture-store"},
                "genreCategory": {"name": "small electronics"},
            }]
        }

    yahoo_result = fetch_and_ingest_yahoo_shopping_from_environment(
        "compact item",
        environ={"YAHOO_SHOPPING_APP_ID": "test-appid"},
        results=5,
        condition="used",
        timeout=3,
        fetch_payload=_fake_yahoo_fetch,
        observed_at="2026-10-02T00:00:00+00:00",
    )
    assert yahoo_calls == [("compact item", "test-appid", 5, "used", 3)]
    assert yahoo_result.accepted_count == 1
    yahoo_observation = yahoo_result.accepted[0]
    assert yahoo_observation.source == "yahoo_shopping"
    assert yahoo_observation.currency == "JPY"
    assert yahoo_observation.purchase_price == 3000
    assert yahoo_observation.metadata["asking_price_only"] is True

    yahoo_candidate = yahoo_observation_to_candidate(yahoo_observation)
    assert yahoo_candidate["source"] == "yahoo_shopping"
    assert yahoo_candidate["evaluation"]["physical"]["policy"]["allowed"] is False
    assert yahoo_candidate["evaluation"]["physical"]["policy"]["physical_fit"] == "insufficient_data"

    from urllib.parse import parse_qs, urlparse
    from unittest.mock import patch
    from research_lab import yahoo_shopping_ingestion_bridge as yahoo_bridge

    yahoo_request = yahoo_bridge.build_item_search_request(
        "camera & case",
        "test-appid",
        results=7,
        condition="used",
    )
    yahoo_url = urlparse(yahoo_request.full_url)
    yahoo_params = parse_qs(yahoo_url.query)
    assert yahoo_request.get_method() == "GET"
    assert yahoo_url.scheme == "https"
    assert yahoo_url.netloc == "shopping.yahooapis.jp"
    assert yahoo_url.path == "/ShoppingWebService/V3/itemSearch"
    assert yahoo_params["query"] == ["camera & case"]
    assert yahoo_params["results"] == ["7"]
    assert yahoo_params["condition"] == ["used"]

    for wrong_url in (
        "https://other.invalid/ShoppingWebService/V3/itemSearch",
        "http://shopping.yahooapis.jp/ShoppingWebService/V3/itemSearch",
        "https://shopping.yahooapis.jp/ShoppingWebService/V3/order",
    ):
        with patch.object(yahoo_bridge, "YAHOO_ITEM_SEARCH_URL", wrong_url):
            try:
                yahoo_bridge.build_item_search_request("camera", "test-appid")
            except ValueError:
                pass
            else:
                raise AssertionError("non-allowlisted Yahoo destination accepted")

    try:
        yahoo_bridge.NoRedirectHandler().redirect_request(
            yahoo_request,
            None,
            302,
            "redirect",
            {},
            "https://other.invalid/collect",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Yahoo redirect accepted")

    try:
        fetch_and_ingest_yahoo_shopping_from_environment(
            "compact item",
            environ={},
            fetch_payload=_fake_yahoo_fetch,
        )
    except RuntimeError as exc:
        assert str(exc) == "Yahoo! Shopping app ID is not configured"
    else:
        raise AssertionError("missing Yahoo app ID must fail closed")

    # PG-013 targeted RED: a Yahoo JAN must resolve against Rakuten
    # Product Search JAN and produce a conservative domestic price comparison.
    from research_lab.rakuten_product_ingestion_bridge import (
        fetch_and_ingest_rakuten_product_from_environment,
    )
    from research_lab.domestic_market_comparison import (
        compare_domestic_observations,
    )

    yahoo_jan_payload = {
        "hits": [{
            "code": "seller:jan-item",
            "name": "PG-013 Compact Camera",
            "price": 3000,
            "condition": "used",
            "url": "https://shopping.yahoo.co.jp/products/pg013",
            "janCode": "4901234567894",
            "genreCategory": {"name": "camera"},
            "seller": {"name": "fixture-store"},
        }]
    }
    yahoo_jan_result = yahoo_bridge.ingest_yahoo_shopping_payload(
        yahoo_jan_payload,
        observed_at="2026-10-02T00:00:00+00:00",
    )
    yahoo_jan_observation = yahoo_jan_result.accepted[0]
    assert yahoo_jan_observation.metadata["gtin"] == "4901234567894"

    rakuten_calls = []
    def _fake_rakuten_fetch(product_code, application_id, access_key, *, hits, timeout):
        rakuten_calls.append((product_code, application_id, access_key, hits, timeout))
        return {
            "items": [{
                "productId": "rakuten-product-001",
                "productCode": "4901234567894",
                "productName": "PG-013 Compact Camera",
                "genreName": "camera",
                "salesMinPrice": 2800,
                "averagePrice": 3200,
                "productUrlPC": "https://product.rakuten.co.jp/product/pg013/",
            }]
        }

    rakuten_result = fetch_and_ingest_rakuten_product_from_environment(
        "4901234567894",
        environ={
            "RAKUTEN_APPLICATION_ID": "test-appid",
            "RAKUTEN_ACCESS_KEY": "test-access-key",
        },
        hits=5,
        timeout=3,
        fetch_payload=_fake_rakuten_fetch,
        observed_at="2026-10-02T00:00:00+00:00",
    )
    assert rakuten_calls == [
        ("4901234567894", "test-appid", "test-access-key", 5, 3)
    ]
    assert rakuten_result.accepted_count == 1
    rakuten_observation = rakuten_result.accepted[0]
    assert rakuten_observation.metadata["gtin"] == "4901234567894"
    assert rakuten_observation.purchase_price == 2800

    comparison = compare_domestic_observations(
        yahoo_jan_observation,
        rakuten_observation,
    )
    assert comparison["same_identity"] is True
    assert comparison["identity_type"] == "gtin"
    assert comparison["lowest_asking_price_jpy"] == 2800
    assert comparison["lowest_asking_source"] == "rakuten_product"
    assert comparison["price_spread_jpy"] == 200
    assert comparison["commerce_authorized"] is False

    from dataclasses import replace
    from urllib.parse import parse_qs, urlparse
    from unittest.mock import patch
    from research_lab import rakuten_product_ingestion_bridge as rakuten_bridge

    rakuten_request = rakuten_bridge.build_product_search_request(
        "4901234567894",
        "test-appid",
        "test-access-key",
        hits=7,
    )
    rakuten_url = urlparse(rakuten_request.full_url)
    rakuten_params = parse_qs(rakuten_url.query)
    assert rakuten_request.get_method() == "GET"
    assert rakuten_url.scheme == "https"
    assert rakuten_url.netloc == "openapi.rakuten.co.jp"
    assert rakuten_url.path == "/ichibaproduct/api/Product/Search/20250801"
    assert rakuten_params["productCode"] == ["4901234567894"]
    assert rakuten_params["applicationId"] == ["test-appid"]
    assert "accessKey" not in rakuten_params
    assert any(
        key.lower() == "accesskey" and value == "test-access-key"
        for key, value in rakuten_request.headers.items()
    )

    for wrong_url in (
        "https://other.invalid/ichibaproduct/api/Product/Search/20250801",
        "http://openapi.rakuten.co.jp/ichibaproduct/api/Product/Search/20250801",
        "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260701",
    ):
        with patch.object(rakuten_bridge, "RAKUTEN_PRODUCT_SEARCH_URL", wrong_url):
            try:
                rakuten_bridge.build_product_search_request(
                    "4901234567894",
                    "test-appid",
                    "test-access-key",
                )
            except ValueError:
                pass
            else:
                raise AssertionError("non-allowlisted Rakuten destination accepted")

    try:
        rakuten_bridge.NoRedirectHandler().redirect_request(
            rakuten_request,
            None,
            302,
            "redirect",
            {},
            "https://other.invalid/collect",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Rakuten redirect accepted")

    try:
        fetch_and_ingest_rakuten_product_from_environment(
            "4901234567894",
            environ={},
            fetch_payload=_fake_rakuten_fetch,
        )
    except RuntimeError as exc:
        assert str(exc) == "Rakuten application ID is not configured"
    else:
        raise AssertionError("missing Rakuten application ID must fail closed")

    mismatched = replace(
        rakuten_observation,
        metadata={**rakuten_observation.metadata, "gtin": "4905524535815"},
    )
    mismatch = compare_domestic_observations(
        yahoo_jan_observation,
        mismatched,
    )
    assert mismatch["same_identity"] is False
    assert mismatch["status"] == "identity_mismatch"
    assert mismatch["lowest_asking_price_jpy"] is None

    # PG-014 targeted RED: deterministic physical evidence with matching
    # GTIN must enrich a domestic candidate and only then allow a proposal.
    from research_lab.real_market_adapter import observation_to_candidate
    from research_lab.physical_evidence_enrichment import (
        enrich_candidate_with_physical_evidence,
    )
    from research_lab.cross_market_proposal import (
        build_cross_market_proposal,
    )

    pg014_candidate = observation_to_candidate(rakuten_observation)
    assert pg014_candidate["metadata"]["gtin"] == "4901234567894"
    assert pg014_candidate["evaluation"]["physical"]["policy"]["physical_fit"] == "insufficient_data"

    physical_evidence = {
        "gtin": "4901234567894",
        "source_kind": "manufacturer_spec",
        "source_ref": "manufacturer:pg014-camera",
        "observed_at": "2026-10-02T00:00:00+00:00",
        "package_size_class": "compact",
        "weight_grams": 420,
        "shipping_cost_jpy": 450,
        "fragility_score": 0.2,
        "storage_score": 0.9,
        "domestic_shipping": True,
    }
    enriched = enrich_candidate_with_physical_evidence(
        pg014_candidate,
        physical_evidence,
    )
    assert enriched["status"] == "enriched"
    assert enriched["candidate"]["evaluation"]["physical"]["policy"]["allowed"] is True
    assert enriched["candidate"]["metadata"]["physical_evidence"]["source_kind"] == "manufacturer_spec"

    proposal = build_cross_market_proposal(
        comparison,
        enriched["candidate"],
    )
    assert proposal["status"] == "proposal_ready"
    assert proposal["proposal_type"] == "review_candidate"
    assert proposal["candidate_source"] == "rakuten_product"
    assert proposal["reference_price_spread_jpy"] == 200
    assert proposal["human_review_required"] is True
    assert proposal["commerce_authorized"] is False
    assert proposal["external_action_authorized"] is False

    mismatched_evidence = dict(
        physical_evidence,
        gtin="4905524535815",
    )
    rejected_enrichment = enrich_candidate_with_physical_evidence(
        pg014_candidate,
        mismatched_evidence,
    )
    assert rejected_enrichment["status"] == "rejected"
    assert rejected_enrichment["reason"] == "identity_mismatch"

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
