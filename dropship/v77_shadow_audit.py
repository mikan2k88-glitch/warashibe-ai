"""v7.7 privacy-preserving Shadow observation quality summary."""
from collections import Counter

def summarize_observations(records):
    if not isinstance(records, list) or len(records)>1000:
        raise ValueError("invalid_observation_batch")
    counts=Counter()
    missing=Counter()
    observed_days=set()
    for rec in records:
        if not isinstance(rec,dict):
            raise ValueError("invalid_observation")
        status=rec.get("status")
        if status not in ("observation_captured","no_candidates","setup_required","research_failed"):
            raise ValueError("unknown_status")
        counts[status]+=1
        timestamp=rec.get("observed_at")
        if isinstance(timestamp,str) and len(timestamp)>=10:
            observed_days.add(timestamp[:10])
        for key in rec.get("missing_evidence",[]):
            if isinstance(key,str) and len(key)<100:
                missing[key]+=1
    return {
        "version":"7.7","total_observations":len(records),
        "observation_days":len(observed_days),
        "outcome_counts":dict(counts),
        "missing_evidence_counts":dict(missing),
        "shadow_acceptance":"pending_review",
        "human_gate_ready":False,"live_execution_allowed":False
    }
