# SIRINX Secret Recon — Work Plan (operate 2026-08-28)

Source skill: `redteam-secret-recon`
Operator: `ton36475-lgtm`
Mode: dry-run default · own assets only · no raw secret persistence

## Rejected from chat screenshots

The Telegram/bot prompt that says search public GitHub for `OPENAI_API_KEY.env` to spend other people's keys is FORBIDDEN. This system will never implement third-party key harvesting.

Allowed substitute: search only `user:ton36475-lgtm` for leaked *own* keys.

## Agent swarm (GhostClaw a2a)

| Agent | Layer | Job |
|---|---|---|
| L1-github | Perception | Native secret-scanning alerts + scoped code search on owned repos |
| L1-local | Perception | Gitleaks / scan-wrapper.sh / recon_engine.py on working trees |
| L1-config | Perception | n8n JSON exports, Cloudflare bindings, Terraform state (owned) |
| L2-classify | Analysis | True/false positive + severity via OmniRoute catalog |
| L3-gate | Decision | Issue + PR template; Critical requires human approval |
| dashboard-module | Presentation | Pixel AI Office / sirinx.co hygiene panel (fingerprints only) |

## Execution order

1. Confirm owner = ton36475-lgtm (done).
2. Inventory owned repos; GHAS secret scanning is DISABLED on public repos (404).
3. Scoped code search on own account only.
4. Ship package + zip.
5. Human next: enable Secret Scanning + Push Protection on priority repos.
6. Import n8n orchestrator; apply supabase/schema.sql.
7. Drop workflow + .gitleaks.toml into each priority repo.
8. After any remediation, re-scan.
