# Security Model

## Identity And Admin Scope

- One environment-configured administrator account
- Constant-time credential comparison
- Signed HTTP-only, SameSite session cookie; Secure in production
- Eight-hour sessions, IP throttling and CSRF validation
- Admin can only upload Takeout and inspect import status
- No registration, publishing, editing, deletion, database or user-management APIs

Store the requested initial password only in the VM `.env` and rotate it after first use because it has already been shared. Never commit credentials.

## Host And Network

- GCP firewall and UFW expose only restricted SSH plus HTTP/HTTPS
- SSH public keys only after bootstrap verifies `authorized_keys`
- Root SSH and password authentication disabled
- fail2ban and unattended security updates enabled
- PostgreSQL has no host port and uses an internal Docker network
- FastAPI has no host port; only Caddy can reach it
- Caddy manages TLS, redirects HTTP, compresses responses and applies security headers
- App and Caddy use read-only filesystems, temporary filesystems, dropped capabilities and `no-new-privileges`
- Docker JSON logs rotate to prevent unbounded disk growth

## Application And Imports

- CSP, HSTS, frame, MIME, referrer and permissions headers
- Admin responses are `no-store` and `noindex`
- Streamed upload limits, ZIP validation, traversal/symlink rejection and zip-bomb controls
- HTML sanitization and restricted iframe hosts
- Checksum media deduplication and original ZIP deletion
- XML parsing uses `defusedxml`
- JSON API is read-only and exposes published posts only

## Secrets And Backups

Excluded from Git: `.env`, private keys, GCP credentials, Takeout archives, database dumps, media backups and logs. Use independent random PostgreSQL/session secrets. Local backups inherit host permissions; any approved off-server copy should be encrypted and access-controlled.

Restores are tested weekly in a temporary PostgreSQL database. A backup is not considered valid until `scripts/test-backups.sh` succeeds.
