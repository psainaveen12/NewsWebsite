#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

require_command docker
load_env

required_variables=(
  APP_DOMAIN
  TLS_EMAIL
  DB_NAME
  DB_USER
  DB_PASSWORD
  ADMIN_USERNAME
  ADMIN_PASSWORD
  SESSION_SECRET
)

for variable in "${required_variables[@]}"; do
  value="${!variable:-}"
  if [ -z "$value" ]; then
    echo "Missing required value in .env: $variable" >&2
    exit 1
  fi
  case "$value" in
    replace-*|change-me*|development-*)
      echo "Replace placeholder value in .env: $variable" >&2
      exit 1
      ;;
  esac
done

if [ "${#DB_PASSWORD}" -lt 16 ]; then
  echo "DB_PASSWORD must be at least 16 characters." >&2
  exit 1
fi
if [ "${#ADMIN_PASSWORD}" -lt 12 ]; then
  echo "ADMIN_PASSWORD must be at least 12 characters." >&2
  exit 1
fi
if [ "${#SESSION_SECRET}" -lt 32 ]; then
  echo "SESSION_SECRET must be at least 32 characters." >&2
  exit 1
fi

docker_compose config --quiet
echo "Preflight validation passed."
