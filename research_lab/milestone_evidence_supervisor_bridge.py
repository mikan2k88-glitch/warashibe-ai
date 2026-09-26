"""Bridge verified CI evidence to the existing bounded milestone supervisor.

Pure LAB projection; a green CI is evidence, not automatic human approval.
"""

from research_lab.milestone_evidence_contract import evaluate_milestone_evidence
from research_lab.autonomous_research_orchestrator_milestone_supervisor import supervise_milestone


def review_milestone(*, milestone_id, experiment_id, expected_sha, ci,
                     current_stage, milestone_stage, cycles_completed=0):
    evidence = evaluate_milestone_evidence(
        milestone_id=milestone_id, experiment_id=experiment_id,
        expected_sha=expected_sha, ci=ci,
    )
    supervisor = supervise_milestone(
        "select_small_next_theme", current_stage, milestone_stage,
        cycles_completed=cycles_completed,
        ci_status="success" if evidence["verified"] else "unverified",
    )
    return {
        "evidence": evidence,
        "supervision": supervisor,
        "completion_candidate": evidence["verified"] and supervisor["milestone_reached"],
        "human_approval_recorded": False,
        "db_record_type": "milestone_review",
        "db_write_performed": False,
        "external_action_authorized": False,
    }


def validate_milestone_evidence_supervisor_bridge():
    sha = "example-sha"
    ci = {
        "head_sha": sha, "status": "completed", "conclusion": "success",
        "html_url": "https://github.com/example/repo/actions/runs/1",
    }
    args = dict(milestone_id="one_item_explanation", experiment_id="offline-v1",
                expected_sha=sha, current_stage="verified", milestone_stage="verified")
    good = review_milestone(**args, ci=ci)
    assert good["completion_candidate"] and good["supervision"]["milestone_reached"]
    assert not good["human_approval_recorded"] and not good["db_write_performed"]
    bad = review_milestone(**args, ci=dict(ci, head_sha="other"))
    assert not bad["completion_candidate"] and not bad["supervision"]["continue_research"]
    pending = review_milestone(**dict(args, current_stage="pending"), ci=ci)
    assert not pending["completion_candidate"] and pending["supervision"]["continue_research"]
    return True


if __name__ == "__main__":
    assert validate_milestone_evidence_supervisor_bridge()
    print("PASS: evidence-to-supervisor bridge")
