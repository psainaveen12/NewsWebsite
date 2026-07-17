#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"
require_command curl
require_command docker
load_env

failures=()
for service in db app caddy; do
  docker_compose ps --status running --services | grep -qx "$service" || failures+=("$service container is not running")
done
curl -fsS --max-time 15 "$APP_BASE_URL/healthz" >/dev/null || failures+=("HTTPS health check failed")

disk_used="$(df -P "$PROJECT_ROOT" | awk 'NR==2 {gsub(/%/, "", $5); print $5}')"
if [ "$disk_used" -ge "${MONITOR_DISK_PERCENT:-85}" ]; then
  failures+=("disk usage is ${disk_used}%")
fi

if [ "${#failures[@]}" -gt 0 ]; then
  message="NewsWebsite monitor: $(IFS='; '; echo "${failures[*]}")"
  echo "$message" >&2
  if [ -n "${MONITOR_WEBHOOK_URL:-}" ]; then
    payload="$(printf '%s' "$message" | jq -Rs '{text: .}')"
    curl -fsS -X POST -H 'Content-Type: application/json' --data "$payload" "$MONITOR_WEBHOOK_URL" >/dev/null || true
  fi
  exit 1
fi

echo "$(date -Is) NewsWebsite health, containers and disk checks passed."
