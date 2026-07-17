# Docker Deployment And Squarespace DNS

## Host Requirements

- Public Linux host with a stable IPv4 address
- Git, Docker Engine and the Docker Compose plugin
- Recommended minimum: 2 GB RAM and 20 GB disk plus room for imported media
- TCP ports `80` and `443` open inbound
- UDP port `443` optional for HTTP/3

No cloud-provider account or managed database is required.

## Deploy The Requested Branch

```bash
git clone --branch NewsWebsiteDocker --single-branch \
  https://github.com/psainaveen12/NewsWebsite.git \
  /opt/newswebsite
cd /opt/newswebsite
cp .env.example .env
```

Edit `.env` and set:

```dotenv
APP_ENV=production
APP_ADDRESS=news.ieltstask.com
APP_BASE_URL=https://news.ieltstask.com
APP_DOMAIN=news.ieltstask.com
TLS_EMAIL=puttisainaveen@gmail.com
```

Also replace PostgreSQL, session and admin placeholders with unique values. The admin password must not be committed.

```bash
bash scripts/preflight.sh
docker compose up -d --build
bash scripts/healthcheck.sh
```

## Squarespace DNS

In the Squarespace Domains dashboard:

1. Open `ieltstask.com`.
2. Open DNS settings.
3. Leave the root (`@`) and `www` records unchanged so `www.ieltstask.com` continues using the existing Blogger/Squarespace configuration.
4. Remove a conflicting `news` CNAME or A record if one exists.
5. Add the record below.

| Field | Value |
|---|---|
| Type | `A` |
| Host/Name | `news` |
| Data/Value | Stable public IPv4 of the Docker host |
| TTL | Automatic/default |

Verify after propagation:

```bash
dig +short news.ieltstask.com A
curl -I https://news.ieltstask.com/healthz
```

The DNS result must equal the Docker host IPv4. Caddy automatically requests TLS after the record resolves and ports `80`/`443` reach the host.

## Updates

```bash
cd /opt/newswebsite
DEPLOY_BRANCH=NewsWebsiteDocker bash scripts/deploy.sh
```

## Production Verification

```bash
docker compose ps
docker compose logs --tail=100 app nginx caddy db
curl -fsS https://news.ieltstask.com/healthz
curl -I https://news.ieltstask.com/
```

Expected health response:

```json
{"status":"ok","database":"ok"}
```
