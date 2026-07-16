# Docker Deployment And Squarespace DNS

## Host Requirements

Use any public Linux host with:

- A stable public IPv4 address
- Git
- Docker Engine and the Docker Compose plugin
- At least 2 GB RAM and 20 GB disk for a small installation
- TCP ports `80` and `443` open inbound
- UDP port `443` open inbound if HTTP/3 is desired

The application does not require a particular hosting provider.

## Clone A Specific Repository Branch

```bash
git clone --branch NewsWebsite-Docker --single-branch \
  https://github.com/psainaveen12/NewsWebsite.git \
  /opt/newswebsite
cd /opt/newswebsite
cp .env.example .env
```

Set production secrets in `.env`. The database password and session secret should be random. The admin password must never be committed.

```bash
openssl rand -hex 24
openssl rand -hex 32
```

Validate and start:

```bash
bash scripts/preflight.sh
docker compose up -d --build
bash scripts/healthcheck.sh
```

## Configure Squarespace DNS

Open the Squarespace Domains dashboard for `ieltstask.com`, then open DNS settings and add:

| Field | Value |
|---|---|
| Type | `A` |
| Host/Name | `news` |
| Data/Value | Stable public IPv4 address of the Docker host |
| TTL | Default/automatic |

Remove any conflicting `news` CNAME or A record. Do not change the root (`@`) or `www` records used by the existing Squarespace site.

After DNS propagates, verify from a workstation:

```bash
dig +short news.ieltstask.com A
curl -I https://news.ieltstask.com/healthz
```

The DNS result must equal the Docker host public address. Caddy will obtain the TLS certificate automatically after DNS resolves and ports `80`/`443` reach the host.

## Update Deployment

From the existing clone:

```bash
cd /opt/newswebsite
DEPLOY_BRANCH=NewsWebsite-Docker bash scripts/deploy.sh
```

The script fetches only the selected branch, fast-forwards the checkout, validates `.env`, rebuilds the image, refreshes containers, and runs the health check.

## Verify Production

```bash
docker compose ps
docker compose logs --tail=100 app caddy db
curl -fsS https://news.ieltstask.com/healthz
```

Expected health response:

```json
{"status":"ok","database":"ok"}
```
