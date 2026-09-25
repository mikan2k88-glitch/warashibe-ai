"""Offline Stripe-style webhook verification boundary for sandbox tests.

This module does not read environment variables or receive network traffic.
It verifies fixture payloads against a caller-supplied secret using HMAC-SHA256
so signature handling can be tested before wiring a real endpoint.
"""

import hashlib
import hmac
import time

SANDBOX_WEBHOOK_VERIFICATION_DESIGN_VERSION = "0.1"
DEFAULT_TOLERANCE_SECONDS = 300


def parse_signature_header(signature_header):
    if not isinstance(signature_header, str) or not signature_header.strip():
        return {"valid": False, "timestamp": None, "signatures": ()}

    timestamp = None
    signatures = []

    for part in signature_header.split(","):
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key == "t":
            try:
                timestamp = int(value)
            except ValueError:
                timestamp = None
        elif key == "v1" and value:
            signatures.append(value)

    return {
        "valid": timestamp is not None and bool(signatures),
        "timestamp": timestamp,
        "signatures": tuple(signatures),
    }


def compute_expected_signature(secret, timestamp, payload):
    if isinstance(payload, str):
        payload = payload.encode("utf-8")
    signed_payload = str(timestamp).encode("ascii") + b"." + payload
    return hmac.new(
        secret.encode("utf-8"),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()


def verify_fixture_signature(
    payload,
    signature_header,
    secret,
    now=None,
    tolerance_seconds=DEFAULT_TOLERANCE_SECONDS,
):
    if not isinstance(secret, str) or not secret:
        return {
            "verified": False,
            "reason": "missing_secret",
            "secret_exposed": False,
        }

    if not isinstance(payload, (bytes, str)):
        return {
            "verified": False,
            "reason": "invalid_payload_type",
            "secret_exposed": False,
        }

    parsed = parse_signature_header(signature_header)
    if not parsed["valid"]:
        return {
            "verified": False,
            "reason": "invalid_signature_header",
            "secret_exposed": False,
        }

    now = int(time.time()) if now is None else int(now)
    if abs(now - parsed["timestamp"]) > tolerance_seconds:
        return {
            "verified": False,
            "reason": "timestamp_outside_tolerance",
            "secret_exposed": False,
        }

    expected = compute_expected_signature(
        secret,
        parsed["timestamp"],
        payload,
    )
    matched = any(
        hmac.compare_digest(expected, candidate)
        for candidate in parsed["signatures"]
    )

    return {
        "verified": matched,
        "reason": "verified" if matched else "signature_mismatch",
        "timestamp": parsed["timestamp"],
        "secret_exposed": False,
    }


def build_sandbox_webhook_verification_design():
    return {
        "version": SANDBOX_WEBHOOK_VERIFICATION_DESIGN_VERSION,
        "mode": "offline_fixture_verification",
        "algorithm": "hmac_sha256",
        "default_tolerance_seconds": DEFAULT_TOLERANCE_SECONDS,
        "raw_payload_required": True,
        "timestamp_check_required": True,
        "constant_time_compare_required": True,
        "caller_supplied_secret_only": True,
        "environment_secret_read_authorized": False,
        "network_endpoint_authorized": False,
        "ledger_write_authorized": False,
        "payment_authorized": False,
        "refund_authorized": False,
        "commerce_authorized": False,
        "external_action_authorized": False,
        "future_live_endpoint_requires_human_gate": True,
        "flow": (
            "receive_raw_fixture_payload",
            "parse_signature_header",
            "check_timestamp_tolerance",
            "compute_hmac_sha256",
            "constant_time_compare",
            "return_verified_event_or_reject",
        ),
    }


def validate_sandbox_webhook_verification_design():
    design = build_sandbox_webhook_verification_design()
    assert design["mode"] == "offline_fixture_verification"
    assert design["raw_payload_required"] is True
    assert design["timestamp_check_required"] is True
    assert design["constant_time_compare_required"] is True
    assert design["environment_secret_read_authorized"] is False
    assert design["network_endpoint_authorized"] is False
    assert design["ledger_write_authorized"] is False
    assert design["commerce_authorized"] is False
    assert design["external_action_authorized"] is False
    assert design["future_live_endpoint_requires_human_gate"] is True
    return True
