#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "Run this script as root." >&2
  exit 1
fi

PACKAGE_MANAGER=""

if command -v apt-get >/dev/null 2>&1; then
  PACKAGE_MANAGER="apt-get"
elif command -v dnf >/dev/null 2>&1; then
  PACKAGE_MANAGER="dnf"
elif command -v yum >/dev/null 2>&1; then
  PACKAGE_MANAGER="yum"
else
  echo "Unsupported package manager. This script currently supports apt, dnf, and yum." >&2
  exit 1
fi

if [ "$PACKAGE_MANAGER" = "apt-get" ]; then
  apt-get update
  apt-get install -y ca-certificates curl gnupg git unzip openssl

  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  chmod a+r /etc/apt/keyrings/docker.gpg

  . /etc/os-release
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${VERSION_CODENAME} stable" \
    > /etc/apt/sources.list.d/docker.list

  apt-get update
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
else
  "$PACKAGE_MANAGER" install -y ca-certificates curl git unzip openssl shadow-utils docker
  "$PACKAGE_MANAGER" install -y docker-compose-plugin docker-compose >/dev/null 2>&1 || true
fi

systemctl enable --now docker

TARGET_USER="${SUDO_USER:-}"
if [ -z "$TARGET_USER" ]; then
  if id ec2-user >/dev/null 2>&1; then
    TARGET_USER="ec2-user"
  elif id ubuntu >/dev/null 2>&1; then
    TARGET_USER="ubuntu"
  else
    TARGET_USER="$(logname 2>/dev/null || true)"
  fi
fi

if id "$TARGET_USER" >/dev/null 2>&1; then
  usermod -aG docker "$TARGET_USER"
fi

docker --version
if docker compose version >/dev/null 2>&1; then
  docker compose version
elif command -v docker-compose >/dev/null 2>&1; then
  docker-compose version
else
  echo "Docker installed, but Docker Compose is still unavailable." >&2
  exit 1
fi
