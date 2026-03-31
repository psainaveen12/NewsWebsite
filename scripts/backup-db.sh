#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

require_command docker
require_command gzip
load_env

TARGET_DIR="$(backup_root)/db"
STAMP="$(timestamp)"
OUTPUT_FILE="$TARGET_DIR/db-$STAMP.sql.gz"

mkdir -p "$TARGET_DIR"
docker_compose exec -T db sh -c 'exec mariadb-dump --single-transaction --quick -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"' \
  | gzip > "$OUTPUT_FILE"

find "$TARGET_DIR" -type f -name '*.sql.gz' -mtime +"${BACKUP_RETENTION_DAYS:-14}" -delete
echo "Database backup written to $OUTPUT_FILE"
