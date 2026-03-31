#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "Run this script as root." >&2
  exit 1
fi

apt update
apt install -y ufw fail2ban

install -m 0755 -d /etc/fail2ban/jail.d
cat >/etc/fail2ban/jail.d/sshd.local <<'EOF'
[sshd]
enabled = true
maxretry = 5
findtime = 10m
bantime = 1h
EOF

ufw default deny incoming
ufw default allow outgoing

ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp

if [ "${UFW_FORCE_ENABLE:-false}" = "true" ]; then
  ufw --force enable
else
  echo "Firewall rules added. Review with 'ufw status verbose' and rerun with UFW_FORCE_ENABLE=true to enable." >&2
fi

systemctl enable --now fail2ban
