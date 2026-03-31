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

require_env_vars() {
  local missing=0

  for var_name in "$@"; do
    if [ -z "${!var_name:-}" ]; then
      echo "Missing required environment variable: $var_name" >&2
      missing=1
    fi
  done

  if [ "$missing" -ne 0 ]; then
    exit 1
  fi
}

docker_compose() {
  if docker compose version >/dev/null 2>&1; then
    docker compose --project-directory "$PROJECT_ROOT" --file "$COMPOSE_FILE" --env-file "$ENV_FILE" "$@"
  elif command -v docker-compose >/dev/null 2>&1; then
    docker-compose --project-directory "$PROJECT_ROOT" --file "$COMPOSE_FILE" --env-file "$ENV_FILE" "$@"
  else
    echo "Docker Compose is not installed. Install the Compose plugin or docker-compose first." >&2
    exit 1
  fi
}

timestamp() {
  date +%F-%H%M%S
}

backup_root() {
  printf '%s\n' "${BACKUP_ROOT:-$PROJECT_ROOT/backups}"
}

ensure_directory() {
  mkdir -p "$1"
}

service_container_id() {
  docker_compose ps -q "$1"
}

service_state() {
  local container_id

  container_id="$(service_container_id "$1")"
  if [ -z "$container_id" ]; then
    return 1
  fi

  docker inspect --format '{{.State.Status}}' "$container_id"
}

service_health() {
  local container_id

  container_id="$(service_container_id "$1")"
  if [ -z "$container_id" ]; then
    return 1
  fi

  docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$container_id"
}
