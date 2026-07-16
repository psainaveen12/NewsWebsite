#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

require_command docker
require_command git

BRANCH="${DEPLOY_BRANCH:-${1:-NewsWebsite-Docker}}"
git check-ref-format --branch "$BRANCH" >/dev/null

cd "$PROJECT_ROOT"
if [ ! -d .git ]; then
  echo "Deployment directory is not a Git repository: $PROJECT_ROOT" >&2
  exit 1
fi
if [ ! -f "$ENV_FILE" ]; then
  echo "Create $ENV_FILE from .env.example and set production secrets before deploying." >&2
  exit 1
fi

git fetch --prune origin "$BRANCH"
git checkout "$BRANCH"
git merge --ff-only "origin/$BRANCH"

bash "$PROJECT_ROOT/scripts/preflight.sh"
docker_compose build --pull
docker_compose up -d --remove-orphans
docker_compose ps
bash "$PROJECT_ROOT/scripts/healthcheck.sh"
