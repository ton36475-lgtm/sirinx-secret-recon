# Severity Matrix for Secret Findings

## Critical
- Live production API keys / service tokens that grant write or billing access (OpenAI, Anthropic, Cloudflare, AWS, payment providers).
- Database connection strings with production credentials.
- Private keys (SSH, TLS, JWT signing) that can be used to impersonate services.
Action: Immediate human notification + quarantine related agents/services until rotated and re-scanned.

## High
- Staging or development keys that still have elevated privileges.
- Tokens with long expiry that appear in git history.
Action: Create issue + PR within 24h, rotate within 72h.

## Medium
- Keys already rotated but still present in history or documentation.
- Test fixtures that look real but are known dummies.
Action: Clean history or mark as false positive with justification.

## Low / Info
- Example keys in README or public docs that are clearly placeholders.
- Publicly documented demo tokens.
Action: Optional documentation improvement.

Always prefer false-positive reduction over aggressive auto-remediation.
