#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "Run this script as root." >&2
  exit 1
fi

APP_USER="${APP_USER:-ubuntu}"
APP_DIR="${APP_DIR:-/home/${APP_USER}/apps/ieltstask}"
LOG_DIR="${LOG_DIR:-/var/log/ieltstask}"
CRON_FILE="/etc/cron.d/ieltstask"

APP_GROUP="$(id -gn "$APP_USER")"

install -m 0755 -o "$APP_USER" -g "$APP_GROUP" -d "$LOG_DIR"

cat >"$CRON_FILE" <<EOF
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

0 2 * * * ${APP_USER} cd ${APP_DIR} && bash scripts/backup-db.sh >> ${LOG_DIR}/backup-db.log 2>&1
20 2 * * * ${APP_USER} cd ${APP_DIR} && bash scripts/backup-wp.sh >> ${LOG_DIR}/backup-wp.log 2>&1
*/5 * * * * ${APP_USER} cd ${APP_DIR} && bash scripts/run-wp-cron.sh >> ${LOG_DIR}/wp-cron.log 2>&1
*/10 * * * * ${APP_USER} cd ${APP_DIR} && bash scripts/healthcheck.sh --external --quiet >> ${LOG_DIR}/healthcheck.log 2>&1
EOF

chmod 0644 "$CRON_FILE"
systemctl enable --now cron

echo "Installed cron jobs at $CRON_FILE"
