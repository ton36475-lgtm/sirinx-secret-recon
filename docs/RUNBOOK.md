# Secret Recon Runbook — SIRINX / GhostClaw

## Daily Operations

1. Check dashboard open Critical + High counts.
2. Review any new GitHub native alerts.
3. Confirm scheduled n8n / Actions runs succeeded.
4. For any Critical: open GhostClaw approval channel immediately.

## On New Finding (Critical)

1. Confirm it is a true positive via L2 classification.
2. Mask the value in every log/chat.
3. Create GhostClaw task with `requiresApproval: true`.
4. After human approval:
   - Rotate the key in the real secrets manager (Cloudflare / Supabase / 1Password).
   - Update all consuming services.
   - Clean git history if the secret was committed (BFG or git-filter-repo).
   - Force-push only after coordination.
5. Re-scan to confirm clean.
6. Mark finding as `remediated` in Supabase.

## False Positive Handling

- Document reason in `remediation_notes`.
- Add to gitleaks allowlist if pattern is legitimate test data.
- Status → `false_positive`.

## Adding New Patterns

1. Extend `scripts/gitleaks.toml` with new `[[rules]]`.
2. Test locally with `scan-wrapper.sh`.
3. Commit to skill / package.
4. Redeploy CI workflow if needed.

## Emergency Quarantine

If a live production key is confirmed leaked:

1. Immediately revoke / rotate at the provider.
2. Quarantine any agent or service still holding the old value.
3. Notify all operators via GhostClaw council channel.
4. Full post-mortem after clean state.

## Never

- Paste a real secret into chat, issue body, or dashboard.
- Search public GitHub for “free keys”.
- Auto-rotate without human gate.
