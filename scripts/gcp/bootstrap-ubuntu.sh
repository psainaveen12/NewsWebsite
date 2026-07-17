#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -eq 0 ]; then
  SUDO=""
  TARGET_USER="${TARGET_USER:-${SUDO_USER:-ubuntu}}"
else
  SUDO="sudo"
  TARGET_USER="${TARGET_USER:-$USER}"
fi
SSH_SOURCE_CIDR="${SSH_SOURCE_CIDR:-}"

$SUDO apt-get update
$SUDO DEBIAN_FRONTEND=noninteractive apt-get install -y \
  ca-certificates cron curl dnsutils fail2ban git gnupg jq openssl unattended-upgrades ufw unzip

$SUDO install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | $SUDO gpg --dearmor --yes -o /etc/apt/keyrings/docker.gpg
$SUDO chmod a+r /etc/apt/keyrings/docker.gpg
. /etc/os-release
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $VERSION_CODENAME stable" | \
  $SUDO tee /etc/apt/sources.list.d/docker.list >/dev/null
$SUDO apt-get update
$SUDO DEBIAN_FRONTEND=noninteractive apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

$SUDO systemctl enable --now docker cron fail2ban unattended-upgrades
$SUDO usermod -aG docker "$TARGET_USER"
$SUDO install -d -m 0750 -o "$TARGET_USER" -g "$TARGET_USER" /opt/newswebsite /opt/newswebsite-backups

$SUDO ufw default deny incoming
$SUDO ufw default allow outgoing
if [ -n "$SSH_SOURCE_CIDR" ]; then
  $SUDO ufw allow from "$SSH_SOURCE_CIDR" to any port 22 proto tcp
else
  echo "WARNING: SSH_SOURCE_CIDR is empty; SSH is open until the GCP firewall rule is restricted." >&2
  $SUDO ufw allow 22/tcp
fi
$SUDO ufw allow 80/tcp
$SUDO ufw allow 443/tcp
$SUDO ufw allow 443/udp
$SUDO ufw --force enable

$SUDO tee /etc/fail2ban/jail.d/newswebsite.local >/dev/null <<'EOF'
[sshd]
enabled = true
maxretry = 5
findtime = 15m
bantime = 1h
EOF
$SUDO systemctl restart fail2ban

AUTHORIZED_KEYS="$(getent passwd "$TARGET_USER" | cut -d: -f6)/.ssh/authorized_keys"
if [ -s "$AUTHORIZED_KEYS" ]; then
  $SUDO tee /etc/ssh/sshd_config.d/99-newswebsite-hardening.conf >/dev/null <<'EOF'
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
PubkeyAuthentication yes
EOF
  $SUDO sshd -t
  $SUDO systemctl reload ssh
else
  echo "SSH password login was not disabled because $AUTHORIZED_KEYS is missing or empty." >&2
fi

echo "Host bootstrap complete. Sign out and back in before running Docker without sudo."
