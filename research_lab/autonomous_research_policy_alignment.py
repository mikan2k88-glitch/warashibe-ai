"""Alignment contract for autonomous research operating policy.

This module reconciles reusable code defaults with the stricter live research
cycle policy. The effective policy always chooses the smaller safety limit.
It performs no external action.
"""

from research_lab.autonomous_research_cycle_budget import LIMITS

POLICY_ALIGNMENT_VERSION = "0.1"

LIVE_POLICY_LIMITS = {
    "themes_per_cycle": 1,
    "code_changes_per_cycle": 3,
    "repair_attempts_per_cycle": 1,
}


def effective_limits(code_limits=None, live_limits=None):
    code = dict(LIMITS if code_limits is None else code_limits)
    live = dict(LIVE_POLICY_LIMITS if live_limits is None else live_limits)
    if set(code) != set(live):
        raise ValueError("policy limit keys must match")
    values = {}
    for name in code:
        pair = (code[name], live[name])
        if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in pair):
            raise ValueError("policy limits must be non-negative integers")
        values[name] = min(pair)
    return values


def policy_alignment_report():
    effective = effective_limits()
    mismatches = {
        name: {"code": LIMITS[name], "live": LIVE_POLICY_LIMITS[name], "effective": effective[name]}
        for name in LIMITS
        if LIMITS[name] != LIVE_POLICY_LIMITS[name]
    }
    return {
        "version": POLICY_ALIGNMENT_VERSION,
        "aligned": not mismatches,
        "mismatches": mismatches,
        "effective_limits": effective,
        "external_action_performed": False,
    }


def validate_policy_alignment():
    report = policy_alignment_report()
    assert report["effective_limits"]["repair_attempts_per_cycle"] == 1
    assert report["mismatches"]["repair_attempts_per_cycle"]["code"] == 2
    assert report["mismatches"]["repair_attempts_per_cycle"]["live"] == 1
    assert report["external_action_performed"] is False
    return True
