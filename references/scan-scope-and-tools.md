# Recommended Scan Scope & Tools (Defensive Only)

## Owned Assets Priority Order
1. Private repositories under ton36475-lgtm (sirinx-os, codexskills, etc.)
2. Public monorepo and related (sirinx-co, sirinx-skills-kit, oz-corp-omega-*)
3. Local working trees on Mac mini M2 control plane and Windows GPU worker
4. Exported n8n workflows and Cloudflare Worker bindings (exported safely)
5. Terraform plans/state if secrets ever leaked into them

## Preferred Tools
- GitHub Secret Scanning (native) + push protection — enable on every repo
- Gitleaks (local + CI) for custom rules and full history
- TruffleHog for verification of whether a found secret is still live (use carefully, dry-run preferred)
- `github___run_secret_scanning` connected tool for targeted content scans
- Pre-commit hooks (gitleaks or detect-secrets) on all developer machines

## What Not to Scan
- Any third-party GitHub repositories
- Customer or partner codebases without explicit written authorization
- Public web / Pastebin / Telegram for "free keys"

## Integration Notes for SIRINX
- Findings metadata → Supabase table or Redis (fingerprint only)
- Alerts → Pixel AI Office dashboard + GhostClaw task queue
- Orchestration → n8n or agent a2a dispatch
- Observability → OpenTelemetry span per scan + Prometheus counter
