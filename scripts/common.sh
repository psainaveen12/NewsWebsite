#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${COMPOSE_FILE:-$PROJECT_ROOT/docker-compose.yml}"
ENV_FILE="${ENV_FILE:-$PROJECT_ROOT/.env}"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Required command not found: $1" >&2
    exit 1
  fi
}

load_env() {
  if [ ! -f "$ENV_FILE" ]; then
    echo "Missing environment file: $ENV_FILE" >&2
    exit 1
  fi

  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
}

docker_compose() {
  docker compose --project-directory "$PROJECT_ROOT" --file "$COMPOSE_FILE" --env-file "$ENV_FILE" "$@"
}

timestamp() {
  date +%F-%H%M%S
}

backup_root() {
  local root="${BACKUP_ROOT:-$PROJECT_ROOT/backups}"
  if [[ "$root" = /* ]]; then printf '%s\n' "$root"; else printf '%s\n' "$PROJECT_ROOT/${root#./}"; fi
}
