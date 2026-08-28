# Live defensive scan — 2026-08-28 (operate session)

Operator: ton36475-lgtm
Skill: redteam-secret-recon
Mode: dry-run / metadata only
Rejected request from chat screenshots: public harvest of OPENAI_API_KEY to spend other people's quota.

## L1 Perception

| Check | Result |
|---|---|
| Auth user | ton36475-lgtm (18 public repos + private hermes-os) |
| Native secret scanning sirinx-secret-recon | DISABLED (404) |
| Native secret scanning sirinx-os | DISABLED (404) |
| github___run_secret_scanning on owned .env.example | Blocked: no GitHub Advanced Security |
| Code search user:ton36475-lgtm filename:.env | 1 file: automation-system-backend/backend/.env.example |
| Code search user:ton36475-lgtm sk-ant- | 0 |
| Code search user:ton36475-lgtm AKIA | 0 |

## L2 Classification

| Finding | Class | Severity | Action |
|---|---|---|---|
| automation-system-backend/backend/.env.example OPENAI_API_KEY=your-openai-api-key | docs / placeholder | Low | allowlist |
| GHAS disabled across owned public repos | control-plane gap | High (posture) | enable Secret Scanning + Push Protection |

No live production key values were retrieved or stored.
