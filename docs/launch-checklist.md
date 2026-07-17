# Production Launch Checklist

- GCP VM uses a reserved static IPv4 and a sufficiently sized persistent disk.
- GCP firewall and UFW allow web traffic; SSH is restricted to an approved CIDR.
- Docker, fail2ban, cron and unattended upgrades are active.
- `.env` contains unique production secrets and requested admin credentials only on the VM.
- Caddy, FastAPI and PostgreSQL containers are healthy; data volumes are mounted.
- Squarespace `news` A record resolves only to the GCP static IPv4; root and `www` remain unchanged.
- HTTP redirects to HTTPS and the certificate is valid.
- `scripts/verify-production.sh`, `scripts/migration-audit.sh` and `scripts/test-backups.sh` pass.
- Highest-value Blogger posts, media, comments and redirects pass manual QA.
- About, Contact, Privacy, Terms, Disclaimer and Editorial Policy pages return 200.
- Search Console and Bing verification succeed; sitemap is submitted to both.
- IndexNow key is reachable and a post-migration batch is accepted.
- Google Analytics real-time activity is visible.
- AdSense ownership and `ads.txt` are valid; ad placements do not disrupt mobile reading.
- Uptime, disk and container monitoring schedules are installed.
- Logs and metrics are watched closely for 24-72 hours after cutover.
