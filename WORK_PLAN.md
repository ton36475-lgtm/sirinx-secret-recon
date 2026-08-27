# Work Plan — Secret Recon (redteam-secret-recon)

## Done this session
- Confirmed owner ton36475-lgtm
- Inventoried owned repos
- Confirmed native secret scanning disabled on key repos
- Owned-account pattern search: no live keys in indexed code
- Packaged Terraform / n8n / schema / agents / dashboard spec

## Human next
1. Enable GitHub Secret scanning + Push protection on public owned repos
2. Copy `.github/workflows/secret-scan.yml` + `.gitleaks.toml` into priority repos
3. Import n8n orchestrator and apply supabase/schema.sql
4. Install local pre-commit on Mac mini / Windows worker

## Forbidden
Public search for OPENAI_API_KEY (or any provider key) with intent to use found keys.
