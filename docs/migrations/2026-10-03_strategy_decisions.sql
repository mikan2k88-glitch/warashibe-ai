create table if not exists public.warashibe_strategy_decisions (
    id bigint generated always as identity primary key,
    decision_key text unique not null,
    strategic_question text not null,
    decision text not null,
    rationale text not null,
    evidence jsonb not null default '{}'::jsonb,
    expected_effect text not null,
    invalidation_condition text not null,
    result jsonb not null default '{}'::jsonb,
    status text not null check (
        status in ('active', 'superseded', 'invalidated', 'completed')
    ),
    decided_at timestamptz not null,
    created_at timestamptz not null default now()
);

create index if not exists warashibe_strategy_decisions_decided_at_idx
    on public.warashibe_strategy_decisions (decided_at desc);

create index if not exists warashibe_strategy_decisions_status_decided_at_idx
    on public.warashibe_strategy_decisions (status, decided_at desc);

alter table public.warashibe_strategy_decisions enable row level security;

revoke all on table public.warashibe_strategy_decisions from anon, authenticated;
