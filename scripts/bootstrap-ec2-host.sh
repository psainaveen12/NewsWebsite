#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "Run this script as root." >&2
  exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_USER="${TARGET_USER:-${SUDO_USER:-}}"
if [ -z "$TARGET_USER" ]; then
  if id ec2-user >/dev/null 2>&1; then
    TARGET_USER="ec2-user"
  else
    TARGET_USER="ubuntu"
  fi
fi
TARGET_GROUP="$(id -gn "$TARGET_USER")"
APP_DIR="${APP_DIR:-/home/${TARGET_USER}/apps/ieltstask}"
BACKUP_DIR="${BACKUP_DIR:-/home/${TARGET_USER}/backups/ieltstask}"
SWAP_SIZE_GB="${SWAP_SIZE_GB:-2}"

if command -v apt-get >/dev/null 2>&1; then
  apt-get update
  apt-get install -y cron unattended-upgrades apt-listchanges

  cat >/etc/apt/apt.conf.d/20auto-upgrades <<'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
EOF
elif command -v dnf >/dev/null 2>&1 || command -v yum >/dev/null 2>&1; then
  PACKAGE_MANAGER="dnf"
  if ! command -v dnf >/dev/null 2>&1; then
    PACKAGE_MANAGER="yum"
  fi

  "$PACKAGE_MANAGER" install -y cronie dnf-automatic
else
  echo "Unsupported package manager. This script currently supports apt, dnf, and yum." >&2
  exit 1
fi

if ! swapon --show | grep -q '^'; then
  fallocate -l "${SWAP_SIZE_GB}G" /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=$((SWAP_SIZE_GB * 1024))
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  grep -q '^/swapfile ' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

bash "$PROJECT_ROOT/scripts/install-docker-ubuntu.sh"
bash "$PROJECT_ROOT/scripts/harden-ubuntu.sh"

install -d -o "$TARGET_USER" -g "$TARGET_GROUP" "$APP_DIR"
install -d -o "$TARGET_USER" -g "$TARGET_GROUP" "$BACKUP_DIR"

if command -v apt-get >/dev/null 2>&1; then
  systemctl enable --now unattended-upgrades cron
else
  systemctl enable --now crond dnf-automatic.timer
fi

echo "EC2 bootstrap completed."
echo "Application directory: $APP_DIR"
echo "Backup directory: $BACKUP_DIR"
