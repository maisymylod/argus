#!/usr/bin/env bash
# Local bootstrap: create .env, optional Python dev tooling, then bring the stack up.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example (edit it to add ANTHROPIC_API_KEY when needed)."
fi

if command -v pre-commit >/dev/null 2>&1; then
  pre-commit install
  echo "pre-commit hooks installed."
else
  echo "pre-commit not found; skipping hook install (pip install pre-commit to enable)."
fi

echo "Bootstrap complete. Run 'make up' to start the stack."
