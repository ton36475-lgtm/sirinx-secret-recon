-- Finding metadata only. Never store raw secret values.
create extension if not exists pgcrypto;

create table if not exists secret_findings (
  id uuid primary key default gen_random_uuid(),
  fingerprint text not null,
  rule_id text not null,
  repo text not null,
  path text not null,
  line_no integer,
  severity text not null check (severity in ('critical','high','medium','low','info')),
  classification text not null default 'needs_review',
  status text not null default 'open' check (status in ('open','triaged','remediating','resolved','false_positive')),
  redacted text,
  source text default 'l1-scanner',
  ghostclaw_task_id text,
  github_issue_url text,
  found_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (fingerprint, repo, path)
);

create index if not exists secret_findings_status_idx on secret_findings (status, severity);
alter table secret_findings enable row level security;
