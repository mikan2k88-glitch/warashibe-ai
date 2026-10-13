"""eBay User OAuth: read-only authorization and one-shot seller return-policy evidence.

Requires EBAY_CLIENT_ID, EBAY_CLIENT_SECRET, EBAY_OAUTH_RUNAME and
FLASK_SECRET_KEY. Configure the eBay RuName to redirect to this callback.
No OAuth token is written to logs, database, cookies or responses.
"""
from __future__ import annotations

import os
import secrets

import requests
from flask import Blueprint, jsonify, redirect, request, session

from .ebay_account_policy_provider import EbayAccountPolicyProvider, SELL_ACCOUNT_READONLY_SCOPE

oauth_bp = Blueprint("dropship_ebay_oauth", __name__, url_prefix="/dropship/ebay/oauth")
AUTH_URL = "https://auth.ebay.com/oauth2/authorize"
TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"


def oauth_config():
    keys = ("EBAY_CLIENT_ID", "EBAY_CLIENT_SECRET", "EBAY_OAUTH_RUNAME", "FLASK_SECRET_KEY")
    missing = [key for key in keys if not os.getenv(key)]
    return {
        "status": "setup_required" if missing else "ready",
        "missing_env": missing,
        "scope": SELL_ACCOUNT_READONLY_SCOPE,
        "callback_path": "/dropship/ebay/oauth/callback",
        "mode": "read_only",
        "human_gate_required": True,
        "live_execution_allowed": False,
    }


@oauth_bp.get("/status")
def status():
    return jsonify(oauth_config())


@oauth_bp.get("/start")
def start():
    config = oauth_config()
    if config["status"] != "ready":
        return jsonify(config), 503
    from urllib.parse import urlencode
    # Flask's signed session contains only short-lived CSRF state, never tokens.
    state = secrets.token_urlsafe(32)
    session["ebay_oauth_state"] = state
    session.permanent = False
    query = urlencode({
        "client_id": os.environ["EBAY_CLIENT_ID"],
        "redirect_uri": os.environ["EBAY_OAUTH_RUNAME"],
        "response_type": "code",
        "scope": SELL_ACCOUNT_READONLY_SCOPE,
        "state": state,
        "prompt": "login",
    })
    response = redirect(AUTH_URL + "?" + query)
    response.headers["Cache-Control"] = "no-store"
    return response


@oauth_bp.get("/callback")
def callback():
    expected = session.pop("ebay_oauth_state", None)
    actual = request.args.get("state", "")
    if not expected or not actual or not secrets.compare_digest(expected, actual):
        return jsonify({"status": "blocked", "reason": "invalid_oauth_state",
                        "live_execution_allowed": False}), 400
    if request.args.get("error"):
        return jsonify({"status": "blocked", "reason": "authorization_denied",
                        "live_execution_allowed": False}), 400
    code = request.args.get("code", "")
    if not code:
        return jsonify({"status": "blocked", "reason": "missing_code",
                        "live_execution_allowed": False}), 400
    if oauth_config()["status"] != "ready":
        return jsonify(oauth_config()), 503
    try:
        response = requests.post(
            TOKEN_URL,
            auth=(os.environ["EBAY_CLIENT_ID"], os.environ["EBAY_CLIENT_SECRET"]),
            data={"grant_type": "authorization_code", "code": code,
                  "redirect_uri": os.environ["EBAY_OAUTH_RUNAME"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=20,
        )
        response.raise_for_status()
        token = response.json().get("access_token")
        if not token:
            raise ValueError("empty_access_token")
        evidence = EbayAccountPolicyProvider(user_token=token).fetch_return_policy_evidence()
        return jsonify({
            "status": "evidence_retrieved" if evidence["status"] == "known" else "evidence_unknown",
            "return_policy_evidence": evidence,
            "token_persisted": False,
            "human_gate_required": True,
            "live_execution_allowed": False,
        }), 200
    except (requests.RequestException, ValueError):
        return jsonify({"status": "blocked", "reason": "oauth_exchange_failed",
                        "live_execution_allowed": False}), 502
