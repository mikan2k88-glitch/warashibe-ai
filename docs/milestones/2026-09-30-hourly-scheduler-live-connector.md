# 2026-09-30 — Hourly Scheduler Live Connector Milestone

## Goal
Prevent duplicate execution when the ChatGPT hourly supervisor schedule and a future GitHub Actions scheduled trigger refer to the same hourly research slot.

## Implemented
- Added `research_lab/scheduler_live_connector.py`.
- Added `research_lab/test_scheduler_live_connector.py`.
- The connector accepts only explicit scheduler sources: `chatgpt_schedule` and `github_actions_schedule`.
- A UTC top-of-hour slot is the idempotency key.
- A slot already completed is a no-op.
- CI `in_progress` blocks duplicate execution.
- CI `failure` does not trigger an automatic retry; it returns to research review.
- CI `success` is accepted only when the CI `head_sha` exactly matches the current HEAD.
- Unknown sources, invalid slots, unknown CI states, and SHA mismatch fail closed.
- The connector is decision-only: no external runtime action, retry, rollback, or human gate is introduced.

## CI verification
- Implementation/test workflow run #1004: success.
- The run executed `research_lab.runner` and all existing tests, including the new `test_scheduler_live_connector` test, successfully.
- Verified workflow head SHA: `6f27f415b5d2a55328465497665f45a41730ecb5`.

## Scheduling architecture decision
The GitHub Actions workflow remains push/manual-triggered for now. A GitHub cron is not enabled in this milestone because the existing ChatGPT hourly supervisor is already active and an independent cron would create an avoidable duplicate-trigger path. The connector contract is in place first so a future second trigger can be added only after live slot coordination is verified.

## Next milestone
Verify the live supervisor-to-CI handoff for one real hourly slot, then decide whether a GitHub scheduled fallback adds value without creating duplicate research cycles.
