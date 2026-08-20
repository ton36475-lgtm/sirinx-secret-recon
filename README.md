# SIRINX Redteam Secret Recon — Operational Package

**Status**: Ready for GhostClaw / SIRINX agent swarm deployment  
**Scope**: Own assets only (`ton36475-lgtm` org/user + controlled infra)  
**Safety**: Dry-run default · Human approval gates · No third-party key harvesting

## Quick Start

### 1. Enable GitHub Native Secret Scanning (Recommended First)

On every owned repository:

- Settings → Code security and analysis → Enable **Secret scanning**
- Enable **Push protection**
- (Optional) Enable **Secret scanning validity checks**

Then list current alerts:

```bash
# Via connected tools or gh CLI
gh api repos/{owner}/{repo}/secret-scanning/alerts
```

### 2. Deploy CI Workflow

Copy `scripts/github-actions-secret-scan.yml` → `.github/workflows/secret-scan.yml`  
Copy `scripts/gitleaks.toml` → `.gitleaks.toml` (or keep in skill path)

Push to trigger first scan. Critical findings auto-open Issues labeled `security,secret-recon,priority:high`.

### 3. Local / Mac mini / Windows Worker Scan

```bash
# Install gitleaks if needed
brew install gitleaks   # or go install github.com/gitleaks/gitleaks/v8@latest

# Scan current directory (working tree)
./scripts/scan-wrapper.sh .

# Full git history
./scripts/scan-wrapper.sh /path/to/repo --full-history
```

Reports land in `/tmp/secret-recon-reports/` (JSON + SARIF, redacted).

### 4. Feed into L2 + GhostClaw

- JSON findings → OmniRoute classification agent (prompt uses severity-matrix).
- Critical/High → create GhostClaw task or a2a dispatch.
- Dashboard module (see `dashboard/`) surfaces status inside Pixel AI Office.

### 5. Terraform (Optional)

```bash
cd terraform
terraform init
terraform plan   # review
# terraform apply  # only after human review
```

Declares secret-scanning enablement, alerting sinks, and optional scanner runners.

### 6. n8n Orchestration

Import `n8n/secret-recon-orchestrator.json` into your n8n instance.  
Schedule: daily full + hourly high-risk paths.  
Webhook path for GitHub events.

### 7. Supabase Schema

Run `supabase/schema.sql` against your operator-owned Supabase project.  
Stores only fingerprints + metadata (never raw secrets).

## Priority Repositories (from scan-scope)

1. `sirinx-os` (private)
2. `sirinx-co`
3. `sirinx-skills-kit`
4. `ghost-claw-os`
5. `oz-corp-omega-dual-node`
6. `hermes-os`
7. `sirinx-solar-energy`
8. All `automation-*` and remaining owned repos

## Human Approval Gates

Any action that:

- Rotates a production key
- Rewrites git history
- Quarantines a live service

**must** pass through GhostClaw council / Pixel AI Office approval channel.

## Observability

- Prometheus: `secrets_found_total`, `secrets_remediated_total`, `scan_duration_seconds`
- OpenTelemetry: one span per scan job + child spans per finding
- Dashboard: severity pie + open findings table + last-scan timestamp

## Forbidden Actions

- Public GitHub search for usable third-party keys (`OPENAI_API_KEY`, etc.)
- Persisting raw secret values anywhere outside a secrets manager
- Auto-rotation without explicit human sign-off

---

**Built from redteam-secret-recon skill · Integrated with GhostClaw OS, OmniRoute, SIRINX pipeline.**
