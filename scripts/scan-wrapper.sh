#!/usr/bin/env bash
# SIRINX Redteam Secret Recon - Local Scanner Wrapper
# Defensive only. Scan only owned assets.
# Usage: ./scan-wrapper.sh [path-to-repo-or-dir] [--full-history]

set -euo pipefail

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
  echo "ERROR: gitleaks is not installed."
  exit 2
fi

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
REPORT_JSON="$REPORT_DIR/findings-$TIMESTAMP.json"
REPORT_SARIF="$REPORT_DIR/findings-$TIMESTAMP.sarif"

run_report() {
  local format="$1"
  local output="$2"
  local -a args=(
    detect
    --source "$TARGET"
    --config "$CONFIG"
    --report-format "$format"
    --report-path "$output"
    --no-banner
    --redact
  )

  if [[ "$FULL_HISTORY" == "--full-history" ]]; then
    args+=(--log-opts="--all")
  fi

  set +e
  gitleaks "${args[@]}"
  local status=$?
  set -e
  return "$status"
}

echo "Running redacted JSON scan..."
JSON_STATUS=0
run_report json "$REPORT_JSON" || JSON_STATUS=$?

echo "Running redacted SARIF scan..."
SARIF_STATUS=0
run_report sarif "$REPORT_SARIF" || SARIF_STATUS=$?

echo
echo "=== Scan complete ==="
echo "JSON report: $REPORT_JSON"
echo "SARIF report: $REPORT_SARIF"

# Fail closed. The previous wrapper swallowed every Gitleaks non-zero exit via
# `|| true`, which could make a scan with findings look successful to callers.
# Preserve non-zero status so CI/orchestration can stop the phase gate.
if (( JSON_STATUS != 0 || SARIF_STATUS != 0 )); then
  echo "RESULT: BLOCKED — Gitleaks returned a non-zero status."
  echo "Review only the redacted reports; never copy raw secret values into logs or chat."
  exit 1
fi

echo "RESULT: CLEAN — both redacted scans completed successfully."
echo "Next: continue the phase only after the independent literal-prefix gate and build/test checks pass."
