# Rollback Checklist

1. If launch quality is unacceptable, point DNS back to the previous production target.
2. Freeze imports and new publishing until the issue is understood.
3. Inspect logs, redirects, media paths, and WordPress settings.
4. Restore the latest known-good database backup if the database is the source of the issue.
5. Restore the latest known-good WordPress content backup if uploads, themes, or plugins are damaged.
6. Validate the fix before attempting another cutover.

## Restore Commands

```bash
cd ~/apps/ieltstask
bash scripts/restore-db.sh /path/to/db-backup.sql.gz
bash scripts/restore-wp.sh /path/to/wp-content-backup.tar.gz
```

## High-Risk Areas to Check First

- Wrong canonical host or bad redirect rules
- Broken imported media
- Incorrect permalink structure
- Theme/plugin conflicts
- Missing environment variables in `.env`
