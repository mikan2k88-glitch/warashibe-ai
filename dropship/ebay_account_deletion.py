from __future__ import annotations

import hashlib
import os


DEFAULT_ENDPOINT = (
    "https://warashibe-ai.onrender.com"
    "/dropship/ebay/marketplace-account-deletion"
)


def build_challenge_response(
    challenge_code: str,
    *,
    verification_token: str | None = None,
    endpoint: str | None = None,
) -> dict:
    challenge = str(challenge_code or "")
    token = verification_token or os.environ.get(
        "EBAY_MARKETPLACE_DELETION_VERIFICATION_TOKEN",
        "",
    )
    callback = endpoint or os.environ.get(
        "EBAY_MARKETPLACE_DELETION_ENDPOINT",
        DEFAULT_ENDPOINT,
    )

    if not challenge:
        raise ValueError("challenge_code is required")
    if not token:
        raise RuntimeError("verification token is not configured")

    digest = hashlib.sha256(
        f"{challenge}{token}{callback}".encode("utf-8")
    ).hexdigest()

    return {
        "challengeResponse": digest,
    }


def acknowledge_deletion_notification(payload: dict | None) -> dict:
    data = payload if isinstance(payload, dict) else {}
    metadata = data.get("metadata") or {}
    notification = data.get("notification") or {}
    notification_data = notification.get("data") or {}

    return {
        "status": "acknowledged",
        "topic": metadata.get("topic"),
        "notification_id_present": bool(notification.get("notificationId")),
        "user_identifier_present": any(
            bool(notification_data.get(key))
            for key in ("username", "userId", "eiasToken")
        ),
        "payload_persisted": False,
        "user_data_persisted_by_current_pipeline": False,
        "commerce_external_writes": False,
        "live_execution_allowed": False,
    }
