#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"
require_command docker
load_env

for attempt in $(seq 1 30); do
  if docker_compose exec -T nginx wget -qO- http://127.0.0.1:8080/nginx-health >/dev/null 2>&1 \
    && docker_compose exec -T app python -c "import urllib.request; urllib.request.urlopen('http://nginx:8080/healthz',timeout=4)" >/dev/null 2>&1; then
    docker_compose exec -T app python -c "import urllib.request; print(urllib.request.urlopen('http://nginx:8080/healthz',timeout=4).read().decode())"
    echo "Nginx and application health checks passed."
    exit 0
  fi
  sleep 2
done

docker_compose ps
docker_compose logs --tail=80 app nginx db caddy
echo "Application did not become healthy." >&2
exit 1
