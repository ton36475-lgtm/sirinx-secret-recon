# Enable GitHub Secret Scanning (required)

Live check 2026-09-09 against owned repos:

- `ton36475-lgtm/sirinx-secret-recon` — Secret scanning **DISABLED** (API 404)
- `ton36475-lgtm/sirinx-os` — Secret scanning **DISABLED**
- `ton36475-lgtm/sirinx-co` — Secret scanning **DISABLED**

## Operator steps (human)
1. Open each owned repo → Settings → Code security and analysis
2. Enable **Secret scanning**
3. Enable **Push protection**
4. Enable Dependabot alerts
5. Copy `.github/workflows/secret-scan.yml` from this package
6. Re-run `python3 -m secret_recon.cli .`

Public-repo secret scanning is available on GitHub Free; private repos may need GHAS.
