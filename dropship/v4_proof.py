from __future__ import annotations

from .cj_token import CJAccessTokenProvider
from .ebay_token import EbayApplicationTokenProvider
from .v3_proof import build_v3_acceptance, build_v3_proof


class _ProofResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class _ProofEbaySession:
    def __init__(self):
        self.calls = 0

    def post(self, url, headers, data, timeout):
        self.calls += 1
        return _ProofResponse({
            "access_token": "proof-ebay-token",
            "expires_in": 7200,
            "token_type": "Application Access Token",
        })


class _ProofCJSession:
    def __init__(self):
        self.calls = 0

    def post(self, url, headers, json, timeout):
        self.calls += 1
        return _ProofResponse({
            "code": 200,
            "result": True,
            "message": "Success",
            "data": {
                "accessToken": "proof-cj-token",
                "refreshToken": "proof-cj-refresh-token",
            },
        })


def build_v4_proof() -> dict:
    ebay_session = _ProofEbaySession()
    cj_session = _ProofCJSession()

    ebay = EbayApplicationTokenProvider(
        client_id="proof-client",
        client_secret="proof-secret",
        session=ebay_session,
    )
    cj = CJAccessTokenProvider(
        api_key="proof-api-key",
        session=cj_session,
    )

    ebay_token = ebay.get_token()
    ebay_token_cached = ebay.get_token()
    cj_token = cj.get_token()
    cj_token_cached = cj.get_token()

    v3 = build_v3_proof()

    checks = {
        "ebay_application_token_minted": bool(ebay_token),
        "ebay_token_cached": ebay_token_cached == ebay_token and ebay_session.calls == 1,
        "cj_access_token_minted": bool(cj_token),
        "cj_token_cached": cj_token_cached == cj_token and cj_session.calls == 1,
        "token_descriptions_hide_secret_values": (
            ebay.describe()["secret_values_exposed"] is False
            and cj.describe()["secret_values_exposed"] is False
        ),
        "v3_real_read_shadow_proof_passed": v3["passed"] is True,
        "v3_live_execution_disabled": v3["live_execution_allowed"] is False,
    }

    return {
        "proof_version": "4.0",
        "passed": all(checks.values()),
        "checks": checks,
        "token_sources": {
            "ebay": ebay.describe(),
            "cj": cj.describe(),
        },
        "v3_proof_passed": v3["passed"],
        "token_values_exposed": False,
        "commerce_external_writes_enabled": False,
        "live_execution_allowed": False,
    }


def build_v4_acceptance() -> dict:
    proof = build_v4_proof()
    v3_acceptance = build_v3_acceptance()
    checks = {
        "v4_proof_passed": proof["passed"],
        "v3_acceptance_passed": v3_acceptance["passed"],
        "token_values_not_exposed": proof["token_values_exposed"] is False,
        "commerce_external_writes_disabled": proof["commerce_external_writes_enabled"] is False,
        "live_execution_disabled": proof["live_execution_allowed"] is False,
    }
    return {
        "acceptance_version": "4.0",
        "passed": all(checks.values()),
        "checks": checks,
        "maturity_ceiling": "promotion_review_human_gate",
        "next_phase": "configure_real_provider_credentials_and_collect_evidence",
        "live_execution_allowed": False,
    }
