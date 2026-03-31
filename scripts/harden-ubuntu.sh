#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "Run this script as root." >&2
  exit 1
fi

ENABLE_FIREWALL="${UFW_FORCE_ENABLE:-${FIREWALL_FORCE_ENABLE:-false}}"

if command -v apt-get >/dev/null 2>&1; then
  apt-get update
  apt-get install -y ufw fail2ban

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

  if [ "$ENABLE_FIREWALL" = "true" ]; then
    ufw --force enable
  else
    echo "Firewall rules added. Review with 'ufw status verbose' and rerun with UFW_FORCE_ENABLE=true to enable." >&2
  fi

  systemctl enable --now fail2ban
elif command -v dnf >/dev/null 2>&1 || command -v yum >/dev/null 2>&1; then
  PACKAGE_MANAGER="dnf"
  if ! command -v dnf >/dev/null 2>&1; then
    PACKAGE_MANAGER="yum"
  fi

  "$PACKAGE_MANAGER" install -y firewalld >/dev/null
  "$PACKAGE_MANAGER" install -y fail2ban >/dev/null 2>&1 || true

  if [ -f /etc/fail2ban/jail.conf ] || [ -d /etc/fail2ban ]; then
    install -m 0755 -d /etc/fail2ban/jail.d
    cat >/etc/fail2ban/jail.d/sshd.local <<'EOF'
[sshd]
enabled = true
maxretry = 5
findtime = 10m
bantime = 1h
EOF
  fi

  if [ "$ENABLE_FIREWALL" = "true" ]; then
    systemctl enable --now firewalld
    firewall-cmd --permanent --add-service=ssh
    firewall-cmd --permanent --add-service=http
    firewall-cmd --permanent --add-service=https
    firewall-cmd --reload
  else
    echo "firewalld is installed. Rerun with UFW_FORCE_ENABLE=true to enable and apply host firewall rules." >&2
  fi

  if systemctl list-unit-files | grep -q '^fail2ban\.service'; then
    systemctl enable --now fail2ban
  else
    echo "fail2ban package was not available on this host. Security group and firewall rules are still required." >&2
  fi
else
  echo "Unsupported package manager. This script currently supports apt, dnf, and yum." >&2
  exit 1
fi
