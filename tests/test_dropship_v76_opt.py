from dropship.v70_research_orchestrator import research_v70

class Supplier:
    def fetch_offers(self):
        return [{"product_key":"one","name":"USB Organizer","supplier_cost":3,"cost_evidence":{"supplier_cost":{"status":"known"}}},
                {"product_key":"two","name":" usb   organizer ","supplier_cost":4,"cost_evidence":{"supplier_cost":{"status":"known"}}}]

class Market:
    def __init__(self): self.calls=0
    def search(self, name):
        self.calls += 1
        return [{"price":8,"currency":"USD"},{"price":20,"currency":"USD"},{"price":float("inf"),"currency":"USD"},
                {"price":12,"currency":"USD"},{"price":100,"currency":"JPY"}]

def test_duplicate_query_calls_once_and_uses_true_median():
    market=Market()
    result=research_v70(Supplier(),market,max_market_queries=1)
    assert result["candidate_count"] == 2
    assert market.calls == result["market_search_calls"] == 1
    assert all(c["indicative_ask_median_usd"]==12 for c in result["candidates"])
    assert all(c["market_quote_count"]==3 for c in result["candidates"])
    assert result["human_gate_ready"] is False
    assert result["live_execution_allowed"] is False
def test_zero_query_limit_invalid():
    try:
        research_v70(Supplier(),Market(),max_market_queries=0)
        assert False
    except ValueError:
        pass
