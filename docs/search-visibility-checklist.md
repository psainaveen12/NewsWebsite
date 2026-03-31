# Search Visibility Checklist

## Google Search Console

1. Add `https://www.ieltstask.com` as a property.
2. Prefer Domain verification if DNS access is available.
3. Submit the XML sitemap from your SEO plugin.
4. Review indexing, excluded pages, clicks, CTR, queries, and Core Web Vitals weekly during launch.

Existing Blogger verification token available for migration:

- `6WbeH24Nl3cffMo0M_o9NYTXpI5weva3_Fknw0SP08`

## Bing Webmaster Tools

1. Create or sign in to Bing Webmaster Tools.
2. Import the site from Search Console or add it manually.
3. Verify the property.
4. Confirm the sitemap is present and healthy.

## IndexNow

1. Install one IndexNow plugin and keep it minimal.
2. Generate and place the key file if the plugin requires it.
3. Confirm new and updated posts trigger notifications automatically.

## XML Sitemap and robots.txt

Use your SEO plugin's sitemap and keep `robots.txt` simple:

```txt
User-agent: *
Disallow: /wp-admin/
Allow: /wp-admin/admin-ajax.php
Sitemap: https://www.ieltstask.com/sitemap_index.xml
```

## Launch Monitoring

For the first few weeks after cutover, review:

- Search Console coverage and queries
- Bing crawl information
- Sitemap health
- Core Web Vitals
- Top landing pages in Analytics
