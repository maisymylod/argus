#!/usr/bin/env bash
# Deterministic, no-network guard against real secrets in tracked files.
# This is the CI backstop; pre-commit runs gitleaks for richer local coverage.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

# Real-secret shapes only, so README/.env.example placeholders do not trip it.
PATTERNS=(
  'sk-ant-api03-[A-Za-z0-9_-]{20,}'   # Anthropic API key
  'AKIA[0-9A-Z]{16}'                  # AWS access key id
  '-----BEGIN [A-Z ]*PRIVATE KEY-----' # private key block
  'ghp_[A-Za-z0-9]{36}'               # GitHub personal token
  'gho_[A-Za-z0-9]{36}'               # GitHub oauth token
)

# Never scan the example file (placeholders by design) or this script.
EXCLUDE_RE='^(\.env\.example|scripts/secret-scan\.sh)$'

found=0
while IFS= read -r file; do
  [[ "$file" =~ $EXCLUDE_RE ]] && continue
  [[ -f "$file" ]] || continue
  for pat in "${PATTERNS[@]}"; do
    if grep -nIEq "$pat" "$file"; then
      echo "POTENTIAL SECRET in $file (pattern: $pat)"
      found=1
    fi
  done
done < <(git ls-files)

if [[ "$found" -ne 0 ]]; then
  echo "secret-scan: failed. Remove the secret and use env vars / .env (gitignored)."
  exit 1
fi
echo "secret-scan: clean"
