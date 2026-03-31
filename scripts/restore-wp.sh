#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

require_command docker
load_env

INPUT_FILE="${1:-}"
if [ -z "$INPUT_FILE" ] || [ ! -f "$INPUT_FILE" ]; then
  echo "Usage: bash scripts/restore-wp.sh /path/to/wp-content-backup.tar.gz" >&2
  exit 1
fi

cat "$INPUT_FILE" | docker_compose exec -T wordpress sh -lc '
  set -eu
  cd /var/www/html
  rm -rf wp-content/uploads wp-content/plugins
  tar -xzf - -C .
'

echo "WordPress content restore completed from $INPUT_FILE"
