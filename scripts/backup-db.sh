#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"
require_command docker
require_command gzip
load_env

TARGET_DIR="$(backup_root)/db"
mkdir -p "$TARGET_DIR"
OUTPUT_FILE="$TARGET_DIR/news-$(timestamp).sql.gz"
docker_compose exec -T db pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner --clean --if-exists | gzip > "$OUTPUT_FILE"
find "$TARGET_DIR" -type f -name '*.sql.gz' -mtime +"${BACKUP_RETENTION_DAYS:-14}" -delete
echo "Database backup written to $OUTPUT_FILE"
