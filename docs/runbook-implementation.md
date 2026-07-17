# Production Runbook Implementation Map

The uploaded 14-page WordPress/Oracle runbook is implemented here using the requested `NewsWebsiteDocker` application as the base and adapting provider/CMS-specific components to GCP and the existing Takeout-only FastAPI CMS.

| Runbook area | NewsWebsiteGCP implementation |
| --- | --- |
| Success criteria | HTTPS, persistent Docker volumes, admin import, media, redirects, JSON reads, SEO, analytics, backups, monitoring and rollback have code/checklists. |
| Reference architecture | One Compute Engine VM, Caddy, FastAPI, PostgreSQL, media and backup storage. |
| Prerequisites | GCP/GitHub/Google/Microsoft/Squarespace/SSH/Takeout inputs are listed in the deployment guide. |
| Repository model | `NewsWebsiteGCP` production branch, ignored secrets/data, GitHub Actions tests and SSH deployment. |
| VM provisioning | Idempotent `scripts/gcp/provision-instance.sh` reserves static IPv4 and creates firewall/Ubuntu VM. |
| Hardening | `bootstrap-ubuntu.sh` configures UFW, fail2ban, SSH keys, unattended updates and Docker. |
| Docker/reverse proxy | Pinned Caddy, FastAPI and PostgreSQL; only Caddy exposes ports 80/443. |
| CMS baseline | Existing private admin is intentionally limited to Takeout upload/status. No editor/plugin/user controls are added. |
| WordPress plugins | Functional equivalents are native: metadata/schema/sitemap, redirects, security, image handling, IndexNow, GA and AdSense. SMTP is unnecessary because there is no email/password-reset workflow. |
| Blogger migration | Both export schemas, pages/posts/drafts/comments/assets, sanitization, deduplication, URL repair, migration audit and manual QA checklist. |
| REST/JSON | Public read-only `/api/v1/articles` API. Write/Application Password endpoints are intentionally omitted because they conflict with the Takeout-only admin requirement. |
| Search visibility | Google/Bing verification, sitemap, robots, IndexNow key/automatic notification and launch monitoring checklist. |
| Analytics/AdSense | GA tag, AdSense ownership/script, `ads.txt`, trust-page and mobile launch gates. |
| Security/backup/monitoring/performance | Host hardening, isolation, headers, daily backups, restore tests, five-minute checks, Caddy compression and lazy media. |
| Launch | Automated production verifier plus manual DNS/content/search/analytics checklist. |
| Rollback | Pre-deploy backups, code rollback script and DNS/data rollback checklist. |

The deliberate FastAPI/PostgreSQL substitutions preserve the user’s existing imported content and exact permission model. Replacing the application with WordPress/MariaDB would add editing, plugin, user and write-API capabilities that were explicitly prohibited.
