# Operation Plan — put the system to work

Date: 2026-08-27
Mode: dry-run default
Owner: ton36475-lgtm

## Done

- Confirmed GitHub identity ton36475-lgtm
- Inventoried 19 owned repositories
- Rejected public third-party key harvest

## Today

1. Enable Secret scanning + Push protection on priority repos
2. Copy `.github/workflows/secret-scan.yml` and `.gitleaks.toml`
3. Install pre-commit hook on developer machines
4. Apply `supabase/schema.sql`
5. Import n8n workflows

## Definition of Done

- Native scanning on for priority repos
- Findings stored as fingerprints only
- Human approval required before production key rotation
