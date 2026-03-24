#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

python3 scripts/build_site_from_json.py

docs_status="$(git status --short --untracked-files=all -- docs)"
if [ -n "$docs_status" ]; then
  echo "Generated docs are out of date. Rebuild docs and include the result in the PR."
  echo "$docs_status"
  git diff --stat -- docs || true
  exit 1
fi

echo "Generated docs are up to date."
