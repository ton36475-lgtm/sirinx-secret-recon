#!/usr/bin/env bash
# Install gitleaks pre-commit hook for owned local repos
# Usage: ./install-pre-commit.sh [path-to-repo]

set -euo pipefail

REPO_PATH="${1:-.}"
HOOK_DIR="${REPO_PATH}/.git/hooks"
HOOK_FILE="${HOOK_DIR}/pre-commit"

if [[ ! -d "${REPO_PATH}/.git" ]]; then
  echo "ERROR: ${REPO_PATH} is not a git repository"
  exit 1
fi

mkdir -p "$HOOK_DIR"

cat > "$HOOK_FILE" << 'EOF'
#!/usr/bin/env bash
# SIRINX defensive secret recon – pre-commit
# Blocks commits that contain high-entropy secrets (own assets only)

if ! command -v gitleaks >/dev/null 2>&1; then
  echo "[secret-recon] WARNING: gitleaks not found – skipping local scan"
  exit 0
fi

CONFIG="$(git rev-parse --show-toplevel)/.gitleaks.toml"
if [[ ! -f "$CONFIG" ]]; then
  # fallback to system or skill config if present
  CONFIG="${HOME}/.config/gitleaks/gitleaks.toml"
fi

echo "[secret-recon] Running gitleaks pre-commit scan..."
gitleaks protect --staged --config "$CONFIG" --redact --no-banner --verbose
EOF

chmod +x "$HOOK_FILE"
echo "[secret-recon] Pre-commit hook installed at $HOOK_FILE"
echo "[secret-recon] Also copy scripts/gitleaks.toml to the repo root as .gitleaks.toml for best results"
