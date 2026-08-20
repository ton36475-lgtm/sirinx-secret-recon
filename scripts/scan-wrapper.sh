#!/usr/bin/env bash
# SIRINX Redteam Secret Recon - Local Scanner Wrapper
# Defensive only. Scan only owned assets.
# Usage: ./scan-wrapper.sh [path-to-repo-or-dir] [--full-history]

set -euo pipefail

SCOPE_FILE="$(dirname "$0")/../references/scan-scope-and-tools.md"
CONFIG="$(dirname "$0")/gitleaks.toml"
REPORT_DIR="${REPORT_DIR:-/tmp/secret-recon-reports}"
mkdir -p "$REPORT_DIR"

TARGET="${1:-.}"
FULL_HISTORY="${2:-}"

echo "=== SIRINX Redteam Secret Recon ==="
echo "Target: $TARGET"
echo "Config: $CONFIG"
echo "Report dir: $REPORT_DIR"
echo "Safety: Own assets only. Never scan third-party."

if ! command -v gitleaks >/dev/null 2>&1; then
  echo "ERROR: gitleaks not installed. Install via: brew install gitleaks  or  go install github.com/gitleaks/gitleaks/v8@latest"
  exit 1
fi

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
REPORT_JSON="$REPORT_DIR/findings-$TIMESTAMP.json"
REPORT_SARIF="$REPORT_DIR/findings-$TIMESTAMP.sarif"

GITLEAKS_ARGS=(
  detect
  --source "$TARGET"
  --config "$CONFIG"
  --report-format json
  --report-path "$REPORT_JSON"
  --no-banner
  --redact
)

if [[ "$FULL_HISTORY" == "--full-history" ]]; then
  GITLEAKS_ARGS+=(--log-opts="--all")
fi

echo "Running gitleaks..."
gitleaks "${GITLEAKS_ARGS[@]}" || true

# Also produce SARIF for GitHub Code Scanning integration if needed
gitleaks detect \
  --source "$TARGET" \
  --config "$CONFIG" \
  --report-format sarif \
  --report-path "$REPORT_SARIF" \
  --no-banner \
  --redact || true

echo ""
echo "=== Scan complete ==="
echo "JSON report: $REPORT_JSON"
echo "SARIF report: $REPORT_SARIF"
echo ""
echo "Next steps (per skill):"
echo "1. Feed findings to L2 Analysis Agents (OmniRoute classification)"
echo "2. Queue Critical/High into GhostClaw decision layer"
echo "3. Create Issues/PRs for remediation (never auto-rotate without approval)"
echo "4. Re-scan after remediation"
echo "5. Mask all secret values in logs/dashboard"
