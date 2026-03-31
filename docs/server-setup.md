# Server Setup

## AWS EC2 Provisioning

1. Launch an Ubuntu 24.04 / 22.04 LTS or Amazon Linux EC2 instance.
2. Choose an instance size that can comfortably run Docker, MariaDB, WordPress, and Caddy on one host.
   A good baseline is `t3.medium` or larger for production traffic.
3. Use a security group that allows inbound `22`, `80`, and `443`.
4. Attach storage sized for WordPress uploads, database growth, and local backups.
5. Associate your SSH key pair and connect as:
   - `ubuntu` for Ubuntu AMIs
   - `ec2-user` for Amazon Linux AMIs

## Initial Host Bootstrap

Clone the repo first:

```bash
mkdir -p ~/apps/ieltstask
cd ~/apps/ieltstask
git clone YOUR_REPO_URL .
```

Then run the EC2 bootstrap as root:

```bash
cd ~/apps/ieltstask
sudo UFW_FORCE_ENABLE=true bash scripts/bootstrap-ec2-host.sh
```

This bootstrap:

- installs Docker Engine and the Compose plugin
- enables the host firewall (`ufw` on Ubuntu, `firewalld` on Amazon Linux)
- enables `fail2ban` when available
- enables unattended upgrades or the native automatic update timer
- creates swap if the host does not already have it
- prepares default app and backup directories

## Configure The App

Create your runtime environment file:

```bash
cd ~/apps/ieltstask
cp .env.example .env
```

Update every placeholder value in `.env`, especially:

- all database passwords
- all WordPress salts and keys
- domain and email settings
- backup location if you do not want the default

Validate before starting:

```bash
bash scripts/preflight.sh
```

## Start The Stack

```bash
docker compose up -d
docker compose ps
bash scripts/healthcheck.sh
```

Once DNS points at the instance and TLS is live, you can also run:

```bash
bash scripts/healthcheck.sh --external
```

## Install Ongoing Cron Jobs

After WordPress itself is installed and reachable, install the host cron jobs:

```bash
sudo APP_USER=$(whoami) APP_DIR=$HOME/apps/ieltstask bash scripts/install-cron-jobs.sh
```

This installs jobs for:

- database backups
- WordPress content backups
- `wp cron event run --due-now`
- production health checks

## GitHub Actions Deployment Secrets

Set these repository secrets before using the deploy workflow:

- `EC2_HOST` or `SSH_HOST`
- `EC2_SSH_PORT` or `SSH_PORT`
- `EC2_SSH_USER` or `SSH_USER`
- `EC2_SSH_KEY` or `SSH_PRIVATE_KEY`
- `DEPLOY_PATH` (optional, if the repo is not located at `~/apps/ieltstask`)

## Post-Bootstrap Notes

- Keep MariaDB private. Do not publish a database port.
- Use SSH keys only.
- Add a second WordPress admin account for recovery.
- Test restore steps before launch, not after.
