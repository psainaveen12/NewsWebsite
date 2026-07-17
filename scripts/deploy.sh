#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"
require_command docker
require_command git
load_env

BRANCH="${DEPLOY_BRANCH:-${1:-NewsWebsiteGCP}}"
cd "$PROJECT_ROOT"

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Deployment stopped: tracked files have uncommitted changes." >&2
  exit 1
fi

if docker_compose ps --status running --services 2>/dev/null | grep -qx db; then
  bash "$PROJECT_ROOT/scripts/backup-db.sh"
  bash "$PROJECT_ROOT/scripts/backup-media.sh"
fi

git fetch origin "$BRANCH"
if [ "$(git branch --show-current)" != "$BRANCH" ]; then
  git checkout "$BRANCH"
fi
git pull --ff-only origin "$BRANCH"

bash "$PROJECT_ROOT/scripts/preflight.sh"
docker_compose build --pull
docker_compose up -d --remove-orphans
bash "$PROJECT_ROOT/scripts/healthcheck.sh"
docker image prune -f
