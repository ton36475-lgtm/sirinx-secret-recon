# GhostClaw a2a swarm playbook — Secret Recon

```
Council
  ├─ L1-github     parallel per priority repo (native alerts)
  ├─ L1-local      Mac mini / worker gitleaks or recon_engine
  ├─ L1-config     n8n JSON + CF bindings + tfstate (owned)
  ├─ L2-classify   OmniRoute
  └─ L3-gate       47 Ronin / human approval
```

Sync rules:
- Findings become tasks with fingerprint as idempotency key.
- Dashboard module reads `secret_recon_findings` (Supabase) — fingerprints only.
- Dry-run flag defaults true in `ghostclaw council.env`.
