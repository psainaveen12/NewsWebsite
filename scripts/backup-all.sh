#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"
load_env
bash "$SCRIPT_DIR/backup-db.sh"
bash "$SCRIPT_DIR/backup-media.sh"

if [ -n "${OFFSITE_BACKUP_COMMAND:-}" ]; then
  bash -lc "$OFFSITE_BACKUP_COMMAND"
fi
