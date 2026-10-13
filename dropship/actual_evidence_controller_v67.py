from __future__ import annotations

from .actual_evidence_controller_v66 import run_actual_evidence_controller_v66
from .ebay_account_policy_provider import (
    EbayAccountPolicyProvider,
    assess_ebay_user_oauth_readiness,
)
from .ebay_official_evidence import (
    EbayOfficialFeeEvidenceProvider,
    EbayOfficialTermsEvidenceProvider,
)


def run_actual_evidence_controller_v67(
    supplier_provider,
    market_provider,
    *,
    freight_provider,
    persistence_client,
    provider_handshake: dict,
    available_capital: float = 3000,
    supplier_currency: str = "USD",
    target_currency: str | None = None,
    fx_rates: dict | None = None,
    budget: dict | None = None,
    shadow_thresholds: dict | None = None,
    history_limit: int = 2000,
    run_limit: int = 200,
    destination_country: str = "US",
    quantity: int = 1,
    freight_max_items: int = 1,
    marketplace_id: str = "EBAY_US",
    ebay_user_access_token: str | None = None,
) -> dict:
    user_oauth = assess_ebay_user_oauth_readiness(
        user_token=ebay_user_access_token,
    )
    account_provider = EbayAccountPolicyProvider(
        user_token=ebay_user_access_token,
        marketplace_id=marketplace_id,
    )

    fee_provider = EbayOfficialFeeEvidenceProvider(
        marketplace_id=marketplace_id,
    )
    terms_provider = EbayOfficialTermsEvidenceProvider(
        marketplace_id=marketplace_id,
        account_policy_provider=account_provider,
    )

    base = run_actual_evidence_controller_v66(
        supplier_provider,
        market_provider,
        freight_provider=freight_provider,
        fee_provider=fee_provider,
        terms_provider=terms_provider,
        persistence_client=persistence_client,
        provider_handshake=provider_handshake,
        available_capital=available_capital,
        supplier_currency=supplier_currency,
        target_currency=target_currency,
        fx_rates=fx_rates,
        budget=budget,
        shadow_thresholds=shadow_thresholds,
        history_limit=history_limit,
        run_limit=run_limit,
        destination_country=destination_country,
        quantity=quantity,
        freight_max_items=freight_max_items,
    )

    return {
        **base,
        "controller_version": "6.7",
        "ebay_user_oauth": user_oauth,
        "evidence_scope": {
            "application_oauth_market_read": True,
            "official_payment_fee_policy": True,
            "official_dropshipping_policy": True,
            "official_cancellation_policy": True,
            "seller_return_policy_read": user_oauth["return_policy_read_ready"],
            "platform_final_value_fee_resolved": False,
            "return_cost_model_resolved": False,
            "refund_reserve_model_resolved": False,
        },
        "human_gate_required": True,
        "automatic_execution": False,
        "external_write_enabled": False,
        "live_execution_allowed": False,
    }
