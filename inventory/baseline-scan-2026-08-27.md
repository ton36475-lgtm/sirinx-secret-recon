# Baseline scan — 2026-08-27

Scope: `user:ton36475-lgtm` only. No public-web key harvest.

## GitHub native Secret Scanning

| Repo | Result |
|------|--------|
| ton36475-lgtm/sirinx-secret-recon | Disabled (API 404) |
| ton36475-lgtm/sirinx-co | Disabled (API 404) |
| ton36475-lgtm/sirinx-os | Disabled (API 404) |

Action: enable Secret scanning + Push protection on all priority repos.

## Code search (owned account only)

Query used: `filename:.env user:ton36475-lgtm`

| Path | Classification |
|------|----------------|
| `automation-system-backend/backend/.env.example` | Low / docs example. Not a live key. |

No committed live `.env` found in the indexed public tree of this account.

## Policy

Public GitHub harvest of third-party API keys is out of scope and not implemented.
