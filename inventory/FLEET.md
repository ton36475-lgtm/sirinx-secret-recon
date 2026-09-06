# Live Fleet Inventory — 2026-09-06 20:12 UTC

**Owner:** ton36475-lgtm
**Policy:** own-assets-only

## Repositories in scope

| Priority | Repo | Visibility |
|----------|------|------------|
| 1 | ghost-claw-os | public |
| 1 | hermes-mesh-fusion | private |
| 1 | hermes-os | private |
| 1 | sirinx-co | public |
| 1 | sirinx-os | public |
| 1 | sirinx-secret-recon | public |
| 1 | sirinx-skills-kit | public |
| 2 | oz-corp-omega-dual-node | public |
| 2 | sirinx-godmode | public |
| 2 | sirinx-sovereign-swarm | public |
| 3 | automated-marketing-agency | public |
| 3 | automation-dashboard | public |
| 3 | automation-documentation | public |
| 3 | automation-mobile-app | public |
| 3 | automation-system-backend | public |
| 3 | chokma-growth-os | public |
| 3 | oz_mobile_app | public |
| 3 | sirinx | public |
| 3 | sirinx-solar-energy | public |
| 4 | unknowcoding-newbie-dev-skill | public |

## Operating rules
1. Scan only rows in this table.
2. Prefer GitHub native secret scanning + push protection.
3. Fall back to local `src/recon_engine.py` or `scripts/scan-wrapper.sh`.
4. Store fingerprints only. Human gate before any rotation.
5. Never search public GitHub for third-party keys to use those keys.
