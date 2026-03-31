#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

require_command docker
load_env

TARGET_DIR="$(backup_root)/wp"
STAMP="$(timestamp)"
OUTPUT_FILE="$TARGET_DIR/wp-content-$STAMP.tar.gz"

ensure_directory "$TARGET_DIR"
docker_compose exec -T wordpress sh -lc '
  set -eu
  cd /var/www/html
  paths=""
  for path in wp-content/uploads wp-content/plugins; do
    if [ -e "$path" ]; then
      paths="$paths $path"
    fi
  done
  if [ -z "$paths" ]; then
    echo "No WordPress content paths found to archive." >&2
    exit 1
  fi
  # shellcheck disable=SC2086
  tar -czf - $paths
' > "$OUTPUT_FILE"

find "$TARGET_DIR" -type f -name '*.tar.gz' -mtime +"${BACKUP_RETENTION_DAYS:-14}" -delete
echo "WordPress content backup written to $OUTPUT_FILE"
