# SIRINX / GhostClaw Redteam Secret Recon System

**Defensive only. Own assets only (ton36475-lgtm + controlled infrastructure).**

## Purpose

Automated discovery, classification, and remediation of exposed secrets (API keys, tokens, credentials) exclusively within operator-owned repositories, local workspaces, n8n exports, Cloudflare bindings, Terraform state, and related systems.

Never used to harvest or exploit third-party secrets.

## Core Safety Rules (Non-Negotiable)

1. Scan and act **only** on assets owned or controlled by the operator.
2. Never search public GitHub / open web for usable third-party API keys.
3. All live remediation (key rotation, history rewrite) requires human approval via GhostClaw / SIRINX OS gates.
4. Dry-run is default. Live validation is rate-limited, non-destructive, and fully logged.
5. Mask all secret values in logs, dashboards, agent memory, and reports. Store only fingerprints + metadata.

## Layered Architecture

### L1 — Perception / Scanner Agents

| Source | Tool / Method | Frequency |
|--------|---------------|-----------|
| GitHub native | `github___list_secret_scanning_alerts`, enable Secret Scanning + Push Protection | Continuous + daily |
| Full history / custom patterns | Gitleaks (local + CI) with `scripts/gitleaks.toml` | On push / PR / daily schedule |
| Verification of liveness | TruffleHog (careful, dry-run preferred) | On Critical findings only |
| Runtime / config | n8n workflow JSON, Cloudflare Worker bindings export, Terraform plan/state, local env snapshots (masked) | On export or change |
| Targeted content | `github___run_secret_scanning` on specific files/diffs | Ad-hoc / PR review |

### L2 — Analysis Agents

- Receive raw findings (redacted).
- Route via OmniRoute / model catalog for:
  - True-positive vs false-positive / test fixture / docs example classification.
  - Severity assignment (Critical / High / Medium / Low) using `references/severity-matrix.md`.
  - Remediation suggestion (history clean via git-filter-repo/BFG, rotate, update secrets manager, open PR, update .gitignore + pre-commit).
- Cross-check against known-good stores (Supabase Vault, Cloudflare Secrets, 1Password if integrated).

### L3 — Decision + Remediation

- Queue into GhostClaw / 47 Ronin decision layer + a2a live dispatch.
- Default path: auto-create GitHub Issue + draft PR (remove secret + harden).
- Critical path: notify Pixel AI Office dashboard + human approval channel → optional emergency rotation workflow (n8n) after explicit approval.
- Observability: OpenTelemetry traces + Prometheus metrics (`secrets_found`, `secrets_remediated`, `scan_duration`).

### Orchestration

- **n8n**: scheduled daily full scan, hourly high-risk paths, webhook receivers for GitHub events.
- **Agent swarm**: parallel L1 scanners coordinated by GhostClaw council / thClaws MCP Hub.
- **Terraform**: optional declarative enablement of secret scanning, runner infra, alerting.
- **Dashboard**: cyberpunk Pixel AI Office / mission-control module surfaces open findings, severity distribution, remediation status.

## Integration with Existing SIRINX Stack

- GhostClaw OS / a2a live dispatch → findings become assignable tasks.
- OmniRoute + provider catalog → best model for classification without hardcoding.
- Supabase / Redis / R2 → store only hashed fingerprint + location + severity + status.
- Cloudflare Workers → lightweight webhook / scheduled triggers if preferred over n8n.
- Production gates → dry-run → approval → quarantine pattern already present in GhostClaw.

## Package Contents

```
secret-recon-system/
├── ARCHITECTURE.md          # This file
├── README.md                # Quick start & operation guide
├── scripts/
│   ├── gitleaks.toml
│   ├── scan-wrapper.sh
│   └── github-actions-secret-scan.yml
├── references/
│   ├── severity-matrix.md
│   └── scan-scope-and-tools.md
├── terraform/               # Skeleton for scanner enablement + alerting
├── n8n/                     # Workflow definitions (JSON)
├── supabase/                # Schema for findings metadata
├── dashboard/               # Module integration notes + sample component
└── docs/                    # Additional runbooks
```

## Operation Flow

1. Confirm scope = own assets only.
2. Prefer GitHub native alerts (cheapest, highest signal).
3. Fall back to Gitleaks/TruffleHog for custom patterns / full history.
4. Feed findings → L2 LLM classification.
5. Route Critical/High through GhostClaw human gates.
6. After remediation → re-scan to confirm clean.
7. Never persist or output raw secret values.

## Anti-Patterns (Forbidden)

- Searching `OPENAI_API_KEY` (or equivalent) across public GitHub with intent to use found keys.
- Storing / transmitting raw secrets in agent context, chat, or non-secret stores.
- Auto-rotating production keys without explicit human approval.
- Scanning third-party or customer environments without written authorization.
