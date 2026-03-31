# IELTSTask Production Runbook

This repository is the code implementation of the production deployment runbook for `https://www.ieltstask.com`.

## Production Targets

- Canonical domain: `https://www.ieltstask.com`
- Apex redirect target: `https://ieltstask.com -> https://www.ieltstask.com`
- Blogger source admin URL: `https://www.blogger.com/u/0/blog/posts/1194349556968361444`
- Blogger migration source file: Google Takeout `feed.atom`

## Delivery Map

| Area | Implemented here |
| --- | --- |
| Docker stack | `docker-compose.yml` |
| Reverse proxy and TLS | `caddy/Caddyfile` |
| PHP tuning | `wordpress/php/custom.ini` |
| Deployment automation | `.github/workflows/deploy.yml`, `scripts/deploy.sh` |
| Backup and restore | `scripts/backup-db.sh`, `scripts/backup-wp.sh`, `scripts/restore-db.sh`, `scripts/restore-wp.sh` |
| Oracle bootstrap | `scripts/install-docker-ubuntu.sh`, `scripts/harden-ubuntu.sh`, `docs/server-setup.md` |
| WordPress baseline | `docs/wordpress-setup.md` |
| Blogger migration QA | `docs/blogger-migration-checklist.md` |
| Blogger theme audit | `docs/blogger-theme-audit.md` |
| API publishing | `docs/json-publishing.md` |
| Search visibility | `docs/search-visibility-checklist.md` |
| Launch and rollback | `docs/launch-checklist.md`, `docs/rollback-checklist.md` |

## Recommended Execution Order

1. Provision the Oracle VM and lock down the firewall.
2. Clone this repo to `~/apps/ieltstask`.
3. Create `.env` from `.env.example` and fill in strong secrets.
4. Start the stack with `docker compose up -d`.
5. Point DNS once HTTPS and container health are good.
6. Complete WordPress installation and activate the theme/plugins.
7. Import Blogger content and run migration QA.
8. Connect Search Console, Bing, Site Kit, Analytics, and IndexNow.
9. Schedule backups and watch the first 24 to 72 hours after cutover closely.
