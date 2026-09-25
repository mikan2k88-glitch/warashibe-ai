"""Tests for sandbox webhook verification design."""

from research_lab.sandbox_webhook_verification_design import (
    build_sandbox_webhook_verification_design,
    compute_expected_signature,
    parse_signature_header,
    validate_sandbox_webhook_verification_design,
    verify_fixture_signature,
)


def run_tests():
    assert validate_sandbox_webhook_verification_design() is True

    secret = "whsec_fixture"
    payload = b'{"id":"evt_test_001"}'
    timestamp = 1_700_000_000
    signature = compute_expected_signature(secret, timestamp, payload)
    header = f"t={timestamp},v1={signature}"

    parsed = parse_signature_header(header)
    assert parsed["valid"] is True
    assert parsed["timestamp"] == timestamp
    assert parsed["signatures"] == (signature,)

    verified = verify_fixture_signature(
        payload,
        header,
        secret,
        now=timestamp + 60,
    )
    assert verified["verified"] is True
    assert verified["reason"] == "verified"
    assert verified["secret_exposed"] is False

    bad_signature = verify_fixture_signature(
        payload,
        f"t={timestamp},v1=deadbeef",
        secret,
        now=timestamp,
    )
    assert bad_signature["verified"] is False
    assert bad_signature["reason"] == "signature_mismatch"

    stale = verify_fixture_signature(
        payload,
        header,
        secret,
        now=timestamp + 301,
    )
    assert stale["verified"] is False
    assert stale["reason"] == "timestamp_outside_tolerance"

    design = build_sandbox_webhook_verification_design()
    assert design["environment_secret_read_authorized"] is False
    assert design["network_endpoint_authorized"] is False
    assert design["ledger_write_authorized"] is False
    assert design["future_live_endpoint_requires_human_gate"] is True


if __name__ == "__main__":
    run_tests()
    print("sandbox webhook verification design tests passed")
