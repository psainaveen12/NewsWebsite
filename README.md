# IELTSTask Production Stack

Production-ready starter repository for [https://www.ieltstask.com](https://www.ieltstask.com), built from the production runbook requirements for a self-hosted WordPress deployment on Oracle Cloud Always Free.

This repository is designed to support:

- WordPress + MariaDB running on Docker Compose
- Caddy for HTTPS, compression, canonical redirects, and security headers
- GitHub Actions deployment over SSH
- Blogger migration planning for blog ID `1194349556968361444`
- Migration notes from the current Blogger theme XML, including Search Console, GA4, and AdSense identifiers
- WordPress REST API publishing with Application Passwords
- Search visibility setup for Search Console, Bing, IndexNow, XML sitemap, and `robots.txt`
- Backups, restore workflows, launch gates, and rollback notes

## Included Deliverables

- `docker-compose.yml`
- `.env.example`
- `caddy/Caddyfile`
- `wordpress/php/custom.ini`
- `wordpress/wp-content/themes/ieltstask-theme/`
- `scripts/install-docker-ubuntu.sh`
- `scripts/harden-ubuntu.sh`
- `scripts/deploy.sh`
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
3. Provision the Oracle Ubuntu VM by following [docs/server-setup.md](docs/server-setup.md).
4. Clone this repo onto the VM at `~/apps/ieltstask`.
5. Run `docker compose up -d`.
6. Point DNS only after the stack is healthy and HTTPS is ready.
7. Complete WordPress installation, plugin setup, and Blogger migration by following the docs in `docs/`.

## Deployment Flow

- Pushes to `main` trigger `.github/workflows/deploy.yml`.
- The workflow connects to the server with `SSH_HOST`, `SSH_PORT`, `SSH_USER`, and `SSH_PRIVATE_KEY`.
- The remote server runs `bash scripts/deploy.sh`, which pulls the latest code and refreshes the Compose stack.

## Local Validation

Useful checks before pushing:

- `docker compose config`
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
- This repo keeps deployment code in Git while persistent WordPress and MariaDB data live in Docker volumes.
- The bundled `ieltstask-theme` is a lightweight starter theme so the site can be activated immediately after setup or migration.
