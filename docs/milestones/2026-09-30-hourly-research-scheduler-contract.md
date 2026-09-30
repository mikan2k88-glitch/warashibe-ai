# 2026-09-30 — Hourly Research Scheduler Contract

## Scope
Connect the AI consumer state transition to a bounded hourly research scheduling decision without granting external execution, retry, rollback, or human-gate bypass powers.

## Implemented
- Added `research_lab/hourly_research_scheduler_contract.py`.
- Added `research_lab/test_hourly_research_scheduler_contract.py`.
- Added the scheduler contract test to `.github/workflows/research-lab.yml`.
- Fixed schema version at `1.0`.
- Hour slots must be timezone-aware and exactly aligned to `HH:00:00`.
- Duplicate completed slots are converted to a safe `no_op`.
- `advance_to_next_theme` schedules `run_research_cycle`.
- `repair_current_audit` schedules `prepare_repair_candidate`.
- `hold` and unknown/invalid inputs schedule `schedule_recheck` and remain fail-closed.
- `human_gate_required=false`, `external_runtime_action_authorized=false`, `auto_retry_authorized=false`, and `auto_rollback_authorized=false` remain fixed.

## Verification
- Consumer state transition contract was already Green at run #997 on commit `5783f76f2ef1948ad56c018aa982a4f9461b36d8`.
- Scheduler implementation/test/workflow commit: `88cecc44fc1427aa20a02ec7305525ce30f218d3`.
- Research Lab CI run #1000 on the exact SHA `88cecc44fc1427aa20a02ec7305525ce30f218d3` completed successfully.
- All existing Research Lab checks plus the new hourly scheduler test completed successfully.

## Boundary
This milestone defines the hourly decision contract; it does not by itself add a second independent GitHub cron. The existing ChatGPT hourly schedule remains the primary autonomous research trigger. A future scheduler integration must preserve duplicate-slot protection and the exact-SHA/CI gates.

## Next
Evaluate the actual hourly trigger path and connect it to the scheduler contract only after proving that duplicate execution cannot occur between the ChatGPT schedule and any GitHub-side trigger.
