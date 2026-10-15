from app import app
from dropship.v70_research_orchestrator import research_v70

class Supplier:
    def fetch_offers(self):
        return [{"name": "organizer", "product_key": "CJ1", "supplier_cost": 4.0,
                 "cost_evidence": {"supplier_cost": {"status": "known"}}}]

class Market:
    def search(self, query):
        return [{"price": 18.0, "currency": "USD"}, {"price": 20.0, "currency": "USD"}]

def test_read_only_actual_adapter_and_unknown_costs():
    result = research_v70(Supplier(), Market(), capital_usd=20)
    assert result["candidate_count"] == 1
    item = result["proposed_single_candidate"]
    assert item["indicative_ask_median_usd"] == 20
    assert "supplier_shipping_usd" in item["unknown_fields"]
    assert "sale_total_usd" in item["unknown_fields"]
    assert item["assessment"]["evaluation"]["profit_usd"] is None
    assert result["human_gate_ready"] is False
    assert result["live_execution_allowed"] is False

def test_limits_and_zero_cost_cannot_pass():
    class BadSupplier:
        def fetch_offers(self):
            return [{"name": "unsafe", "product_key": "CJ2",
                     "supplier_cost": 0, "cost_evidence": {"supplier_cost": {"status": "known"}}}]
    result = research_v70(BadSupplier(), Market())
    assert "supplier_cost_usd" in result["proposed_single_candidate"]["unknown_fields"]
    try:
        research_v70(Supplier(), Market(), max_candidates=1000)
        assert False
    except ValueError:
        pass

def test_status_is_safe():
    with app.test_client() as client:
        result = client.get("/dropship/v7.0/status")
        assert result.status_code == 200
        assert result.json["actual_data_acceptance"] == "pending"
        assert result.json["live_execution_allowed"] is False
