#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
PUBLIC_REPO_URL="${PUBLIC_REPO_URL:?PUBLIC_REPO_URL is required}"
PUBLIC_BRANCH="${PUBLIC_BRANCH:-main}"
SYNC_COMMIT_MESSAGE="${SYNC_COMMIT_MESSAGE:?SYNC_COMMIT_MESSAGE is required}"
SYNC_BOT_NAME="${SYNC_BOT_NAME:-preview-sync[bot]}"
SYNC_BOT_EMAIL="${SYNC_BOT_EMAIL:-41898282+github-actions[bot]@users.noreply.github.com}"

temp_dir="$(mktemp -d)"
cleanup() {
  rm -rf "$temp_dir"
}
trap cleanup EXIT

git clone --quiet --branch "$PUBLIC_BRANCH" --single-branch "$PUBLIC_REPO_URL" "$temp_dir/public"

git -C "$temp_dir/public" rm -r -q --ignore-unmatch .
git -C "$ROOT_DIR" archive --format=tar HEAD | tar -xf - -C "$temp_dir/public"
git -C "$temp_dir/public" add -A

if git -C "$temp_dir/public" diff --cached --quiet; then
  echo "Public repository already matches preview."
  exit 0
fi

git -C "$temp_dir/public" config user.name "$SYNC_BOT_NAME"
git -C "$temp_dir/public" config user.email "$SYNC_BOT_EMAIL"
git -C "$temp_dir/public" commit -m "$SYNC_COMMIT_MESSAGE"
git -C "$temp_dir/public" push origin "$PUBLIC_BRANCH"
