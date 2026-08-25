# Redteam Secret Recon – System Architecture

**Version:** 1.1 (upgraded from skill)  
**Scope:** Defensive secret & API-key discovery, classification and remediation for **owned assets only** (ton36475-lgtm / SIRINX / GhostClaw).

## 1. Design Principles

1. **Own-assets only** – never harvest third-party secrets.
2. **Zero raw secret retention** – fingerprints + metadata only.
3. **Human-in-the-loop for Critical** – GhostClaw / SIRINX OS policy gates.
4. **Dry-run default** – live validation or rotation requires explicit approval.
5. **Agentic + traditional hybrid** – L1 scanners can be pure tools or sub-agents; L2 uses multi-LLM routing; L3 uses GhostClaw council.

## 2. Layered Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Pixel AI Office / Dashboard                   │
│         (findings list · severity distribution · status)         │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                 L3 Decision + Remediation Layer                  │
│  GhostClaw / 47 Ronin · Issue+PR · Approval gates · n8n rotate  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                      L2 Analysis Agents                          │
│  OmniRoute multi-LLM · true/false positive · severity · path     │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                   L1 Perception / Scanner Agents                 │
│  GitHub native · Gitleaks · TruffleHog · n8n · CF · Terraform    │
└─────────────────────────────────────────────────────────────────┘
```

### 2.1 L1 – Perception / Scanner Agents

| Source                    | Tool / Method                          | Frequency          | Notes |
|---------------------------|----------------------------------------|--------------------|-------|
| Owned GitHub repos        | Native Secret Scanning + Push Protection | Continuous + on push | Preferred first path |
| Owned GitHub repos        | Gitleaks (Actions + local)             | Push / PR / daily  | Custom rules + full history |
| Local Mac mini / Windows  | `scan-wrapper.sh` + Gitleaks           | On demand / cron   | Working trees + .env* (not committed) |
| n8n workflow exports      | JSON parse + regex / Gitleaks          | On export / daily  | Never store live secrets in workflows |
| Cloudflare Workers/Pages  | API export of bindings (masked)        | Daily / on change  | Use CF API or dashboard export |
| Terraform state / plans   | Gitleaks on plan files                 | On plan / apply    | Catch accidental injection |
| Process environment       | Snapshot (masked)                      | On demand          | Local control-plane only |

**Custom Gitleaks rules** (see `scripts/gitleaks.toml`):
- OpenAI (`sk-…T3BlbkFJ…` and generic `sk-`)
- Anthropic (`sk-ant-…`)
- AWS Access Key + Secret
- Cloudflare API Token
- Supabase service_role / JWT
- Generic API key / token patterns
- Allowlist for test/example/dummy paths and placeholder values

### 2.2 L2 – Analysis Agents

Input: redacted findings (RuleID, File, Commit, Line, Entropy, Fingerprint).

Processing (via OmniRoute / provider catalog – no hard-coded models):
1. Classify true positive vs false positive / test fixture / documentation.
2. Assign severity using `references/severity-matrix.md`.
3. Suggest remediation:
   - Delete from history (BFG / git-filter-repo)
   - Rotate key
   - Move to secrets manager (Supabase Vault / Cloudflare Secrets / 1Password)
   - Open PR + .gitignore / pre-commit hook
4. Cross-check fingerprint against known-good stores to reduce noise.

Output: structured finding record (Supabase / Redis) + task for L3.

### 2.3 L3 – Decision + Remediation

- **Default path**: create GitHub Issue (label `secret-recon`, `priority:high`) + optional auto-PR that removes the secret and adds protection.
- **Critical path**:
  1. Notify Pixel AI Office dashboard + human approval channel.
  2. Optionally trigger emergency key-rotation n8n workflow **only after** human approval.
  3. Quarantine related agents / services until re-scan is clean.
- All actions logged via OpenTelemetry spans + Prometheus counters (`secrets_found`, `secrets_remediated`, `secrets_false_positive`).

## 3. Orchestration

### 3.1 Traditional

- **n8n**:
  - Daily full scan workflow
  - Hourly high-risk path scan
  - GitHub webhook receiver → L1 → L2 → L3
  - Post-approval rotation workflow
- **GitHub Actions**: push / PR / schedule (see `.github/workflows/`)
- **Cron on Mac mini control plane**: local `scan-wrapper.sh`

### 3.2 Agentic (GhostClaw OS)

- Findings become a2a tasks.
- Parallel L1 scanner sub-agents per repo / source type.
- Coordinated by thClaws MCP Hub or GhostClaw council.
- Coding sub-agents can be assigned remediation PRs after human gate.

## 4. Data Model (Supabase)

See `supabase/schema.sql`.

Key tables:
- `secret_findings` – fingerprint, rule_id, severity, status, location metadata, never the secret value.
- `scan_runs` – audit of every scan.
- `remediation_actions` – linked to findings + approval records.

## 5. Observability

- OpenTelemetry traces for every scan → analysis → decision.
- Prometheus metrics:
  - `secret_recon_findings_total{severity, rule_id}`
  - `secret_recon_remediated_total`
  - `secret_recon_false_positive_total`
- Dashboard module inside existing Pixel AI Office / mission-control UI.

## 6. Terraform (Optional)

See `terraform/`. Declares:
- GitHub repository settings (secret scanning, push protection)
- Optional scanner runner (EC2 / Cloudflare Worker / local)
- Alerting (SNS / webhook → n8n / GhostClaw)

## 7. Safety & Compliance Checklist

- [ ] Scope confirmed = own assets only
- [ ] GitHub native secret scanning enabled on all target repos
- [ ] Gitleaks config + allowlist reviewed
- [ ] Supabase schema deployed (no secret columns)
- [ ] n8n workflows imported and dry-run tested
- [ ] Human approval channel configured for Critical
- [ ] Agent memory / logs configured to never retain raw secrets
- [ ] Re-scan procedure documented after every remediation

## 8. Forbidden Actions

- Public GitHub search for `OPENAI_API_KEY` (or any provider key) with intent to use the keys.
- Persisting raw secrets anywhere outside a proper secrets manager.
- Auto-rotation of production keys.
- Scanning any third-party or customer codebase without written authorization.

---

This architecture is designed to plug directly into the existing SIRINX multi-agent stack (GhostClaw OS, OmniRoute, Pixel AI Office dashboard, a2a live dispatch) while remaining fully usable as a standalone defensive tool.
