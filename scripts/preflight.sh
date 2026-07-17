#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"
require_command docker
load_env

required=(APP_BASE_URL APP_DOMAIN POSTGRES_DB POSTGRES_USER POSTGRES_PASSWORD DATABASE_URL SESSION_SECRET ADMIN_USERNAME ADMIN_PASSWORD)
for variable in "${required[@]}"; do
  if [ -z "${!variable:-}" ]; then echo "Missing required variable: $variable" >&2; exit 1; fi
done

if [ "${APP_ENV:-development}" = "production" ]; then
  [ "$APP_BASE_URL" = "https://$APP_DOMAIN" ] || { echo "Production APP_BASE_URL must be https://$APP_DOMAIN" >&2; exit 1; }
  case ",${COMPOSE_PROFILES:-}," in *,cloudflare,*) ;; *) echo "Production COMPOSE_PROFILES must include cloudflare" >&2; exit 1;; esac
  token_file="${CLOUDFLARE_TUNNEL_TOKEN_FILE:-./secrets/cloudflare-tunnel-token}"
  [[ "$token_file" = /* ]] || token_file="$PROJECT_ROOT/${token_file#./}"
  [ -s "$token_file" ] || { echo "Missing Cloudflare tunnel token file: $token_file" >&2; exit 1; }
  [ "${#SESSION_SECRET}" -ge 32 ] || { echo "SESSION_SECRET must have at least 32 characters" >&2; exit 1; }
  [ "${#ADMIN_PASSWORD}" -ge 16 ] || { echo "ADMIN_PASSWORD must have at least 16 characters" >&2; exit 1; }
  case "$POSTGRES_PASSWORD$SESSION_SECRET$ADMIN_PASSWORD" in *replace-with*|*change-me*) echo "Replace every placeholder secret" >&2; exit 1;; esac
fi

docker_compose config --quiet
echo "Preflight checks passed."
