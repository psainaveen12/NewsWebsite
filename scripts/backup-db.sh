#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

require_command docker
load_env

TARGET_DIR="$(backup_root)/db"
STAMP="$(timestamp)"
OUTPUT_FILE="$TARGET_DIR/newswebsite-$STAMP.sql.gz"

mkdir -p "$TARGET_DIR"
docker_compose exec -T db sh -c \
  'exec pg_dump --clean --if-exists --no-owner --no-privileges -U "$POSTGRES_USER" "$POSTGRES_DB"' \
  | gzip > "$OUTPUT_FILE"

find "$TARGET_DIR" -type f -name '*.sql.gz' -mtime +"${BACKUP_RETENTION_DAYS:-14}" -delete
echo "Database backup written to $OUTPUT_FILE"
