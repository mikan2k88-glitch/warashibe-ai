from dropship.v70_research_orchestrator import research_v70

class Supplier:
    def fetch_offers(self):
        return [{"name":"organizer","product_key":"p1","supplier_cost":4.0,
                 "cost_evidence":{"supplier_cost":{"status":"known"}}}]

class Market:
    def search(self,name):
        return [{"price":18,"currency":"USD"}]

class Freight:
    def fetch_shipping_evidence(self,candidate,*,destination_country,quantity):
        assert destination_country == "US" and quantity == 1
        return {"status":"known","shipping_cost":2.06,"currency":"USD",
                "variant_id":"vid1","destination_country":"US",
                "source":"cj-freight-calculate"}

class NoFreight:
    def fetch_shipping_evidence(self,candidate,*,destination_country,quantity):
        return {"status":"unknown","reason":"variant_not_found","source":"cj-freight-calculate"}

def test_verified_cj_freight_enters_research_evidence():
    result=research_v70(Supplier(),Market(),freight_provider=Freight())
    item=result["proposed_single_candidate"]
    assert result["freight_quote_attempts"]==1
    assert "supplier_shipping_usd" not in item["unknown_fields"]
    assert "sale_total_usd" in item["unknown_fields"]
    assert item["assessment"]["evaluation"]["profit_usd"] is None
    assert result["live_execution_allowed"] is False

def test_unavailable_freight_remains_unknown():
    result=research_v70(Supplier(),Market(),freight_provider=NoFreight())
    assert "supplier_shipping_usd" in result["proposed_single_candidate"]["unknown_fields"]

def test_freight_limit_zero_disables_queries():
    result=research_v70(Supplier(),Market(),freight_provider=Freight(),max_freight_quotes=0)
    assert result["freight_quote_attempts"] == 0
    assert "supplier_shipping_usd" in result["proposed_single_candidate"]["unknown_fields"]
