# SIRINX Secret Recon — Package Manifest

Built from skill `redteam-secret-recon` for operator `ton36475-lgtm`.

## What this zip is

A defensive secret / API-key reconnaissance system for **own assets only**.

- L1 scanners: GitHub native GHAS, Gitleaks CI, local `recon_engine.py`
- L2 classification: placeholders vs needs-review (no raw values stored)
- L3 gates: GhostClaw human approval before rotation
- Orchestration: n8n JSON + GitHub Actions + optional Terraform
- Dashboard module notes for sirinx.co / Pixel AI Office / Motionsites 3D
- AWS Agent Toolkit + Cloudflare Computer notes as optional infra lanes

## What this zip is not

- Not a public GitHub key harvester
- Not a way to use other people's `OPENAI_API_KEY`
- Not an auto-rotator for production credentials
