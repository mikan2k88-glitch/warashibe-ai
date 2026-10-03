---
name: using-warashibe-runtime-status
description: Use when checking Warashibe AI research-lab deployment state, CI and Render SHA consistency, Render live status, or deciding whether Firecrawl is needed.
---

# Using Warashibe Runtime Status

## Overview
Use the Supabase runtime-status cache first. GitHub and Render remain sources of truth; Firecrawl is a last fallback.

## When to Use
- Checking whether research-lab is deployed and live.
- Verifying HEAD, CI SHA, and Render live SHA.
- Deciding whether a direct Render lookup or Firecrawl is necessary.
- Auditing a completed development endpoint.

## Core Contract
Read the latest row from `public.warashibe_runtime_status` for:
- service_name = `warashibe-ai-research-lab`
- branch = `research-lab`

Treat the cached deployment as consistent only when:
- `deployment_consistent = true`
- `ci_status = success`
- `render_status = live`
- `git_head_sha = ci_sha = render_live_sha`

## Source Priority
1. Supabase runtime-status cache.
2. Render connector when the cache is missing, stale, or inconsistent.
3. Firecrawl only when required evidence still cannot be obtained.

When Render is checked directly, append a new verified snapshot to Supabase.

## Fixed Render Context
- Workspace: `My Workspace`
- workspaceId: `tea-d9gv8dj7uimc7395bt5g`
- Service: `warashibe-ai-research-lab`
- serviceId: `srv-daq2dru7bikc73bb9ik0`

Pass the confirmed workspaceId directly to Render calls. Do not stop to ask for workspace selection again unless the configured workspace is unavailable or the user explicitly changes it.

## Safety
The Supabase row is an audit/cache record only. It never authorizes deployment, purchases, sales, payments, secrets changes, production changes, or controlled automation.

## Common Mistakes
| Mistake | Correct behavior |
|---|---|
| Start with Firecrawl | Query Supabase first |
| Treat Supabase as source of truth | Use it as verified cache; GitHub/Render remain authoritative |
| Trust a successful CI alone | Require exact SHA equality with Render live |
| Reuse a stale cache blindly | Refresh from Render and append a new snapshot |
| Ask for My Workspace every time | Reuse the confirmed workspaceId |
