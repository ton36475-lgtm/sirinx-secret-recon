# Policy — SIRINX Secret Recon (Non-Negotiable)

## Allowed
- Scan repositories owned by `ton36475-lgtm` (and future SIRINX orgs under the same operator).
- Scan local working trees on operator-controlled machines (Mac mini, Windows worker).
- Scan exported n8n workflows, Cloudflare bindings, Terraform state **owned by the operator**.
- Store fingerprints + location + severity. Mask values everywhere.

## Forbidden
- Searching public GitHub / the open web for `OPENAI_API_KEY` (or any provider key) **to use other people's credentials**.
- Using leaked third-party keys. That violates provider TOS and can be unauthorized access.
- Auto-rotating production keys without a human approval gate.
- Scanning customer or partner code without written authorization.
- Persisting raw secrets in chat, Obsidian, R2 public buckets, or agent memory.

## Default mode
Dry-run. Live validation (TruffleHog verify) is optional, rate-limited, non-destructive, and logged.

## Screenshot / vibe-code note
A Telegram prompt suggesting “search GitHub for OPENAI_API_KEY.env to spend other people’s money” is **out of policy**. This system will not implement that path.
