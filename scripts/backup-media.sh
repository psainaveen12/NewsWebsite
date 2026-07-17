#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"
require_command docker
load_env

TARGET_DIR="$(backup_root)/media"
mkdir -p "$TARGET_DIR"
OUTPUT_FILE="$TARGET_DIR/media-$(timestamp).tar.gz"
docker run --rm -v "${COMPOSE_PROJECT_NAME:-newswebsite}_media_data:/source:ro" -v "$TARGET_DIR:/backup" alpine:3.22 sh -c "cd /source && tar -czf /backup/$(basename "$OUTPUT_FILE") ."
find "$TARGET_DIR" -type f -name '*.tar.gz' -mtime +"${BACKUP_RETENTION_DAYS:-14}" -delete
echo "Media backup written to $OUTPUT_FILE"
