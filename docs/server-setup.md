# Server Setup

## Oracle Cloud VM Provisioning

1. Create an Ubuntu LTS VM on Oracle Cloud Always Free, ideally Ampere A1 Flex.
2. Attach a public IP.
3. Upload your SSH public key during provisioning.
4. Allow inbound ports `22`, `80`, and `443` in the OCI security list or network security group.
5. SSH in and update the host:

```bash
ssh ubuntu@YOUR_SERVER_IP
sudo apt update && sudo apt upgrade -y
sudo reboot
```

## Install Docker and Base Packages

Run this script as root on the VM:

```bash
sudo bash scripts/install-docker-ubuntu.sh
```

It installs Docker Engine, the Compose plugin, Git, curl prerequisites, and adds the default server user to the `docker` group.

## Hardening Baseline

Run:

```bash
sudo UFW_FORCE_ENABLE=true bash scripts/harden-ubuntu.sh
```

This sets up:

- `ufw`
- `fail2ban`
- Open ports `22`, `80`, and `443`

## App Directory Layout

Clone the repo on the server at:

```bash
mkdir -p ~/apps/ieltstask
cd ~/apps/ieltstask
git clone YOUR_REPO_URL .
cp .env.example .env
```

Fill in `.env`, then start the stack:

```bash
docker compose up -d
docker compose ps
```

## Post-Bootstrap Notes

- Keep MariaDB private. Do not publish a DB port.
- Use SSH keys only.
- Add a second WordPress admin account for recovery.
- Schedule regular OS updates.
