from dropship.v70_research_orchestrator import research_v70
class Supplier:
    def fetch_offers(self):
        return [{"product_key":"p1","name":"organizer","supplier_cost":0,
                 "cost_evidence":{"supplier_cost":{"status":"unknown"}}}]
class Market:
    def search(self, query):
        return [{"price":22,"currency":"USD"}]
class Freight:
    def __init__(self, matched=True): self.matched=matched
    def fetch_shipping_evidence(self, candidate, *, destination_country, quantity):
        return {"status":"known","shipping_cost":2.06,"currency":"USD",
                "variant_id":"v1","variant_sell_price":4.25,
                "variant_price_source":"cj-variant-query",
                "destination_country":"US","source":"cj-freight-calculate"}
def test_selected_variant_price_resolves_unknown():
    result=research_v70(Supplier(), Market(), freight_provider=Freight())
    item=result["proposed_single_candidate"]
    assert "supplier_cost_usd" not in item["unknown_fields"]
    assert "supplier_shipping_usd" not in item["unknown_fields"]
    assert "sale_total_usd" in item["unknown_fields"]
    assert item["assessment"]["evaluation"]["profit_usd"] is None
    assert result["live_execution_allowed"] is False
def test_mismatched_variant_cannot_promote_price():
    from dropship.v70_research_orchestrator import research_v70
    class BadFreight(Freight):
        def fetch_shipping_evidence(self, candidate, *, destination_country, quantity):
            result=super().fetch_shipping_evidence(candidate,destination_country=destination_country,quantity=quantity)
            result["variant_id"]="v2"
            result["variant_price_source"]="unknown"
            return result
    result=research_v70(Supplier(), Market(), freight_provider=BadFreight())
    assert "supplier_cost_usd" in result["proposed_single_candidate"]["unknown_fields"]
