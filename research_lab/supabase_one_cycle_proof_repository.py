"""Supabase append-only repository for PG-035 one-cycle Warashibe proofs."""

TABLE_NAME="warashibe_one_cycle_proofs"

class SupabaseOneCycleProofRepository:
    def __init__(self,client,table=TABLE_NAME):
        if client is None:
            raise ValueError("client is required")
        self.client=client
        self.table=table

    def get(self,proof_key):
        response=(self.client.table(self.table)
                  .select("proof_key,item_key,proof_mode,proof,completed_at")
                  .eq("proof_key",proof_key).limit(1).execute())
        rows=response.data or []
        return dict(rows[0]) if rows else None

    def append(self,proof):
        if not isinstance(proof,dict):
            raise ValueError("proof must be a mapping")
        if proof.get("status")!="one_cycle_warashibe_proved":
            raise ValueError("one_cycle_warashibe_proved required")
        if proof.get("chain_consistent") is not True:
            raise ValueError("consistent chain required")
        if proof.get("warashibe_loop_v2_contract_complete") is not True:
            raise ValueError("Warashibe Loop v2 contract completion required")
        if proof.get("controlled_automation_authorized") is not False:
            raise ValueError("proof must not authorize controlled automation")
        key=proof.get("proof_key")
        if self.get(key) is not None:
            raise ValueError("proof_key already exists")
        response=self.client.table(self.table).insert({
            "proof_key":key,
            "item_key":proof.get("item_key"),
            "proof_mode":proof.get("proof_mode"),
            "proof":dict(proof),
            "completed_at":proof.get("cycle_completed_at"),
        }).execute()
        rows=response.data or []
        if not rows:
            raise RuntimeError("one-cycle proof insert returned no row")
        return dict(rows[0])
