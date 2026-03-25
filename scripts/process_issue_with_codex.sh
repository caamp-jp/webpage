#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/process_issue_with_codex.sh [options] ISSUE_NUMBER

Read a GitHub issue, let Codex determine whether it is a page/site update for this
repository, and if so implement the change, create a branch, open a PR, and
comment on the issue.

Options:
  --repo OWNER/REPO        GitHub repository that owns the issue and PR
                           Default: caamp-jp/preview
  --base-remote NAME       Git remote used for fetch/push
                           Default: auto-detected from --repo, else preview, else origin
  --base-branch NAME       Base branch for the worktree and PR
                           Default: repository default branch
  -h, --help               Show this help

Environment overrides:
  CODEX_MODEL              Default: gpt-5.4
  CODEX_REASONING_EFFORT   Default: medium
EOF
}

log() {
  printf '[codex-issue] %s\n' "$*"
}

die() {
  printf '[codex-issue] %s\n' "$*" >&2
  exit 1
}

require_command() {
  local command_name="$1"
  command -v "$command_name" >/dev/null 2>&1 || die "Required command not found: $command_name"
}

detect_base_remote() {
  local target_repo="$1"
  local remote_name
  local remote_url

  while IFS=$'\t' read -r remote_name remote_url; do
    if [[ "$remote_url" == *"${target_repo}.git"* ]] || [[ "$remote_url" == *"${target_repo}" ]]; then
      printf '%s\n' "$remote_name"
      return 0
    fi
  done < <(git remote -v | awk '$3 == "(fetch)" {print $1 "\t" $2}')

  if git remote get-url preview >/dev/null 2>&1; then
    printf 'preview\n'
    return 0
  fi

  if git remote get-url origin >/dev/null 2>&1; then
    printf 'origin\n'
    return 0
  fi

  return 1
}

cleanup_tempdir() {
  if [[ -n "${TEMP_DIR:-}" && -d "${TEMP_DIR:-}" ]]; then
    rm -rf "$TEMP_DIR"
  fi
}

cleanup_worktree() {
  if [[ -n "${WORKTREE_DIR:-}" && -d "${WORKTREE_DIR:-}" ]]; then
    git worktree remove --force "$WORKTREE_DIR" >/dev/null 2>&1 || rm -rf "$WORKTREE_DIR"
  fi
}

TARGET_REPO="caamp-jp/preview"
BASE_REMOTE=""
BASE_BRANCH=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      [[ $# -ge 2 ]] || die "--repo requires a value"
      TARGET_REPO="$2"
      shift 2
      ;;
    --base-remote)
      [[ $# -ge 2 ]] || die "--base-remote requires a value"
      BASE_REMOTE="$2"
      shift 2
      ;;
    --base-branch)
      [[ $# -ge 2 ]] || die "--base-branch requires a value"
      BASE_BRANCH="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    -*)
      die "Unknown option: $1"
      ;;
    *)
      break
      ;;
  esac
done

[[ $# -eq 1 ]] || {
  usage >&2
  exit 1
}

ISSUE_NUMBER="$1"
[[ "$ISSUE_NUMBER" =~ ^[0-9]+$ ]] || die "Issue number must be numeric"

require_command git
require_command gh
require_command codex
require_command python3

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

if [[ -z "$BASE_REMOTE" ]]; then
  BASE_REMOTE="$(detect_base_remote "$TARGET_REPO")" || die "Could not detect a git remote for $TARGET_REPO"
fi

if [[ -z "$BASE_BRANCH" ]]; then
  BASE_BRANCH="$(gh repo view "$TARGET_REPO" --json defaultBranchRef --jq '.defaultBranchRef.name')"
fi

CODEX_MODEL="${CODEX_MODEL:-gpt-5.4}"
CODEX_REASONING_EFFORT="${CODEX_REASONING_EFFORT:-medium}"
BRANCH_NAME="codex/issue-${ISSUE_NUMBER}"
WORKTREE_DIR="$(mktemp -d "${TMPDIR:-/tmp}/codex-issue-${ISSUE_NUMBER}.XXXXXX")"

if git show-ref --verify --quiet "refs/heads/$BRANCH_NAME"; then
  die "Local branch already exists: $BRANCH_NAME"
fi

if git ls-remote --exit-code --heads "$BASE_REMOTE" "$BRANCH_NAME" >/dev/null 2>&1; then
  die "Remote branch already exists on $BASE_REMOTE: $BRANCH_NAME"
fi

TEMP_DIR="$(mktemp -d)"
trap 'cleanup_worktree; cleanup_tempdir' EXIT

ISSUE_JSON_FILE="$TEMP_DIR/issue.json"
PROMPT_FILE="$TEMP_DIR/prompt.txt"
SCHEMA_FILE="$TEMP_DIR/result-schema.json"
RESULT_FILE="$TEMP_DIR/result.json"
PARSED_ENV_FILE="$TEMP_DIR/result.env"
PR_BODY_FILE="$TEMP_DIR/pr-body.md"
ISSUE_COMMENT_FILE="$TEMP_DIR/issue-comment.md"

log "Fetching issue #$ISSUE_NUMBER from $TARGET_REPO"
gh issue view "$ISSUE_NUMBER" \
  -R "$TARGET_REPO" \
  --json number,title,body,url,labels,author,assignees,comments \
  > "$ISSUE_JSON_FILE"

cat > "$SCHEMA_FILE" <<'EOF'
{
  "type": "object",
  "additionalProperties": false,
  "required": [
    "result",
    "summary",
    "commit_message",
    "pr_title",
    "pr_body",
    "issue_comment"
  ],
  "properties": {
    "result": {
      "type": "string",
      "enum": ["not_applicable", "changed"]
    },
    "summary": {
      "type": "string"
    },
    "commit_message": {
      "type": "string"
    },
    "pr_title": {
      "type": "string"
    },
    "pr_body": {
      "type": "string"
    },
    "issue_comment": {
      "type": "string"
    }
  }
}
EOF

cat > "$PROMPT_FILE" <<EOF
You are working in the repository at $WORKTREE_DIR.

The current branch has already been prepared for Issue #$ISSUE_NUMBER. Do not create commits,
push, open a PR, or comment on GitHub. Only inspect the issue, edit files when appropriate,
verify the result locally, and return JSON matching the provided schema.

Issue context is stored in:
$ISSUE_JSON_FILE

Repository-specific constraints:
- This repo manages the static site for caamp.jp.
- Prefer updating SITE_CONTENT.json, X_EMBED.txt, and generators/scripts instead of hand-editing generated docs.
- If structure or content changes, regenerate docs with: python3 scripts/build_site_from_json.py
- Validate generated output with: scripts/check_generated_docs.sh
- Keep links relative and follow the repository instructions in AGENTS.md.

Task:
1. Read the issue context from the JSON file above.
2. Decide whether the issue is a page/site update request that should be implemented in this repository.
3. If it is not applicable, make no file changes and return result="not_applicable" with a short Japanese summary.
4. If it is applicable, implement the requested changes in the working tree.
5. Run the necessary local verification commands.
6. Return concise Japanese strings for:
   - summary
   - commit_message
   - pr_title
   - pr_body
   - issue_comment

Output requirements:
- Return only JSON matching the schema.
- If result="changed", all string fields must be non-empty.
- issue_comment must NOT include a leading "Codexが生成したコメントです。" line because the wrapper script adds it.
- pr_body must NOT include a leading "Codexが生成したコメントです。" line because the wrapper script adds it.
- pr_body should be ready to use as a GitHub PR body and should include "Closes #$ISSUE_NUMBER" when appropriate.
EOF

log "Fetching $BASE_REMOTE/$BASE_BRANCH"
git fetch "$BASE_REMOTE" "$BASE_BRANCH"

log "Creating isolated worktree $WORKTREE_DIR on branch $BRANCH_NAME"
git worktree add -b "$BRANCH_NAME" "$WORKTREE_DIR" "$BASE_REMOTE/$BASE_BRANCH" >/dev/null

verify_generated_output() {
  local worktree="$1"
  local snapshot_dir

  snapshot_dir="$(mktemp -d "${TMPDIR:-/tmp}/codex-verify.XXXXXX")"
  cp -R "$worktree/docs" "$snapshot_dir/docs"
  (
    cd "$worktree"
    python3 scripts/build_site_from_json.py
  )
  if ! diff -qr "$snapshot_dir/docs" "$worktree/docs" >/dev/null 2>&1; then
    rm -rf "$snapshot_dir"
    die "Generated docs changed when rebuilt; docs are not in sync with source content"
  fi
  rm -rf "$snapshot_dir"
}

log "Running Codex with model=$CODEX_MODEL effort=$CODEX_REASONING_EFFORT"
codex exec \
  -C "$WORKTREE_DIR" \
  -m "$CODEX_MODEL" \
  -c 'approval_policy="never"' \
  -c "model_reasoning_effort=\"$CODEX_REASONING_EFFORT\"" \
  -s danger-full-access \
  --color never \
  --output-schema "$SCHEMA_FILE" \
  -o "$RESULT_FILE" \
  - < "$PROMPT_FILE"

python3 - "$RESULT_FILE" "$PARSED_ENV_FILE" <<'PY'
import json
import shlex
import sys

result_path, env_path = sys.argv[1], sys.argv[2]
with open(result_path, encoding="utf-8") as fh:
    data = json.load(fh)

keys = [
    "result",
    "summary",
    "commit_message",
    "pr_title",
    "pr_body",
    "issue_comment",
]

with open(env_path, "w", encoding="utf-8") as fh:
    for key in keys:
        value = data.get(key, "")
        if value is None:
            value = ""
        fh.write(f"{key.upper()}={shlex.quote(str(value))}\n")
PY

# shellcheck source=/dev/null
source "$PARSED_ENV_FILE"

if [[ "$RESULT" == "not_applicable" ]]; then
  log "Issue #$ISSUE_NUMBER is not applicable: $SUMMARY"
  git branch -D "$BRANCH_NAME" >/dev/null 2>&1 || true
  exit 0
fi

[[ "$RESULT" == "changed" ]] || die "Unexpected result from Codex: $RESULT"
[[ -n "$COMMIT_MESSAGE" ]] || die "Codex returned an empty commit message"
[[ -n "$PR_TITLE" ]] || die "Codex returned an empty PR title"
[[ -n "$PR_BODY" ]] || die "Codex returned an empty PR body"
[[ -n "$ISSUE_COMMENT" ]] || die "Codex returned an empty issue comment"

if [[ -z "$(git -C "$WORKTREE_DIR" status --short --untracked-files=all)" ]]; then
  die "Codex reported changes, but the working tree is clean"
fi

log "Running final verification"
verify_generated_output "$WORKTREE_DIR"

log "Creating commit"
git -C "$WORKTREE_DIR" add -A
git -C "$WORKTREE_DIR" commit -m "$COMMIT_MESSAGE"

log "Pushing branch to $BASE_REMOTE"
git -C "$WORKTREE_DIR" push -u "$BASE_REMOTE" "$BRANCH_NAME"

python3 - "$PR_BODY_FILE" "$PR_BODY" <<'PY'
import sys

path, body = sys.argv[1], sys.argv[2].strip()
with open(path, "w", encoding="utf-8") as fh:
    fh.write("Codexが生成したコメントです。\n\n")
    if body:
        fh.write(body)
        fh.write("\n")
PY

log "Creating pull request in $TARGET_REPO"
PR_URL="$(gh pr create \
  -R "$TARGET_REPO" \
  --base "$BASE_BRANCH" \
  --head "$BRANCH_NAME" \
  --title "$PR_TITLE" \
  --body-file "$PR_BODY_FILE")"

python3 - "$ISSUE_COMMENT_FILE" "$ISSUE_COMMENT" "$PR_URL" <<'PY'
import sys

path, body, pr_url = sys.argv[1], sys.argv[2].strip(), sys.argv[3].strip()
with open(path, "w", encoding="utf-8") as fh:
    fh.write("Codexが生成したコメントです。\n\n")
    if body:
        fh.write(body)
        fh.write("\n\n")
    fh.write(f"PR: {pr_url}\n")
PY

log "Commenting on issue #$ISSUE_NUMBER"
gh issue comment "$ISSUE_NUMBER" -R "$TARGET_REPO" --body-file "$ISSUE_COMMENT_FILE"

log "Completed: $PR_URL"
