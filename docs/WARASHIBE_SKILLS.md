# Warashibe AI Skills Index

This file is the project-level index for reusable Warashibe AI development techniques. Project policy remains authoritative in `Warashibe AI 開発引き継ぎ.md`.

## Project-specific skills

### using-warashibe-runtime-status
Path: `docs/skills/using-warashibe-runtime-status/SKILL.md`

Use for deployment verification and runtime-state lookup. Primary rule:
`Supabase -> Render connector -> Firecrawl`.

### verifying-exact-sha-deployment
Status: candidate for extraction.

Current rule:
`research-lab HEAD == successful CI SHA == Render live SHA` before calling the endpoint deployed consistently.

### syncing-warashibe-library
Status: candidate for extraction.

Current proven personal-Library path:
`files.list -> materialize -> edit -> source_file_ref -> destination_path overwrite -> files.list version check`.

### using-warashibe-dev-queue-fallback
Status: candidate for extraction.

When GitHub direct write is unavailable because of environment/tool restrictions, use the existing Supabase `warashibe_dev_queue` development-ticket path rather than stopping the milestone.

### presenting-complete-code
Status: candidate for extraction.

When code must be shown to the user, provide complete replaceable files while preserving modularity and avoiding unnecessary file growth.

## Installed/shared skills used by Warashibe AI

- Supabase: schema, RLS, migrations, SQL verification, advisors.
- Supabase Postgres Best Practices: query/schema optimization.
- Render MCP / Monitor / Debug: service, deployment, logs, metrics.
- Firecrawl: web fallback and hard-to-retrieve current information.
- Superpowers Test-Driven Development: contract -> RED -> minimal repair.
- Superpowers Systematic Debugging: CI/runtime failure diagnosis.
- Superpowers Verification Before Completion: evidence before completion claims.
- Superpowers Writing Skills: create/update reusable skills.

## Skill-management policy

Create or update a project skill when a technique is repeatedly reused, easy to forget, or causes wasted external calls when forgotten.

Do not create a skill for every PG or one-off implementation detail. Keep Warashibe Loop v2, Human Gate, one-item rule, starting-capital policy, and current milestone state in the project handoff document.

When a project-specific skill changes materially:
1. update its SKILL.md in the same development turn;
2. update this index if trigger/scope changes;
3. verify CI;
4. verify Render exact-SHA if the research-lab endpoint changed;
5. sync the Library handoff when the operational rule affects future development.
