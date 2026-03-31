#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "Run this script as root." >&2
  exit 1
fi

apt update
apt install -y ufw fail2ban

ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp

if [ "${UFW_FORCE_ENABLE:-false}" = "true" ]; then
  ufw --force enable
else
  echo "Firewall rules added. Review with 'ufw status verbose' and rerun with UFW_FORCE_ENABLE=true to enable." >&2
fi

systemctl enable --now fail2ban
