#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

require_command docker
require_command git
load_env

BRANCH="${DEPLOY_BRANCH:-${1:-main}}"

cd "$PROJECT_ROOT"
git fetch origin "$BRANCH"

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
  git checkout "$BRANCH"
fi

git pull --ff-only origin "$BRANCH"
docker_compose config -q
docker_compose pull
docker_compose up -d --remove-orphans
docker image prune -f
docker_compose ps
