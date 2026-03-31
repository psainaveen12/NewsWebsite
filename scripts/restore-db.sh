#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

require_command docker
load_env

INPUT_FILE="${1:-}"
if [ -z "$INPUT_FILE" ] || [ ! -f "$INPUT_FILE" ]; then
  echo "Usage: bash scripts/restore-db.sh /path/to/db-backup.sql.gz" >&2
  exit 1
fi

if [[ "$INPUT_FILE" = *.gz ]]; then
  gzip -dc "$INPUT_FILE"
else
  cat "$INPUT_FILE"
fi | docker_compose exec -T db sh -c 'exec mariadb -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"'

echo "Database restore completed from $INPUT_FILE"
