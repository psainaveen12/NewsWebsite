# Launch Checklist

## Infrastructure

- DNS points to the Oracle VM
- `https://www.ieltstask.com` is live
- `https://ieltstask.com` redirects permanently to `https://www.ieltstask.com`
- `docker compose ps` shows healthy runtime services
- Persistent volumes are mounted and writable
- Firewall and fail2ban are active

## WordPress

- Admin login works
- Media uploads work
- Permalinks work
- Email / password reset works
- Required plugins are configured

## Content

- Top migrated posts have been checked manually
- Important images render correctly
- Redirects from historic Blogger URLs are tested
- Trust pages exist and are linked in navigation/footer

## Search and Analytics

- Sitemap is live
- `robots.txt` is correct
- Search Console is verified
- Existing Search Console token has been reused or replaced intentionally
- Bing Webmaster Tools is verified
- IndexNow is enabled
- Site Kit is connected
- GA4 measurement ID `G-SCBVGKWD97` is reporting correctly
- AdSense publisher `ca-pub-9276619150182367` is connected only after trust pages are complete
- Analytics data is flowing

## Backups and Monitoring

- Database backup runs successfully
- WordPress content backup runs successfully
- Restore steps are understood
- HTTPS uptime monitoring is active

## Suggested Backup Cron Jobs

```cron
0 2 * * * cd /home/ubuntu/apps/ieltstask && bash scripts/backup-db.sh >> /home/ubuntu/backup.log 2>&1
30 2 * * * cd /home/ubuntu/apps/ieltstask && bash scripts/backup-wp.sh >> /home/ubuntu/backup.log 2>&1
```
