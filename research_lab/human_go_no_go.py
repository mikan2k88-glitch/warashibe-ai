"""PG-025 Human Go/No-Go Decision.

Records the human decision after PG-024. GO permits only the next design stage;
it does not authorize live commerce or execution.
"""

from datetime import datetime, timezone

DECISION_VERSION="0.1"


def _text(value,name,max_length=500):
    if not isinstance(value,str) or not value.strip():
        raise ValueError(f"{name} is required")
    value=value.strip()
    if len(value)>max_length:
        raise ValueError(f"{name} is too long")
    return value


def _utc(value,name):
    value=_text(value,name,80)
    text=value[:-1]+"+00:00" if value.endswith("Z") else value
    dt=datetime.fromisoformat(text)
    if dt.tzinfo is None:
        raise ValueError(f"{name} must include timezone")
    return dt.astimezone(timezone.utc)


def _money(value,name):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or value<0:
        raise ValueError(f"{name} must be a non-negative number")
    return int(round(value))


def build_human_go_no_go_decision(
    audit, *, decision_key, decision, decided_at, reviewer_id, reason,
    approved_budget_jpy, max_transactions, approved_providers, valid_until,
):
    if not isinstance(audit,dict):
        raise ValueError("audit must be a dictionary")
    if audit.get("status")!="live_readiness_audit_complete":
        raise ValueError("live_readiness_audit_complete required")
    if audit.get("ready_for_human_go_no_go") is not True:
        raise ValueError("audit must be ready_for_human_go_no_go")
    if audit.get("human_go_no_go_required") is not True:
        raise ValueError("human go/no-go requirement missing")
    if audit.get("live_commerce_authorized") is not False:
        raise ValueError("live commerce must remain unauthorized")

    decision=str(decision or "").strip().lower()
    if decision not in {"go","no_go"}:
        raise ValueError("decision must be go or no_go")

    decided=_utc(decided_at,"decided_at")
    expires=_utc(valid_until,"valid_until")
    if expires<=decided:
        raise ValueError("valid_until must be after decided_at")

    budget=_money(approved_budget_jpy,"approved_budget_jpy")
    if isinstance(max_transactions,bool) or not isinstance(max_transactions,int) or max_transactions<0:
        raise ValueError("max_transactions must be a non-negative integer")
    if not isinstance(approved_providers,list) or any(not isinstance(x,str) or not x.strip() for x in approved_providers):
        raise ValueError("approved_providers must be a list of provider names")

    if decision=="go":
        if budget<=0:
            raise ValueError("GO requires positive approved budget")
        if max_transactions!=1:
            raise ValueError("GO pilot is limited to exactly one transaction")
        if not approved_providers:
            raise ValueError("GO requires at least one approved provider")
    else:
        budget=0
        max_transactions=0
        approved_providers=[]

    return {
        "version":DECISION_VERSION,
        "status":"human_go_no_go_recorded",
        "decision_key":_text(decision_key,"decision_key",200),
        "source_audit_key":audit.get("audit_key"),
        "decision":decision,
        "decided_at":decided.isoformat(),
        "valid_until":expires.isoformat(),
        "reviewer_id":_text(reviewer_id,"reviewer_id",100),
        "reason":_text(reason,"reason",1000),
        "pilot_scope":{
            "approved_budget_jpy":budget,
            "max_transactions":max_transactions,
            "quantity_per_transaction":1,
            "parallel_positions_allowed":False,
            "approved_providers":[x.strip() for x in approved_providers],
        },
        "human_final_buy_required":True,
        "live_execution_authorized":False,
        "execution_triggered":False,
        "commerce_authorized":False,
        "external_action_authorized":False,
        "purchase_authorized":False,
        "payment_authorized":False,
        "sale_authorized":False,
    }
