#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"
require_command docker
load_env

INPUT_FILE="${1:-}"
if [ -z "$INPUT_FILE" ] || [ ! -f "$INPUT_FILE" ]; then echo "Usage: bash scripts/restore-media.sh BACKUP.tar.gz" >&2; exit 1; fi
ABS_INPUT="$(cd "$(dirname "$INPUT_FILE")" && pwd)/$(basename "$INPUT_FILE")"
docker run --rm -v "${COMPOSE_PROJECT_NAME:-newswebsite}_media_data:/target" -v "$ABS_INPUT:/backup.tar.gz:ro" alpine:3.22 sh -c 'find /target -mindepth 1 -delete && tar -xzf /backup.tar.gz -C /target'
echo "Media restore completed."
