#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
command -v crontab >/dev/null || { echo "cron is not installed." >&2; exit 1; }
mkdir -p "$PROJECT_ROOT/backups"

current="$(crontab -l 2>/dev/null || true)"
filtered="$(printf '%s\n' "$current" | sed '/# BEGIN NEWSWEBSITE/,/# END NEWSWEBSITE/d')"
{
  printf '%s\n' "$filtered"
  echo "# BEGIN NEWSWEBSITE"
  echo "0 2 * * * cd $PROJECT_ROOT && bash scripts/backup-db.sh >> $PROJECT_ROOT/backups/operations.log 2>&1"
  echo "30 2 * * * cd $PROJECT_ROOT && bash scripts/backup-media.sh >> $PROJECT_ROOT/backups/operations.log 2>&1"
  echo "*/5 * * * * cd $PROJECT_ROOT && bash scripts/monitor.sh >> $PROJECT_ROOT/backups/monitor.log 2>&1"
  echo "15 3 * * 0 cd $PROJECT_ROOT && bash scripts/test-backups.sh >> $PROJECT_ROOT/backups/operations.log 2>&1"
  echo "# END NEWSWEBSITE"
} | crontab -

echo "Installed daily backups, five-minute monitoring, and weekly restore verification for $(id -un)."
