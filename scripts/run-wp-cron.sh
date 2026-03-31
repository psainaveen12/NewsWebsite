#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if bash "$PROJECT_ROOT/scripts/wp-cli.sh" core is-installed >/dev/null 2>&1; then
  bash "$PROJECT_ROOT/scripts/wp-cli.sh" cron event run --due-now
else
  echo "WordPress is not installed yet; skipping cron run."
fi
