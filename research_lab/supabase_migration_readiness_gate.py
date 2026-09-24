"""Human-approval gate for any future Supabase migration.

This module never executes SQL. Passing technical validation is necessary but
never sufficient: explicit human approval is also required before a caller may
consider a real migration eligible for execution.
"""

from research_lab.supabase_schema_dry_run_validation import validate_schema_dry_run

READINESS_GATE_VERSION = "0.1"


def migration_readiness(*, human_approved=False):
    dry_run = validate_schema_dry_run()
    technically_ready = dry_run["valid"] is True

    return {
        "technically_ready": technically_ready,
        "human_approved": human_approved is True,
        "execution_allowed": technically_ready and human_approved is True,
        "writes_enabled": False,
        "sql_executed": False,
    }


def require_migration_approval(*, human_approved=False):
    status = migration_readiness(human_approved=human_approved)
    if not status["execution_allowed"]:
        raise PermissionError("Supabase migration requires explicit human approval")
    return status
