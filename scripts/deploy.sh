#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"
require_command docker
require_command git
load_env

BRANCH="${DEPLOY_BRANCH:-${1:-NewsWebsiteDocker}}"
cd "$PROJECT_ROOT"

git fetch origin "$BRANCH"
if [ "$(git branch --show-current)" != "$BRANCH" ]; then
  git checkout "$BRANCH"
fi
git pull --ff-only origin "$BRANCH"

bash "$PROJECT_ROOT/scripts/preflight.sh"
docker_compose build --pull
docker_compose up -d --remove-orphans
docker_compose exec -T caddy caddy reload --config /etc/caddy/Caddyfile
bash "$PROJECT_ROOT/scripts/healthcheck.sh"
docker image prune -f
