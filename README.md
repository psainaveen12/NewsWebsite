# IELTSTask Newsroom

A Docker-native article curation application for `news.ieltstask.com`. An authenticated import-only admin submits one or many public blog article URLs; the application safely extracts publisher metadata, stores it in PostgreSQL, and presents it through a responsive public newsroom.

The stack is provider-neutral. It requires only a public Linux host with Git, Docker Engine, Docker Compose, and ports `80`/`443` available.

## What It Does

- Imports one URL or up to 50 URLs per submission
- Extracts title, description, lead image, author, publisher, publication date, and canonical URL
- Updates matching canonical/source URLs instead of creating duplicates
- Blocks private network targets, unsafe schemes, credential-bearing URLs, oversized responses, and unsafe redirects
- Stores article metadata in a private PostgreSQL container
- Displays searchable and paginated article cards plus article summary pages
- Provides one restricted admin account with import-only functionality
- Uses Caddy for automatic HTTPS on `news.ieltstask.com`
- Includes health checks, CI, database backup/restore, and branch-driven deployment

## Architecture

```text
Browser -> Caddy :80/:443 -> FastAPI app :8000 -> PostgreSQL :5432
                            (private Docker networks)
```

Only Caddy publishes host ports. PostgreSQL is isolated on an internal Docker network. See [the full architecture](docs/full-e2e-architecture.md).

## First Local Run

```bash
git checkout NewsWebsite-Docker
cp .env.example .env
```

Edit `.env` and replace every placeholder. Generate secrets with:

```bash
openssl rand -hex 24
openssl rand -hex 32
```

For local HTTP testing, use:

```env
ENVIRONMENT=development
APP_DOMAIN=localhost
ALLOWED_HOSTS=localhost,127.0.0.1
COOKIE_SECURE=false
```

Start the stack:

```bash
docker compose up -d --build
docker compose ps
```

Open `http://localhost`. The admin login is at `http://localhost/login`.

Stop without deleting data:

```bash
docker compose down
```

Delete the local database and all Docker volumes only when intentionally resetting:

```bash
docker compose down --volumes
```

## Admin Credentials

The default admin username is configured as `sainaveennews`. Set the password only in the uncommitted `.env` file:

```env
ADMIN_USERNAME=sainaveennews
ADMIN_PASSWORD=your-private-password
SESSION_SECRET=at-least-32-random-characters
```

The password is intentionally not committed to Git. Because any password shared in chat should be considered exposed, rotate it before making the site public.

The account can only access the import desk, submit article URLs, review import results, and open stored public article pages. There are no user-management, database-management, delete, or arbitrary-edit controls.

## Deploy From Repository And Branch

First deployment:

```bash
git clone --branch NewsWebsite-Docker --single-branch \
  https://github.com/psainaveen12/NewsWebsite.git newswebsite
cd newswebsite
cp .env.example .env
```

Set production values in `.env`, including:

```env
ENVIRONMENT=production
APP_DOMAIN=news.ieltstask.com
ALLOWED_HOSTS=news.ieltstask.com
COOKIE_SECURE=true
TLS_EMAIL=puttisainaveen@gmail.com
```

Then deploy:

```bash
bash scripts/preflight.sh
docker compose up -d --build
bash scripts/healthcheck.sh
```

Every later deployment uses the branch name explicitly:

```bash
DEPLOY_BRANCH=NewsWebsite-Docker bash scripts/deploy.sh
```

The generic clone/update helper also accepts repository, branch, and deployment directory:

```bash
bash scripts/deploy-from-repo.sh \
  https://github.com/psainaveen12/NewsWebsite.git \
  NewsWebsite-Docker \
  /opt/newswebsite
```

## Squarespace DNS

Docker does not connect directly to Squarespace. Squarespace hosts the DNS record, while Caddy on the Docker host serves the subdomain and obtains its TLS certificate.

In Squarespace Domains, add:

| Type | Host | Value | TTL |
|---|---|---|---|
| `A` | `news` | Public IPv4 address of the Docker host | Automatic/default |

If the host has a stable public IPv6 address, optionally add an `AAAA` record for `news`. Do not add both an old CNAME and the new A/AAAA record for the same host. Allow inbound TCP `80` and `443`, plus UDP `443` for HTTP/3.

Full instructions and verification commands are in [deployment-and-dns.md](docs/deployment-and-dns.md).

## Operations

```bash
# Logs
docker compose logs -f app caddy db

# Health
bash scripts/healthcheck.sh

# Backup
bash scripts/backup-db.sh

# Restore
bash scripts/restore-db.sh backups/db/newswebsite-YYYY-MM-DD-HHMMSS.sql.gz

# Tests
python -m pip install -r requirements-dev.txt
pytest -q
```

The `postgres_data` Docker volume is the source of truth. Keep encrypted database backups outside the application host for disaster recovery.

## Repository Layout

```text
app/                    FastAPI application, templates, and styles
caddy/Caddyfile         HTTPS reverse proxy configuration
docker/                 Container startup and migration entrypoint
migrations/             Versioned PostgreSQL schema migrations
scripts/                Deploy, health, backup, and restore operations
tests/                  Authentication, ingestion, display, and URL-safety tests
docker-compose.yml      Complete application stack
Dockerfile              Non-root application image
docs/                   Architecture, security, DNS, and deployment guidance
```
