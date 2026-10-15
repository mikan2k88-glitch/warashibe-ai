import json
from scripts.dropship_v70_research import sanitized_report

def test_missing_credentials_yield_blocked_evidence():
    report = sanitized_report({"status":"setup_required", "reason":"credentials_missing"})
    assert report["status"] == "setup_required"
    assert report["evidence_ready"] is False
    assert report["human_gate_ready"] is False
    assert report["live_execution_allowed"] is False

class Supplier:
    def fetch_offers(self):
        return [{"product_key":"a", "name":"test organizer", "supplier_cost":4,
                 "cost_evidence":{"supplier_cost":{"status":"known"}}}]
class Market:
    def search(self, name):
        return [{"price":15,"currency":"USD"}]

def test_sanitized_evidence_contains_only_safe_summary():
    report = sanitized_report({"status":"ready","supplier_provider":Supplier(),
                               "market_provider":Market()})
    assert report["status"] == "observation_captured"
    assert "platform_fee" in report["missing_evidence"]
    assert report["evidence_ready"] is False
    assert report["live_execution_allowed"] is False
    assert "supplier_provider" not in json.dumps(report)
