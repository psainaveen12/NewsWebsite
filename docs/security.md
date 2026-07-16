# Security Notes

## Admin Boundary

The application has one environment-configured admin identity. It can only:

- Sign in and sign out
- Submit article URLs for ingestion
- Review per-URL import results
- Open stored public article pages

There are no user management, shell, database, delete, content-body editing, or file-upload controls.

Authentication uses constant-time credential comparison, a signed same-site session cookie, CSRF protection, an eight-hour session lifetime, and per-client login throttling. Production requires HTTPS-only cookies.

## URL Fetching Boundary

Article fetching protects the host from server-side request forgery by:

- Allowing only HTTP and HTTPS
- Rejecting URL credentials
- Resolving and rejecting non-global IP addresses
- Revalidating every redirect target
- Rejecting local hostnames
- Enforcing redirect, timeout, content-type, and response-size limits
- Discarding unsafe image and canonical URLs

DNS rebinding is reduced through resolution checks, but no metadata fetcher should be treated as a general-purpose proxy. Keep the admin credentials private.

## Secrets

`.env` is ignored by Git. Production startup rejects placeholder, short, or development secrets. Rotate any password that has appeared in chat, tickets, screenshots, or shell history before public launch.

## Network Boundary

- Caddy is the only service publishing host ports.
- PostgreSQL is isolated on an internal Docker network.
- The application runs as a non-root user with all Linux capabilities dropped and a read-only filesystem.
- Security headers are applied by both the application and Caddy.
