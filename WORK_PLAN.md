# Work Plan — Secret Recon Automation (2026-09-07)

## In scope now
1. Package this defensive system (Terraform, n8n, Supabase, agents, dashboard, scanners).
2. Live-scan owned GitHub assets only.
3. Record control gaps (GHAS off) and placeholder .env.example.
4. Deliver a single zip.

## Out of scope / refused
- Public GitHub harvest of OPENAI_API_KEY belonging to other people.
- Auto-rotating production keys.
- Building the full 3D solar sirinx.co redesign in this package (tracked as follow-on).

## Follow-on after hygiene is green
- Enable GHAS + push protection on remaining repos.
- Drop secret-scan.yml into sirinx-os / sirinx-co / ghost-claw-os / hermes-os.
- Import n8n orchestrator and apply Supabase schema.
- Dashboard module inside Pixel AI Office.
- Separate program: 3-site sirinx.co 3D solar upgrade using motionsites-inspired design system.
