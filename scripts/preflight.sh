#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

require_command docker
load_env

required_vars=(
  PRIMARY_DOMAIN
  APEX_DOMAIN
  WP_HOME
  WP_SITEURL
  TLS_EMAIL
  DB_NAME
  DB_USER
  DB_PASSWORD
  DB_ROOT_PASSWORD
  WORDPRESS_TABLE_PREFIX
  AUTH_KEY
  SECURE_AUTH_KEY
  LOGGED_IN_KEY
  NONCE_KEY
  AUTH_SALT
  SECURE_AUTH_SALT
  LOGGED_IN_SALT
  NONCE_SALT
  BACKUP_ROOT
)

secret_vars=(
  DB_PASSWORD
  DB_ROOT_PASSWORD
  AUTH_KEY
  SECURE_AUTH_KEY
  LOGGED_IN_KEY
  NONCE_KEY
  AUTH_SALT
  SECURE_AUTH_SALT
  LOGGED_IN_SALT
  NONCE_SALT
)

require_env_vars "${required_vars[@]}"

for secret_var in "${secret_vars[@]}"; do
  secret_value="${!secret_var:-}"

  if [[ "$secret_value" == replace-with-* ]] || [[ "$secret_value" == changeme* ]]; then
    echo "Environment variable $secret_var still uses a placeholder value." >&2
    exit 1
  fi
done

if [ "$PRIMARY_DOMAIN" = "$APEX_DOMAIN" ]; then
  echo "PRIMARY_DOMAIN and APEX_DOMAIN must be different so the apex can redirect cleanly." >&2
  exit 1
fi

if [ "$WP_HOME" != "https://$PRIMARY_DOMAIN" ]; then
  echo "WP_HOME should match https://$PRIMARY_DOMAIN for this stack." >&2
  exit 1
fi

if [ "$WP_SITEURL" != "$WP_HOME" ]; then
  echo "WP_SITEURL should match WP_HOME for this stack." >&2
  exit 1
fi

if [[ "$TLS_EMAIL" != *@* ]]; then
  echo "TLS_EMAIL must be a valid mailbox for certificate issuance notices." >&2
  exit 1
fi

ensure_directory "$(backup_root)/db"
ensure_directory "$(backup_root)/wp"

docker info >/dev/null 2>&1
docker_compose config -q

echo "Preflight checks passed."
