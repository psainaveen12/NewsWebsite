# Docker Deployment And Cloudflare Tunnel

## Host Requirements

- Linux host with outbound Internet access
- Git, Docker Engine and the Docker Compose plugin
- Recommended minimum: 2 GB RAM and 20 GB disk plus room for imported media
- Outbound access to Cloudflare; no inbound HTTP or HTTPS ports are required

The database and media remain on the Docker host. A stable public IPv4 is not required.

## Configure Cloudflare

1. Add `ieltstask.com` to Cloudflare and update the domain nameservers at Squarespace Domains.
2. Preserve the existing root (`@`) and `www` records so `www.ieltstask.com` remains unchanged.
3. In Cloudflare, open **Networking > Tunnels** and create a remotely managed tunnel named `newswebsite`.
4. Add a published application with hostname `news.ieltstask.com` and service `http://app:8000`.
5. Copy the tunnel token. The hostname route automatically creates a proxied CNAME to the tunnel.

The token can start the tunnel and must be treated as a secret.

## Deploy The Branch

```bash
git clone --branch NewsWebsiteDocker --single-branch \
  https://github.com/psainaveen12/NewsWebsite.git \
  /opt/newswebsite
cd /opt/newswebsite
cp .env.example .env
mkdir -p secrets
printf '%s' 'PASTE_TUNNEL_TOKEN_HERE' > secrets/cloudflare-tunnel-token
chmod 600 secrets/cloudflare-tunnel-token
```

Set the production values in `.env`:

```dotenv
COMPOSE_PROFILES=cloudflare
APP_ENV=production
APP_BASE_URL=https://news.ieltstask.com
APP_DOMAIN=news.ieltstask.com
CLOUDFLARE_TUNNEL_TOKEN_FILE=./secrets/cloudflare-tunnel-token
```

Replace every PostgreSQL, session and admin placeholder with an independent random value. Then deploy:

```bash
bash scripts/preflight.sh
docker compose --profile cloudflare up -d --build --remove-orphans
bash scripts/healthcheck.sh
```

## Security Group

Cloudflare Tunnel makes outbound connections, so EC2 inbound ports `80` and `443` can remain closed. Restrict inbound SSH to your own IP. PostgreSQL and FastAPI are never bound to a public host interface; the local development binding uses `127.0.0.1` only.

## Updates

```bash
cd /opt/newswebsite
DEPLOY_BRANCH=NewsWebsiteDocker bash scripts/deploy.sh
```

## Verification

```bash
docker compose --profile cloudflare ps
docker compose --profile cloudflare logs --tail=100 app cloudflared db
curl -fsS https://news.ieltstask.com/healthz
curl -I https://news.ieltstask.com/
```

Expected health response:

```json
{"status":"ok","database":"ok"}
```
