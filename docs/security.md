# Security Model

## Authentication

- One environment-configured administrator account
- Constant-time username and password comparison
- Signed, HTTP-only, SameSite session cookie
- Secure cookies required in production
- Eight-hour session lifetime
- Login throttling by client address
- CSRF tokens on login, import and logout
- No registration, user management, editing or deletion API

The requested initial password must be stored only in the production `.env`. Rotate it if it has been shared through chat, email or logs.

## Archive Processing

- ZIP extension and structure validation
- Streamed upload with configured byte limit
- Path traversal and absolute path rejection
- Symbolic-link rejection
- Maximum file count and expanded archive size
- Suspicious compression-ratio rejection
- Image checksum deduplication
- HTML sanitization before database storage
- Non-YouTube iframes, scripts, forms, objects and embeds removed
- Original upload removed after processing

## Runtime Isolation

- PostgreSQL has no published host port
- Internal Docker network separates the database
- Application container runs as UID/GID `10001`
- Read-only application filesystem with dedicated temporary and media mounts
- Linux capabilities dropped from the application
- Cloudflare Tunnel uses outbound-only connectivity; no public origin port is published
- The local application port is bound only to host loopback
- Security headers and content security policy are applied to every response
- Admin pages receive `no-store` and `noindex`

## Secrets

Never commit `.env`, Cloudflare tunnel tokens, Takeout exports, backups, database dumps, SSH keys or credentials. Use at least 32 random bytes for `SESSION_SECRET` and independent random PostgreSQL credentials.
