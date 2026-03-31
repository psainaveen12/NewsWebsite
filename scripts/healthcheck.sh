#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

require_command docker
load_env

QUIET=false
CHECK_EXTERNAL=false

for arg in "$@"; do
  case "$arg" in
    --quiet)
      QUIET=true
      ;;
    --external)
      CHECK_EXTERNAL=true
      ;;
    *)
      echo "Unknown option: $arg" >&2
      echo "Usage: bash scripts/healthcheck.sh [--quiet] [--external]" >&2
      exit 1
      ;;
  esac
done

log() {
  if [ "$QUIET" != "true" ]; then
    echo "$1"
  fi
}

fail() {
  echo "Healthcheck failed: $1" >&2
  exit 1
}

assert_service_status() {
  local service_name="$1"
  local expected_health="$2"
  local actual_state
  local actual_health

  actual_state="$(service_state "$service_name" 2>/dev/null || true)"
  actual_health="$(service_health "$service_name" 2>/dev/null || true)"

  if [ -z "$actual_state" ]; then
    fail "service '$service_name' is not running."
  fi

  if [ "$expected_health" = "running" ]; then
    if [ "$actual_state" != "running" ]; then
      fail "service '$service_name' state is '$actual_state', expected 'running'."
    fi
  elif [ "$actual_health" != "$expected_health" ]; then
    fail "service '$service_name' health is '$actual_health', expected '$expected_health'."
  fi

  log "Service '$service_name' is $actual_health."
}

assert_service_status db healthy
assert_service_status wordpress healthy
assert_service_status caddy running

docker_compose exec -T wordpress php -r '
$body = @file_get_contents("http://127.0.0.1/wp-login.php");
if ($body === false) {
    fwrite(STDERR, "WordPress local HTTP endpoint is unreachable.\n");
    exit(1);
}
' >/dev/null || fail "WordPress did not answer on its local HTTP endpoint."

log "WordPress local HTTP endpoint is reachable."

if [ "$CHECK_EXTERNAL" = "true" ]; then
  require_command curl
  curl --fail --silent --show-error "https://${PRIMARY_DOMAIN}/healthz" >/dev/null \
    || fail "Primary HTTPS health endpoint https://${PRIMARY_DOMAIN}/healthz is unreachable."
  log "Primary HTTPS health endpoint is reachable."
fi

log "Healthcheck passed."
