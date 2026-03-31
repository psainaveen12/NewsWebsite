# Blogger Theme Audit

This file captures the operational details extracted from the provided Blogger XML so the WordPress migration preserves the parts that matter.

## Verified Existing Integrations

- Google Search Console verification token: `6WbeH24Nl3cffMo0M_o9NYTXpI5weva3_Fknw0SP08`
- GA4 measurement ID: `G-SCBVGKWD97`
- AdSense publisher ID: `ca-pub-9276619150182367`

## Current Brand Direction

- Primary accent color: `#fd3a13`
- Light background: `#f5f6f7`
- Dark footer and topbar background: `#16161a`
- Primary font family: `Roboto`

The starter WordPress theme in this repo has been aligned toward this palette so the cutover feels closer to the existing Blogger site instead of looking unrelated.

## Trust And Policy Pages Detected

The Blogger XML references these pages in the topbar, footer, and trust sections:

- About Us: `/p/about-us.html`
- Contact Us: `/p/contact-us.html`
- Privacy Policy: `/p/privacy-policy.html`
- Terms and Conditions: `/p/terms-and-conditions.html`
- Disclaimer: `/p/disclaimer.html`
- Editorial Policy: `/p/editorial-policy.html`

Create matching WordPress pages and keep the slugs aligned before applying for or re-enabling AdSense.

## Blogger Theme Structure Worth Preserving

The XML is not only a color system. It defines several structural expectations that should survive the migration:

- Dark topbar with legal and utility links
- Sticky header with brand, primary navigation, and search
- Homepage sections for ticker, featured posts, content blocks, and sidebar widgets
- Two-column content layout with a roughly `320px` sidebar
- Article pages with breadcrumbs, author/date metadata, labels, sharing links, comments, and related content
- Footer trust statement followed by legal links and a secondary footer menu
- Cookie consent, ad slots, and disclosure language that reinforce policy compliance

## Blogger Theme Behaviors Worth Preserving

- Clear ad disclosure messaging
- Footer trust block with legal links
- Search-friendly metadata and Open Graph tags
- Comment support and post-share links
- Mobile-responsive navigation and sticky header behavior

## Blogger-Specific Notes From The XML

- The Blogger XML contains a `NewsArticle` JSON-LD block on post pages.
- The footer trust message already uses strong compliance language around independent editorial content and ad identification.
- The sidebar and footer are widget-driven, so the WordPress port should keep widget areas instead of hardcoding everything.
- A generic Disqus shortname (`probloggertemplates`) appears in the XML and should be treated as template residue, not production configuration.
- Several menu labels in the XML look template-generic rather than IELTS-specific, so they should be reviewed during content migration instead of copied blindly.

## WordPress Starter Theme Alignment Added

- Custom logo support
- Top bar, primary, footer, and social menu locations
- Sidebar widget area with policy/search fallback content
- Breadcrumbs on posts, pages, archives, and error states
- Share links on single posts
- Footer trust panel plus exact legal page targets based on the XML
- Two-column layout so the site feels like the current Blogger structure during migration

## Migration Mapping

| Blogger theme item | WordPress target |
| --- | --- |
| Search Console token | Site Kit or SEO plugin verification field |
| GA4 tag | Site Kit or Analytics connection |
| AdSense account meta | Site Kit or AdSense verification |
| Legal page links | Published WordPress pages and menu links |
| Accent color | `ieltstask-theme` palette |
| Editorial disclosure copy | Footer/trust content and article disclosure |
