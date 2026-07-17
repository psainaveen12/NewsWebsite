#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"
require_command docker
require_command git
load_env

REF="${1:-}"
[ -n "$REF" ] || { echo "Usage: bash scripts/rollback.sh GOOD_GIT_COMMIT" >&2; exit 1; }
cd "$PROJECT_ROOT"
git diff --quiet && git diff --cached --quiet || { echo "Rollback requires a clean worktree." >&2; exit 1; }
git rev-parse --verify "$REF^{commit}" >/dev/null

bash "$PROJECT_ROOT/scripts/backup-all.sh"
ORIGINAL_BRANCH="$(git branch --show-current)"
git switch --detach "$REF"
if docker_compose build && docker_compose up -d --remove-orphans && bash "$PROJECT_ROOT/scripts/healthcheck.sh"; then
  echo "Application code is running from $REF. Data volumes were preserved."
  echo "Run 'git switch $ORIGINAL_BRANCH' before the next normal deployment."
else
  git switch "$ORIGINAL_BRANCH"
  echo "Rollback build failed; returned to $ORIGINAL_BRANCH." >&2
  exit 1
fi
