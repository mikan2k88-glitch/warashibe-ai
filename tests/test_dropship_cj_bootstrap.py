from datetime import datetime, timezone

from dropship.cj_only_collector import run_cj_supplier_collection


class FakeSupplier:
    provider_name = "cjdropshipping-list-v2"

    def fetch_offers(self):
        return [{
            "product_key": "cj-1",
            "name": "CJ Product",
            "supplier": "CJdropshipping",
            "source": "cjdropshipping-list-v2",
            "supplier_cost": 4.5,
            "sale_price": 0.0,
            "supplier_shipping": 0.0,
            "delivery_days": 7,
            "inventory_confirmed": True,
            "metadata": {"currency": "USD"},
        }]


class MemoryPersistence:
    def __init__(self):
        self.rows = {}
        self.last = None

    def insert(self, table, row):
        fp = row["observation_fingerprint"]
        if fp in self.rows:
            raise RuntimeError("duplicate 23505")
        self.rows[fp] = dict(row)
        self.last = dict(row)
        return dict(row)


def test_cj_supplier_collection_is_read_only_and_not_promotable():
    db = MemoryPersistence()
    result = run_cj_supplier_collection(
        FakeSupplier(),
        persistence_client=db,
        observed_at=datetime(2026, 10, 12, 13, 15, tzinfo=timezone.utc),
    )
    assert result["status"] == "collecting_cj_supplier_evidence"
    assert result["inserted_count"] == 1
    assert result["market_evidence_available"] is False
    assert result["promotion_review_enabled"] is False
    assert result["human_gate_candidate_ready"] is False
    assert result["commerce_external_writes"] is False
    assert result["live_execution_allowed"] is False
    observation = db.last["observation"]
    assert observation["source"] == "cj-supplier-shadow"
    assert observation["promotion_eligible"] is False
    assert observation["market_evidence_available"] is False


def test_cj_supplier_collection_deduplicates_within_hour():
    db = MemoryPersistence()
    t1 = datetime(2026, 10, 12, 13, 5, tzinfo=timezone.utc)
    t2 = datetime(2026, 10, 12, 13, 55, tzinfo=timezone.utc)
    first = run_cj_supplier_collection(FakeSupplier(), persistence_client=db, observed_at=t1)
    second = run_cj_supplier_collection(FakeSupplier(), persistence_client=db, observed_at=t2)
    assert first["inserted_count"] == 1
    assert second["inserted_count"] == 0
    assert second["duplicate_count"] == 1


def test_cj_supplier_collection_allows_next_hour_snapshot():
    db = MemoryPersistence()
    first = run_cj_supplier_collection(
        FakeSupplier(),
        persistence_client=db,
        observed_at=datetime(2026, 10, 12, 13, 5, tzinfo=timezone.utc),
    )
    second = run_cj_supplier_collection(
        FakeSupplier(),
        persistence_client=db,
        observed_at=datetime(2026, 10, 12, 14, 5, tzinfo=timezone.utc),
    )
    assert first["inserted_count"] == 1
    assert second["inserted_count"] == 1
    assert len(db.rows) == 2


def test_cj_supplier_collection_requires_persistence():
    result = run_cj_supplier_collection(
        FakeSupplier(),
        persistence_client=None,
    )
    assert result["status"] == "setup_required"
    assert result["live_execution_allowed"] is False
