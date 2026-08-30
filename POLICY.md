# POLICY — Defensive Secret Recon Only

## Allowed
- Scan repos owned by ton36475-lgtm
- Scan local workers and SIRINX Cloudflare/Supabase exports (masked)
- Store fingerprints + path + rule + severity only
- Open Issue/PR; rotate only after human approval

## Forbidden
- Public GitHub search for usable third-party keys
- Storing raw secrets in chat, agent memory, dashboards, or R2 public buckets
- Auto-rotate production keys
- Scanning third-party or customer code without written authorization
