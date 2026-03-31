# Blogger Migration Checklist

## Source Context

- Target site: `https://www.ieltstask.com`
- Blogger admin URL: `https://www.blogger.com/u/0/blog/posts/1194349556968361444`
- Recommended import source: Google Takeout `feed.atom`

## Before Import

1. Export Blogger content through Google Takeout.
2. Save the current Blogger theme backup.
3. Capture screenshots of key landing pages and high-traffic posts.
4. Prepare a list of the top-value URLs to verify after cutover.
5. Finish WordPress production setup before importing.

## Import Flow

1. Install a Blogger importer plugin in WordPress.
2. Import the Takeout `feed.atom` file into the live production stack.
3. Validate counts for:
   - posts
   - pages
   - labels or categories
   - comments
   - media references

## QA Checklist

| Check | Expected result |
| --- | --- |
| Post count | Import count is close to the Blogger source count |
| Images | No broken hero or inline images |
| Metadata | Titles, dates, descriptions, and taxonomy survive import |
| Internal links | Old references resolve correctly |
| Top URLs | Highest-value historical content renders correctly |
| Redirects | Old Blogger patterns resolve with `301` to canonical URLs |

## Repairs Likely Needed

- Replace missing Blogger-hosted image URLs
- Fix inline HTML cleanup issues
- Re-map old internal links
- Preserve or redirect legacy slugs
- Recheck embedded videos and tables

## After Import

1. Test the most important migrated URLs manually.
2. Submit the sitemap again in Search Console and Bing.
3. Inspect the highest-value URLs in Search Console after launch.
