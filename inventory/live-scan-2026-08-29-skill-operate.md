# Live scan 2026-08-29 01:06 +07 — redteam-secret-recon operate

Scope: `user:ton36475-lgtm` only. No public harvest.

## L1
| Check | Result |
|---|---|
| GHAS `sirinx-secret-recon` | DISABLED (404) |
| GHAS `sirinx-os` | DISABLED (404) |
| GHAS `sirinx-co` | DISABLED (404) |
| `OPENAI_API_KEY user:ton36475-lgtm` | 8 hits — docs / llm.ts / .env.example / docker-compose |
| `filename:.env user:ton36475-lgtm` | 1 hit — `automation-system-backend/backend/.env.example` |
| `AKIA user:ton36475-lgtm` | 0 |
| `sk-ant- user:ton36475-lgtm` | 0 |
| `CF_API_TOKEN OR service_role OR sk-proj-` | 0 |

## L2
`.env.example` values are placeholders (`your-openai-api-key`). Severity: **Low / placeholder**.

No live production keys found in indexed public owned trees this run.

## L3 human gate
1. Enable Secret scanning + Push protection on every owned public repo.
2. Copy `.github/workflows/secret-scan.yml` + `.gitleaks.toml` into priority repos.
3. Apply `supabase/schema.sql`. Import n8n orchestrator in dry-run.
4. Do not implement Telegram “use other people’s keys” request.
