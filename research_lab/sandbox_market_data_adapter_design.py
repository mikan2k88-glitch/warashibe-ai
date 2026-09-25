"""Design a normalized market-data adapter for Warashibe AI sandbox use.

The adapter accepts already-fetched fixture/provider records and converts them
into the real-world candidate schema. It performs no network access itself.
"""

SANDBOX_MARKET_DATA_ADAPTER_VERSION = "0.1"

SUPPORTED_PROVIDER_CLASSES = (
    "official_api",
    "official_feed",
    "public_web",
    "manual_import",
    "third_party_aggregator",
)

REQUIRED_SOURCE_FIELDS = (
    "provider",
    "provider_class",
    "item_id",
    "title",
    "price_jpy",
)

OPTIONAL_SOURCE_FIELDS = (
    "estimated_sale_price_jpy",
    "estimated_fees_jpy",
    "estimated_shipping_jpy",
    "estimated_days_to_sell",
    "liquidation_value_jpy",
    "market_depth",
    "automation_ease",
    "confidence",
)


def normalize_market_record(record):
    if not isinstance(record, dict):
        return {
            "valid": False,
            "errors": ("record_not_mapping",),
            "candidate": None,
        }

    errors = []
    for field in REQUIRED_SOURCE_FIELDS:
        if field not in record:
            errors.append(f"missing_{field}")

    provider_class = record.get("provider_class")
    if provider_class not in SUPPORTED_PROVIDER_CLASSES:
        errors.append("unsupported_provider_class")

    price = record.get("price_jpy")
    if not isinstance(price, int) or isinstance(price, bool) or price <= 0:
        errors.append("invalid_price_jpy")

    if errors:
        return {
            "valid": False,
            "errors": tuple(errors),
            "candidate": None,
        }

    candidate = {
        "provider": record["provider"],
        "provider_class": provider_class,
        "item_id": record["item_id"],
        "title": record["title"],
        "purchase_price_jpy": price,
        "estimated_sale_price_jpy": record.get("estimated_sale_price_jpy", price),
        "estimated_fees_jpy": record.get("estimated_fees_jpy", 0),
        "estimated_shipping_jpy": record.get("estimated_shipping_jpy", 0),
        "estimated_days_to_sell": record.get("estimated_days_to_sell", 30),
        "liquidation_value_jpy": record.get("liquidation_value_jpy", 0),
        "market_depth": record.get("market_depth", 0.0),
        "automation_ease": record.get("automation_ease", 0.0),
        "confidence": record.get("confidence", 0.0),
        "source_url": record.get("source_url"),
        "source_timestamp": record.get("source_timestamp"),
    }

    return {
        "valid": True,
        "errors": (),
        "candidate": candidate,
        "network_execution_authorized": False,
        "commerce_authorized": False,
    }


def build_market_data_batch(records):
    normalized = []
    rejected = []

    for record in records or ():
        result = normalize_market_record(record)
        if result.get("valid"):
            normalized.append(result["candidate"])
        else:
            rejected.append({
                "record": record,
                "errors": result.get("errors", ()),
            })

    return {
        "version": SANDBOX_MARKET_DATA_ADAPTER_VERSION,
        "mode": "offline_normalization",
        "normalized": tuple(normalized),
        "rejected": tuple(rejected),
        "normalized_count": len(normalized),
        "rejected_count": len(rejected),
        "network_execution_authorized": False,
        "secret_access_authorized": False,
        "commerce_authorized": False,
        "external_action_authorized": False,
    }


def build_sandbox_market_data_adapter_design():
    return {
        "version": SANDBOX_MARKET_DATA_ADAPTER_VERSION,
        "mode": "design_only",
        "supported_provider_classes": SUPPORTED_PROVIDER_CLASSES,
        "required_source_fields": REQUIRED_SOURCE_FIELDS,
        "optional_source_fields": OPTIONAL_SOURCE_FIELDS,
        "network_default": "deny",
        "requires_terms_review_for_automated_collection": True,
        "requires_provider_capability_check": True,
        "requires_source_timestamp": True,
        "requires_sanitized_observability": True,
        "network_execution_authorized": False,
        "secret_access_authorized": False,
        "purchase_authorized": False,
        "listing_authorized": False,
        "payment_authorized": False,
        "commerce_authorized": False,
        "external_action_authorized": False,
        "flow": (
            "receive_fixture_or_provider_record",
            "validate_provider_class",
            "validate_required_fields",
            "normalize_candidate_schema",
            "attach_source_metadata",
            "return_to_sandbox_pipeline",
        ),
    }


def validate_sandbox_market_data_adapter_design():
    design = build_sandbox_market_data_adapter_design()
    assert design["mode"] == "design_only"
    assert design["network_default"] == "deny"
    assert design["requires_terms_review_for_automated_collection"] is True
    assert design["requires_provider_capability_check"] is True
    assert design["network_execution_authorized"] is False
    assert design["secret_access_authorized"] is False
    assert design["commerce_authorized"] is False
    assert design["external_action_authorized"] is False
    return True
