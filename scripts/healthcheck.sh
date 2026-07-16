#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

require_command docker
load_env

attempts="${HEALTHCHECK_ATTEMPTS:-20}"
for ((attempt = 1; attempt <= attempts; attempt++)); do
  if docker_compose exec -T app python -c \
    "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=3)" \
    >/dev/null 2>&1; then
    echo "Application health check passed."
    exit 0
  fi
  sleep 3
done

echo "Application health check failed after $attempts attempts." >&2
docker_compose ps >&2
docker_compose logs --tail=100 app db >&2
exit 1
