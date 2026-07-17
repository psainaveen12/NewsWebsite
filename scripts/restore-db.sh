#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"
require_command docker
load_env

INPUT_FILE="${1:-}"
if [ -z "$INPUT_FILE" ] || [ ! -f "$INPUT_FILE" ]; then echo "Usage: bash scripts/restore-db.sh BACKUP.sql[.gz]" >&2; exit 1; fi
if [[ "$INPUT_FILE" == *.gz ]]; then gzip -dc "$INPUT_FILE"; else cat "$INPUT_FILE"; fi | docker_compose exec -T db psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"
echo "Database restore completed."
