-- SIRINX Redteam Secret Recon — Findings Metadata Schema
-- Store ONLY fingerprints + location + severity + status.
-- NEVER store raw secret values.

-- Enable required extensions if not already present
create extension if not exists "pgcrypto";

-- Findings table
create table if not exists secret_recon_findings (
  id                uuid primary key default gen_random_uuid(),
  fingerprint       text not null,                    -- SHA-256 of the secret (or gitleaks fingerprint)
  secret_type       text not null,                    -- e.g. openai-api-key, aws-access-key, generic-api-key
  severity          text not null check (severity in ('Critical', 'High', 'Medium', 'Low', 'Info')),
  repo_full_name    text,                             -- owner/repo
  file_path         text,
  commit_sha        text,
  line_number       integer,
  branch            text,
  status            text not null default 'open' check (status in ('open', 'triaged', 'false_positive', 'remediated', 'wont_fix')),
  classification    text,                             -- true_positive / false_positive / test_fixture / docs_example
  remediation_notes text,
  assigned_to       text,                             -- GhostClaw agent or human
  ghostclaw_task_id text,
  first_seen_at     timestamptz not null default now(),
  last_seen_at      timestamptz not null default now(),
  remediated_at     timestamptz,
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now()
);

-- Unique constraint on fingerprint + location to avoid duplicates
create unique index if not exists idx_findings_fingerprint_location
  on secret_recon_findings (fingerprint, coalesce(repo_full_name, ''), coalesce(file_path, ''), coalesce(commit_sha, ''));

create index if not exists idx_findings_status on secret_recon_findings (status);
create index if not exists idx_findings_severity on secret_recon_findings (severity);
create index if not exists idx_findings_repo on secret_recon_findings (repo_full_name);

-- Scan runs table for observability
create table if not exists secret_recon_scans (
  id              uuid primary key default gen_random_uuid(),
  source          text not null,                      -- github-native / gitleaks / trufflehog / n8n / manual
  target          text not null,                      -- repo or path
  started_at      timestamptz not null default now(),
  finished_at     timestamptz,
  findings_count  integer default 0,
  status          text not null default 'running' check (status in ('running', 'completed', 'failed')),
  report_json_url text,                               -- R2 or local path to redacted report
  error_message   text,
  created_at      timestamptz not null default now()
);

-- RLS policies (operator only — adjust to your auth model)
alter table secret_recon_findings enable row level security;
alter table secret_recon_scans enable row level security;

-- Example policy: service_role full access (adjust for your JWT claims)
create policy "service_role_all_findings" on secret_recon_findings
  for all using (auth.role() = 'service_role');

create policy "service_role_all_scans" on secret_recon_scans
  for all using (auth.role() = 'service_role');

-- Updated_at trigger
create or replace function update_updated_at_column()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger update_findings_updated_at
  before update on secret_recon_findings
  for each row execute function update_updated_at_column();
