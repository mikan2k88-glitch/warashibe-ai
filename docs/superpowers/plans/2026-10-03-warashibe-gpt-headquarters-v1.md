# Warashibe GPT Headquarters v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a persistent GPT-side strategy headquarters that preserves current strategy, records durable strategic decisions, and guides future Warashibe development without granting real-world execution authority.

**Architecture:** GitHub stores the human-readable current strategy, Supabase stores append-only strategic decision history, and `research_lab/headquarters.py` builds a safe strategy snapshot. Existing Runtime Status remains the deployment-evidence source. Skills and Library describe the operating rule for future sessions.

**Tech Stack:** Python, GitHub Actions, Supabase/Postgres, Render, Markdown.

**Spec:** `docs/superpowers/specs/2026-10-03-warashibe-gpt-headquarters-design.md`

## Global Constraints

- North Star: approximately JPY 3,000 -> one item at a time -> JPY 1,000,000.
- Priority order: Commerce Loop -> Capital Velocity -> Learning Loop.
- Human Gate remains required for real purchase, payment, sale/listing, secrets/auth changes, destructive DB changes, and risky main/production changes.
- HQ never self-authorizes execution.
- Strategy history is append-only in v1.
- Public Supabase table uses RLS and closed-by-default anon/authenticated access.
- Runtime evidence lookup remains Supabase -> Render connector -> Firecrawl.

## Review Focus

- Missing or malformed strategic state must not produce execution authorization.
- Unchanged wording must not create strategy churn.
- Strategy repository must expose no update/delete workflow.
- Supabase table must remain inaccessible to anon/authenticated roles.
- Runtime inconsistency must not be interpreted as strategy completion.

---

### Task 1: Headquarters contract and current strategy source

**Files:**
- Create: `docs/WARASHIBE_HQ.md`
- Create: `research_lab/test_headquarters.py`
- Modify: `research_lab/runner.py`
- Create: `research_lab/headquarters.py`

**Interfaces:**
- Produces: `build_headquarters_snapshot(...)`, `evaluate_strategy_transition(current, candidate, evidence)`.

- [ ] Write tests first for Human Gate, no self-authorization, one bottleneck, stable strategy, and material transition detection.
- [ ] Activate the test module in runner and verify targeted RED.
- [ ] Implement the minimal HQ module and current strategy doc.
- [ ] Verify targeted tests and full build profile pass.
- [ ] Commit.

### Task 2: Append-only strategy decision repository

**Files:**
- Create: `research_lab/test_supabase_strategy_decision_repository.py`
- Create: `research_lab/supabase_strategy_decision_repository.py`

**Interfaces:**
- Produces: `SupabaseStrategyDecisionRepository.latest(limit=...)` and `.append(decision)`.
- No update/delete methods.

- [ ] Write repository contract tests first.
- [ ] Verify RED.
- [ ] Implement minimal append/latest repository.
- [ ] Verify tests pass.
- [ ] Commit.

### Task 3: Supabase strategy memory schema

**Files:**
- Create: `docs/migrations/2026-10-03_strategy_decisions.sql`

**Interfaces:**
- Produces: `public.warashibe_strategy_decisions`.

- [ ] Add migration source with required fields and status check constraint.
- [ ] Enable RLS and revoke anon/authenticated privileges.
- [ ] Commit migration source.
- [ ] Apply migration to project `bittxuhjejaokfgmymkw`.
- [ ] Insert and read back initial HQ decision.
- [ ] Run security/performance advisors.

### Task 4: HQ skill and skills index

**Files:**
- Create: `docs/skills/using-warashibe-headquarters/SKILL.md`
- Modify: `docs/WARASHIBE_SKILLS.md`

**Interfaces:**
- Produces future-session trigger and operating rule.

- [ ] Add concise project skill using HQ when a session starts or next objective is chosen.
- [ ] Update index to mark HQ as active.
- [ ] Commit.
- [ ] Verify CI.

### Task 5: Endpoint verification and persistence

**Files/Systems:**
- GitHub Actions
- Render
- Supabase `warashibe_runtime_status`
- ChatGPT Library `Warashibe AI 開発引き継ぎ.md`

**Interfaces:**
- Consumes exact HEAD SHA from final commit.

- [ ] Confirm exact-SHA CI success.
- [ ] Confirm same SHA live on Render.
- [ ] Append verified Runtime Status snapshot with `deployment_consistent=true`.
- [ ] Sync HQ architecture and current strategy into Library handoff.
- [ ] Verify Library version increment and final project state.
