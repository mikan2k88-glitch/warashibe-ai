"""Supabase append-only repository for PG-024 Live-readiness Audits."""

TABLE_NAME = "warashibe_live_readiness_audits"


class SupabaseLiveReadinessAuditRepository:
    def __init__(self, client, table=TABLE_NAME):
        if client is None:
            raise ValueError("client is required")
        self.client = client
        self.table = table

    @staticmethod
    def _validate(audit):
        if not isinstance(audit, dict):
            raise ValueError("audit must be a mapping")
        required=("audit_key","auditor_id","audited_at","audit")
        missing=[key for key in required if key not in audit]
        if missing:
            raise ValueError("audit missing required keys: "+",".join(missing))
        payload=audit["audit"]
        if not isinstance(payload, dict) or payload.get("status")!="live_readiness_audit_complete":
            raise ValueError("live_readiness_audit_complete required")
        if payload.get("human_go_no_go_required") is not True:
            raise ValueError("human go/no-go must remain required")
        if payload.get("live_commerce_authorized") is not False:
            raise ValueError("live commerce must remain unauthorized")
        for key in ("commerce_authorized","external_action_authorized","purchase_authorized","payment_authorized","sale_authorized"):
            if payload.get(key) is not False:
                raise ValueError(f"{key} must remain false")
        return audit

    def get(self,audit_key):
        if not isinstance(audit_key,str) or not audit_key.strip():
            raise ValueError("audit_key must be a non-empty string")
        response=(self.client.table(self.table)
                  .select("audit_key,auditor_id,audited_at,audit")
                  .eq("audit_key",audit_key.strip()).limit(1).execute())
        rows=response.data or []
        return dict(rows[0]) if rows else None

    def append(self,audit):
        audit=self._validate(audit)
        key=audit["audit_key"].strip()
        if self.get(key) is not None:
            raise ValueError("audit_key already exists")
        payload={
            "audit_key":key,
            "auditor_id":audit["auditor_id"],
            "audited_at":audit["audited_at"],
            "audit":dict(audit["audit"]),
        }
        response=self.client.table(self.table).insert(payload).execute()
        rows=response.data or []
        if not rows:
            raise RuntimeError("live-readiness audit insert returned no row")
        return dict(rows[0])
