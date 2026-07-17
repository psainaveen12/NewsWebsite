#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"
require_command docker
load_env

for attempt in $(seq 1 30); do
  tunnel_ready=true
  if [[ ",${COMPOSE_PROFILES:-}," = *,cloudflare,* ]]; then
    docker_compose ps --status running --services | grep -qx cloudflared || tunnel_ready=false
  fi
  if $tunnel_ready && docker_compose exec -T app python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz',timeout=4)" >/dev/null 2>&1; then
    docker_compose exec -T app python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/healthz',timeout=4).read().decode())"
    echo "Application${COMPOSE_PROFILES:+ and Cloudflare Tunnel} health checks passed."
    exit 0
  fi
  sleep 2
done

docker_compose ps
docker_compose logs --tail=80 app db cloudflared
echo "Application did not become healthy." >&2
exit 1
