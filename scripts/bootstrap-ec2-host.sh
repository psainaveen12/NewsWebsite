#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "Run this script as root." >&2
  exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_USER="${TARGET_USER:-${SUDO_USER:-ubuntu}}"
TARGET_GROUP="$(id -gn "$TARGET_USER")"
APP_DIR="${APP_DIR:-/home/${TARGET_USER}/apps/ieltstask}"
BACKUP_DIR="${BACKUP_DIR:-/home/${TARGET_USER}/backups/ieltstask}"
SWAP_SIZE_GB="${SWAP_SIZE_GB:-2}"

apt update
apt install -y cron unattended-upgrades apt-listchanges

cat >/etc/apt/apt.conf.d/20auto-upgrades <<'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
EOF

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

systemctl enable --now unattended-upgrades cron

echo "EC2 bootstrap completed."
echo "Application directory: $APP_DIR"
echo "Backup directory: $BACKUP_DIR"
