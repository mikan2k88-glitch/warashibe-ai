"""Opt-in routing of the existing selected P2 candidate to hypothetical storage."""
from research_lab.shadow_validation import create_shadow_candidate


def route_selected_to_shadow(result, *, repository, assessment, as_of):
    selected = result.get("best_candidate")
    if selected is None:
        return {"status": "no_candidate_selected", "shadow_candidate_id": None,
                "external_execution_authorized": False, "human_gate_required": True}
    shadow = create_shadow_candidate(selected, assessment, repository=repository, as_of=as_of)
    return {"status": "shadow_candidate", "shadow_candidate_id": shadow["shadow_candidate_id"],
            "promotion_ready": False, "human_review_ready": False,
            "external_execution_authorized": False, "purchase_authorized": False,
            "human_gate_required": True}
