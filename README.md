# IELTSTask EC2 Production Stack

Production-ready starter repository for [https://www.ieltstask.com](https://www.ieltstask.com), built for a self-hosted WordPress deployment on a single AWS EC2 instance with no external database or other required AWS managed services.

This repository is designed to support:

- WordPress + MariaDB running on Docker Compose on one EC2 host
- Caddy for HTTPS, compression, canonical redirects, and security headers
- GitHub Actions deployment over SSH to EC2
- Blogger migration planning for blog ID `1194349556968361444`
- Migration notes from the current Blogger theme XML, including Search Console, GA4, and AdSense identifiers
- WordPress REST API publishing with Application Passwords
- Search visibility setup for Search Console, Bing, IndexNow, XML sitemap, and `robots.txt`
- Host bootstrap, health checks, cron automation, backups, restore workflows, launch gates, and rollback notes

## Included Deliverables

- `docker-compose.yml`
- `.env.example`
- `caddy/Caddyfile`
- `wordpress/php/custom.ini`
- `wordpress/wp-content/mu-plugins/`
- `wordpress/wp-content/themes/ieltstask-theme/`
- `scripts/bootstrap-ec2-host.sh`
- `scripts/install-docker-ubuntu.sh`
- `scripts/harden-ubuntu.sh`
- `scripts/preflight.sh`
- `scripts/deploy.sh`
- `scripts/healthcheck.sh`
- `scripts/wp-cli.sh`
- `scripts/run-wp-cron.sh`
- `scripts/install-cron-jobs.sh`
- `scripts/backup-db.sh`
- `scripts/backup-wp.sh`
- `scripts/restore-db.sh`
- `scripts/restore-wp.sh`
- `.github/workflows/deploy.yml`
- `docs/production-runbook.md`
- `docs/server-setup.md`
- `docs/wordpress-setup.md`
- `docs/blogger-migration-checklist.md`
- `docs/blogger-theme-audit.md`
- `docs/json-publishing.md`
- `docs/search-visibility-checklist.md`
- `docs/launch-checklist.md`
- `docs/rollback-checklist.md`

## Quick Start

1. Copy `.env.example` to `.env`.
2. Replace every placeholder secret and email value.
3. Provision the AWS EC2 host by following [docs/server-setup.md](docs/server-setup.md).
4. Clone this repo onto the VM at `~/apps/ieltstask`.
5. Run `bash scripts/preflight.sh`.
6. Run `docker compose up -d`.
7. Run `bash scripts/healthcheck.sh` after the containers start.
8. Point DNS only after the stack is healthy and HTTPS is ready.
9. Complete WordPress installation, plugin setup, and Blogger migration by following the docs in `docs/`.
10. Install the host cron jobs after WordPress is initialized.

## Deployment Flow

- Pushes to `main` and `awsPlatformDeployTest` trigger `.github/workflows/deploy.yml`.
- The workflow connects to the server with `EC2_HOST` / `SSH_HOST`, `EC2_SSH_PORT` / `SSH_PORT`, `EC2_SSH_USER` / `SSH_USER`, `EC2_SSH_KEY` / `SSH_PRIVATE_KEY`, and optionally `DEPLOY_PATH`.
- The remote server runs `bash scripts/deploy.sh`, which pulls the latest code and refreshes the Compose stack.

## Local Validation

Useful checks before pushing:

- `bash scripts/preflight.sh`
- `docker compose config`
- `bash scripts/healthcheck.sh`
- `bash -n scripts/*.sh`

## Blogger Migration Context

- WordPress production URL: `https://www.ieltstask.com`
- Blogger admin URL provided: `https://www.blogger.com/u/0/blog/posts/1194349556968361444`
- Recommended import source: Google Takeout `feed.atom`
- Existing Search Console token from Blogger XML: `6WbeH24Nl3cffMo0M_o9NYTXpI5weva3_Fknw0SP08`
- Existing GA4 measurement ID from Blogger XML: `G-SCBVGKWD97`
- Existing AdSense publisher ID from Blogger XML: `ca-pub-9276619150182367`

## Notes

- Do not commit `.env`, database dumps, backups, SSH keys, or uploaded media.
- This repo keeps deployment code in Git while persistent WordPress and MariaDB data live in Docker volumes on the EC2 instance.
- The bundled `ieltstask-theme` is a lightweight starter theme so the site can be activated immediately after setup or migration.
