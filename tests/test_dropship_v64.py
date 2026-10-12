from dropship.cj_provider import normalize_cj_product
from dropship.cost_completeness import assess_cost_completeness
from dropship.terms_evidence import assess_terms_evidence
from dropship.v64_proof import build_v64_acceptance, build_v64_proof
from dropship.v64_release import build_v64_release_status
from dropship.supabase_rest import SupabaseRestClient
from dropship.supabase_persistence import persist_observations


def _complete_candidate():
    return {
        "product_key": "complete",
        "supplier_cost": 10,
        "supplier_shipping": 2,
        "platform_fee_rate": 0.1,
        "payment_fee_rate": 0.03,
        "expected_return_cost": 1,
        "refund_reserve": 1,
        "supplier_allows_dropshipping": True,
        "platform_terms_confirmed": True,
        "return_terms_confirmed": True,
        "cancellation_terms_confirmed": True,
        "cost_evidence": {
            "supplier_cost": {"status": "known"},
            "supplier_shipping": {"status": "known"},
            "platform_fee_rate": {"status": "known"},
            "payment_fee_rate": {"status": "known"},
            "expected_return_cost": {"status": "known"},
            "refund_reserve": {"status": "known"},
        },
    }


def test_v64_unknown_shipping_blocks_cost_completeness():
    candidate = _complete_candidate()
    candidate["supplier_shipping"] = 0
    candidate["cost_evidence"]["supplier_shipping"] = {"status": "unknown"}
    result = assess_cost_completeness(candidate)
    assert result["passed"] is False
    assert "supplier_shipping" in result["unknown_fields"]
    assert result["economics_reliable_for_promotion"] is False
    assert result["live_execution_allowed"] is False


def test_v64_explicit_zero_cost_can_be_known():
    candidate = _complete_candidate()
    candidate["supplier_shipping"] = 0
    candidate["cost_evidence"]["supplier_shipping"] = {
        "status": "known",
        "source": "confirmed-free-shipping",
    }
    result = assess_cost_completeness(candidate)
    assert result["passed"] is True


def test_v64_terms_require_returns_and_cancellation():
    candidate = _complete_candidate()
    candidate["return_terms_confirmed"] = False
    result = assess_terms_evidence(candidate)
    assert result["passed"] is False
    assert "return_terms" in result["missing_fields"]


def test_cj_product_marks_placeholder_shipping_unknown():
    row = normalize_cj_product({
        "id": "cj-1",
        "nameEn": "CJ Product",
        "nowPrice": 4.5,
        "totalVerifiedInventory": 12,
    })
    assert row["supplier_shipping"] == 0.0
    assert row["cost_evidence"]["supplier_cost"]["status"] == "known"
    assert row["cost_evidence"]["supplier_shipping"]["status"] == "unknown"
    assert row["terms_evidence"]["return_terms"]["status"] == "unknown"


def test_v64_proof_blocks_incomplete_real_candidate():
    proof = build_v64_proof()
    assert proof["passed"] is True
    assert proof["complete_case"]["human_gate_ready_count"] == 1
    assert proof["incomplete_case"]["human_gate_ready_count"] == 0
    gate = proof["incomplete_case"]["v64_promotion_gates"][0]
    assert "supplier_shipping" in gate["cost_completeness"]["unknown_fields"]


def test_v64_acceptance_and_release():
    acceptance = build_v64_acceptance()
    status = build_v64_release_status()
    assert acceptance["passed"] is True
    assert status["status"] == "cost_completeness_endpoint_reached"
    assert status["live_execution_allowed"] is False


def test_flask_v64_endpoints_smoke():
    from app import app

    client = app.test_client()
    proof = client.get("/dropship/v6.4/proof")
    acceptance = client.get("/dropship/v6.4/acceptance")
    status = client.get("/dropship/v6.4/status")
    incomplete = client.post("/dropship/v6.4/cost-completeness", json={
        "candidate": {
            "supplier_cost": 10,
            "supplier_shipping": 0,
            "cost_evidence": {
                "supplier_cost": {"status": "known"},
                "supplier_shipping": {"status": "unknown"},
            },
        }
    })

    assert proof.status_code == 200
    assert acceptance.status_code == 200
    assert status.status_code == 200
    assert incomplete.status_code == 200
    assert proof.get_json()["passed"] is True
    assert acceptance.get_json()["passed"] is True
    assert status.get_json()["status"] == "cost_completeness_endpoint_reached"
    assert incomplete.get_json()["passed"] is False


class _ConflictResponse:
    ok = False
    status_code = 409

    def json(self):
        return {"code": "23505", "message": "duplicate key value violates unique constraint"}


class _ConflictSession:
    def post(self, *args, **kwargs):
        return _ConflictResponse()


def test_supabase_unique_conflict_is_classified_as_duplicate():
    client = SupabaseRestClient(
        url="https://example.supabase.co",
        key="server-secret-placeholder",
        session=_ConflictSession(),
    )
    result = persist_observations(client, [{
        "product_key": "dup",
        "supplier": "proof",
        "source": "proof",
        "observed_at": "2026-10-12T14:00:00+00:00",
        "supplier_cost": 1,
        "sale_price": 2,
        "inventory_confirmed": True,
    }])
    assert result["inserted_count"] == 0
    assert result["duplicate_count"] == 1
    assert result["error_count"] == 0
