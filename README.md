# SIRINX / GhostClaw – Redteam Secret Recon System

**Defensive-only automated secret & API-key reconnaissance for owned assets.**

This package implements the `redteam-secret-recon` skill as a complete, production-ready system for the SIRINX / OZ-CORP / GhostClaw agentic environment.

> **Core Safety Rule (Non-Negotiable)**  
> Scan and act **only** on repositories, files, environments and infrastructure owned or controlled by the operator (`ton36475-lgtm` org/user, local Mac mini / Windows worker, Cloudflare accounts under SIRINX, Supabase projects of the operator).  
> **Never** search public GitHub or the open web for the purpose of obtaining usable third-party API keys.

## Quick Start

```bash
# 1. Local scan (requires gitleaks)
./scripts/scan-wrapper.sh /path/to/your/repo

# 2. Install GitHub Actions workflow into any owned repo
cp .github/workflows/secret-scan.yml <repo>/.github/workflows/secret-scan.yml
# or use the copy in scripts/

# 3. Enable native GitHub Secret Scanning + Push Protection on the repo

# 4. Deploy Supabase schema (see supabase/)
# 5. Import n8n workflow (see n8n/)
# 6. Optional Terraform for infra-as-code enablement (see terraform/)
```

## Package Contents

```
sirinx-secret-recon/
├── README.md
├── ARCHITECTURE.md
├── docs/
│   └── RUNBOOK.md
├── scripts/
│   ├── gitleaks.toml
│   ├── scan-wrapper.sh
│   └── install-pre-commit.sh
├── .github/workflows/secret-scan.yml
├── terraform/
├── n8n/
├── supabase/
├── dashboard/
└── references/
```

## Architecture Summary

- **L1 Perception / Scanner Agents**  
  GitHub native secret scanning, Gitleaks/TruffleHog local + CI, n8n exports, Cloudflare bindings, Terraform state.

- **L2 Analysis Agents**  
  Multi-LLM classification (true/false positive, severity) via OmniRoute / model catalog. Cross-check against known-good secret stores.

- **L3 Decision + Remediation**  
  GhostClaw / 47 Ronin decision layer. Default: Issue + PR. Critical: human approval gate + optional emergency rotation (n8n) after approval.

- **Orchestration**  
  n8n (daily/hourly) + GitHub webhooks + agent swarm (a2a live dispatch). Dashboard module inside Pixel AI Office / mission-control.

All findings store **only fingerprints / metadata**. Raw secret values are never persisted in agent memory, logs, Obsidian, or R2.

## Integration with Existing SIRINX Stack

| Component              | Role                                      |
|------------------------|-------------------------------------------|
| GhostClaw OS / a2a     | Findings become tasks for coding sub-agents or humans |
| OmniRoute + catalog    | Best model for classification             |
| Supabase / Redis / R2  | Finding metadata only                     |
| Cloudflare Workers     | Lightweight webhook receivers (optional)  |
| Pixel AI Office UI     | Surface open findings & remediation status|
| Production gates       | dry-run → approval → quarantine           |

## Operating Procedure

1. Confirm scope is strictly own assets.
2. Prefer GitHub native alerts first.
3. Fall back to local Gitleaks for custom patterns / full history.
4. Feed redacted findings to L2 LLM classification.
5. Route High/Critical through GhostClaw human gates.
6. After remediation, re-scan to confirm clean.
7. Never output or persist raw secret values.

## Anti-Patterns (Forbidden)

- Searching `OPENAI_API_KEY` (or equivalent) across public GitHub with intent to use found keys.
- Storing or transmitting raw secrets in agent context, chat, or non-secret stores.
- Auto-rotating production keys without explicit human approval.
- Scanning third-party repositories or customer environments without written authorization.

---

**Built for GhostClaw OS · SIRINX · OZ-CORP**  
Defensive security hygiene only.
