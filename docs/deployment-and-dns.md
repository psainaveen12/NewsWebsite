# GCP Single-VM Deployment And Squarespace DNS

## 1. Accounts And Inputs

Prepare a billed GCP project, GitHub repository access, Squarespace domain DNS access, Google Search Console, Google Analytics, Google AdSense, Bing Webmaster Tools, the Blogger Takeout ZIP, an SSH key pair and a password manager. Keep a copy of the current Blogger theme and a list of high-traffic URLs for migration QA.

Recommended VM: Ubuntu 24.04 LTS, `e2-medium`, 50 GB balanced persistent disk. Increase disk size before import if Takeout media plus retained backups will exceed available capacity.

## 2. Provision Compute Engine

Authenticate the current `gcloud` CLI, then run from this repository:

```bash
gcloud auth login
GCP_PROJECT_ID=YOUR_PROJECT_ID \
GCP_REGION=us-east1 \
GCP_ZONE=us-east1-b \
SSH_SOURCE_CIDR=YOUR_PUBLIC_IP/32 \
bash scripts/gcp/provision-instance.sh
```

The idempotent script enables Compute Engine, reserves a regional static external IPv4, creates restricted SSH and public web firewall rules, and creates one Ubuntu VM without a workload service account. It prints the static IP.

Add your SSH public key to the instance’s metadata, connect, and clone the branch:

```bash
sudo apt-get update && sudo apt-get install -y git
sudo git clone --branch NewsWebsiteGCP --single-branch \
  https://github.com/psainaveen12/NewsWebsite.git /opt/newswebsite
sudo chown -R "$USER:$USER" /opt/newswebsite
cd /opt/newswebsite
SSH_SOURCE_CIDR=YOUR_PUBLIC_IP/32 bash scripts/gcp/bootstrap-ubuntu.sh
```

Sign out and back in so Docker group membership applies. The bootstrap installs Docker Engine/Compose, UFW, fail2ban, cron, unattended upgrades and DNS/diagnostic tools. It disables password and root SSH login only after confirming the deployment user has an `authorized_keys` file.

## 3. Configure Production Secrets

```bash
cd /opt/newswebsite
cp .env.example .env
chmod 600 .env
openssl rand -hex 32  # PostgreSQL password
openssl rand -hex 48  # session secret
openssl rand -hex 24  # IndexNow key
```

Set these values in `.env`:

```dotenv
APP_ENV=production
APP_BASE_URL=https://news.ieltstask.com
APP_DOMAIN=news.ieltstask.com
APP_SITE_ADDRESS=news.ieltstask.com
TLS_EMAIL=puttisainaveen@gmail.com

POSTGRES_PASSWORD=INDEPENDENT_HEX_SECRET
DATABASE_URL=postgresql+psycopg://newswebsite:THE_SAME_HEX_SECRET@db:5432/newswebsite
SESSION_SECRET=INDEPENDENT_LONG_SECRET
ADMIN_USERNAME=sainaveennews
ADMIN_PASSWORD=THE_REQUESTED_PASSWORD_THEN_ROTATE_IT

GOOGLE_SITE_VERIFICATION=YOUR_GOOGLE_TOKEN
BING_SITE_VERIFICATION=YOUR_BING_TOKEN
GA_MEASUREMENT_ID=G-SCBVGKWD97
ADSENSE_PUBLISHER_ID=ca-pub-9276619150182367
ADS_TXT_LINE=google.com, pub-9276619150182367, DIRECT, f08c47fec0942fa0
INDEXNOW_KEY=YOUR_GENERATED_INDEXNOW_KEY
```

The actual admin password, database password, session secret, SSH key and IndexNow key must never be committed.

## 4. Start Before DNS Cutover

```bash
bash scripts/preflight.sh
docker compose up -d --build
bash scripts/healthcheck.sh
docker compose ps
```

Caddy cannot obtain a public certificate until DNS points to this VM and ports 80/443 are reachable. The application and database can still become healthy before that cutover.

## 5. Squarespace DNS

In Squarespace Domains, open `ieltstask.com` DNS settings:

1. Preserve all root (`@`) and `www` records so `www.ieltstask.com` remains unchanged.
2. Remove only conflicting `news` A, AAAA or CNAME records.
3. Create an A record with host `news` and data equal to the reserved GCP IPv4.
4. Use the default TTL or 300 seconds during cutover.

Verify from a separate machine:

```bash
dig +short A news.ieltstask.com
curl -I http://news.ieltstask.com
curl -I https://news.ieltstask.com
```

Caddy automatically obtains and renews the certificate after the hostname resolves and ports 80/443 are reachable. Do not create a Squarespace URL forwarding rule; the A record must reach Caddy directly.

## 6. Install Operations

```bash
cd /opt/newswebsite
bash scripts/install-operations.sh
bash scripts/backup-all.sh
bash scripts/test-backups.sh
bash scripts/verify-production.sh
```

The user crontab runs database backup daily at 02:00, media backup at 02:30, health/disk monitoring every five minutes, and isolated restore verification each Sunday. Backups remain on the VM by default to satisfy the single-server constraint. For disaster recovery, set `OFFSITE_BACKUP_COMMAND` to an operator-owned encrypted copy command when an off-server destination is approved.

## 7. GitHub Actions Deployment

Add repository environment `production`, then these secrets:

- `GCP_SSH_HOST`: reserved static IPv4, without `https://`
- `GCP_SSH_PORT`: normally `22`
- `GCP_SSH_USER`: the Ubuntu deployment user
- `GCP_SSH_PRIVATE_KEY`: the complete private key matching instance metadata
- `GCP_SSH_KNOWN_HOSTS`: the verified `known_hosts` line for the VM

Create the host-key value once from a trusted connection, compare its fingerprint with the VM, and store the entire output of `ssh-keyscan -H -p 22 STATIC_IP` in `GCP_SSH_KNOWN_HOSTS`. The workflow does not learn a new host key during deployment.

Optionally set repository variable `GCP_DEPLOY_PATH`; it defaults to `/opt/newswebsite`.

Pushes to `NewsWebsiteGCP` run the Python tests and shell syntax checks before SSH deployment. The remote deployment makes database/media backups, fast-forwards the branch, rebuilds containers, verifies health and prunes unused images.

## 8. Search, Analytics And Monetization

1. Verify `news.ieltstask.com` in Google Search Console and Bing Webmaster Tools using the configured meta tokens or a DNS verification record.
2. Submit `https://news.ieltstask.com/sitemap.xml` to both tools.
3. Confirm `robots.txt`, `ads.txt` and the IndexNow key URL return 200.
4. Run `bash scripts/indexnow-submit.sh` once after migration; future successful imports notify IndexNow automatically.
5. Verify Google Analytics real-time traffic and AdSense ownership before adding ad units.
6. Review indexing, crawl issues, queries, clicks, CTR, position and mobile Core Web Vitals weekly for the first month.

## 9. Launch Gate

Run the automated checks, then complete [the launch checklist](launch-checklist.md). Do not cut over until top Blogger URLs, hero/inline images, comments, trust pages and redirects are manually verified.
