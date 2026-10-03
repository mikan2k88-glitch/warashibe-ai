"""Supabase append-only repository for PG-036 live pilot reviews."""

TABLE_NAME="warashibe_live_pilot_reviews"

class SupabaseLivePilotReviewRepository:
    def __init__(self,client,table=TABLE_NAME):
        if client is None:
            raise ValueError("client is required")
        self.client=client
        self.table=table

    def get(self,review_key):
        response=(self.client.table(self.table)
                  .select("review_key,proof_key,item_key,review_mode,review,reviewed_at")
                  .eq("review_key",review_key).limit(1).execute())
        rows=response.data or []
        return dict(rows[0]) if rows else None

    def append(self,review):
        if not isinstance(review,dict):
            raise ValueError("review must be a mapping")
        if review.get("status")!="live_pilot_review_complete":
            raise ValueError("live_pilot_review_complete required")
        if review.get("learning_loop_feedback_ready") is not True:
            raise ValueError("learning loop feedback must be ready")
        if review.get("eligible_for_controlled_automation") is not False:
            raise ValueError("review must not auto-enable controlled automation")
        if review.get("controlled_automation_authorized") is not False:
            raise ValueError("controlled automation must remain unauthorized")
        key=review.get("review_key")
        if self.get(key) is not None:
            raise ValueError("review_key already exists")
        response=self.client.table(self.table).insert({
            "review_key":key,
            "proof_key":review.get("proof_key"),
            "item_key":review.get("item_key"),
            "review_mode":review.get("review_mode"),
            "review":dict(review),
            "reviewed_at":review.get("reviewed_at"),
        }).execute()
        rows=response.data or []
        if not rows:
            raise RuntimeError("live pilot review insert returned no row")
        return dict(rows[0])
