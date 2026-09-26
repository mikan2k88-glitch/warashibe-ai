"""Read-only milestone evidence contract, ready for future DB persistence.

Only an explicitly supplied CI record can prove completion. No network or DB I/O.
"""


def evaluate_milestone_evidence(*, milestone_id, expected_sha, ci, experiment_id):
    if not all(isinstance(x, str) and x.strip() for x in (milestone_id, expected_sha, experiment_id)):
        raise ValueError("missing_milestone_identity")
    if not isinstance(ci, dict):
        ci = {}
    matched = ci.get("head_sha") == expected_sha
    passed = ci.get("status") == "completed" and ci.get("conclusion") == "success"
    url = ci.get("html_url")
    verified = matched and passed and isinstance(url, str) and url.startswith(
        "https://github.com/"
    )
    return {
        "milestone_id": milestone_id,
        "experiment_id": experiment_id,
        "commit_sha": expected_sha,
        "ci_run_url": url if verified else None,
        "ci_status": ci.get("status"),
        "ci_conclusion": ci.get("conclusion"),
        "verified": verified,
        "state": "ci_verified" if verified else "awaiting_matching_successful_ci",
        "db_record_type": "milestone_evidence",
        "db_write_performed": False,
        "external_action_authorized": False,
    }


def validate_milestone_evidence_contract():
    sha = "fcb6b5a6aefb4b7cab757dccadbaef0da5a39c65"
    ci = {
        "head_sha": sha, "status": "completed", "conclusion": "success",
        "html_url": "https://github.com/example/repo/actions/runs/123",
    }
    args = {"milestone_id": "one_item_explanation", "expected_sha": sha,
            "experiment_id": "offline-one-item-v1"}
    good = evaluate_milestone_evidence(**args, ci=ci)
    assert good["verified"] and not good["db_write_performed"]
    assert good["commit_sha"] == sha and good["db_record_type"] == "milestone_evidence"
    assert not evaluate_milestone_evidence(**args, ci=dict(ci, head_sha="other"))["verified"]
    assert not evaluate_milestone_evidence(**args, ci=dict(ci, conclusion="failure"))["verified"]
    assert not evaluate_milestone_evidence(**args, ci=dict(ci, status="in_progress"))["verified"]
    assert not evaluate_milestone_evidence(**args, ci=dict(ci, html_url="invalid"))["verified"]
    assert not evaluate_milestone_evidence(**args, ci=None)["verified"]
    return True


if __name__ == "__main__":
    assert validate_milestone_evidence_contract()
    print("PASS: read-only milestone evidence contract")
