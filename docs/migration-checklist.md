# Blogger Migration Checklist

## Before Import

- Download a final Blogger-only Google Takeout ZIP and keep it unchanged.
- Export the Blogger theme and capture screenshots of homepage, article, mobile and key pages.
- Record source counts and the highest-traffic historic URLs.
- Complete a database and media backup.

## Import

- Sign in at `/login` and upload the original ZIP.
- Wait for `completed`; review every warning in the audit trail.
- Run `bash scripts/migration-audit.sh`.
- Confirm post, page, comment and asset counts against the source.

## Manual QA

- Check at least 25 high-value posts and all trust pages.
- Verify title, description, author, publish/update dates, labels, body formatting and comments.
- Verify featured and inline images, tables, lists, links and YouTube embeds on desktop/mobile.
- Test historic `/YYYY/MM/slug.html` and `/p/slug.html` URLs for permanent redirects.
- Search for several exact titles and content phrases.
- Confirm drafts are not public and re-importing does not duplicate content.

Do not change DNS until these checks pass.
