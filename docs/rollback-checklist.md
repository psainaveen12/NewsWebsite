# Rollback Checklist

1. Freeze Takeout imports and preserve logs.
2. Run `bash scripts/backup-all.sh` before changing code or data.
3. For a code regression, run `bash scripts/rollback.sh GOOD_COMMIT`; PostgreSQL/media volumes remain unchanged.
4. For bad data, restore the latest verified database and media pair with `restore-db.sh` and `restore-media.sh`.
5. For an unacceptable launch, restore the previous Squarespace `news` DNS target or remove the new record.
6. Inspect Caddy/app/database logs, migration warnings, redirect paths and media references.
7. Re-run health, production, migration and backup verification before retrying cutover.

Never restore a database backup without its matching media backup. Keep the failed state’s backup until the incident is understood.
