"""Select an outcome repository without creating credentials or remote resources.

JSON remains the safe default.  Supabase is opt-in and requires an already-created
client to be injected by trusted application code; this module never reads or
constructs credentials itself.
"""

from research_lab.live_outcome_store import OutcomeStore
from research_lab.outcome_repository import validate_repository
from research_lab.supabase_outcome_repository import SupabaseOutcomeRepository


def build_outcome_repository(backend="json", *, path=None, supabase_client=None, table="warashibe_sale_outcomes"):
    name = (backend or "json").strip().lower()
    if name == "json":
        repository = OutcomeStore() if path is None else OutcomeStore(path)
    elif name == "supabase":
        if supabase_client is None:
            raise ValueError("supabase backend requires an injected client")
        repository = SupabaseOutcomeRepository(supabase_client, table=table)
    else:
        raise ValueError(f"unsupported outcome repository backend: {backend}")
    return validate_repository(repository)
