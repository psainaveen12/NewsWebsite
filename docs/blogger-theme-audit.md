# Blogger Theme Audit

This file captures the operational details extracted from the provided Blogger XML so the WordPress migration preserves the parts that matter.

## Verified Existing Integrations

- Google Search Console verification token: `6WbeH24Nl3cffMo0M_o9NYTXpI5weva3_Fknw0SP08`
- GA4 measurement ID: `G-SCBVGKWD97`
- AdSense publisher ID: `ca-pub-9276619150182367`

## Current Brand Direction

- Primary accent color: `#fd3a13`
- Light background: `#f5f6f7`
- Dark footer / topbar background: `#16161a`
- Primary font family: `Roboto`

The starter WordPress theme in this repo has been aligned toward this palette so the cutover feels closer to the existing Blogger site instead of looking unrelated.

## Trust and Policy Pages Detected

The Blogger theme references these pages in topbar, footer, and trust sections:

- About Us
- Contact Us
- Privacy Policy
- Terms / Terms and Conditions
- Disclaimer
- Editorial Policy

Create the same pages in WordPress before applying for or re-enabling AdSense.

## Blogger Theme Behaviors Worth Preserving

- Clear ad disclosure messaging
- Footer trust block with legal links
- Search-friendly metadata and Open Graph tags
- Comment support and post-share links
- Mobile-responsive navigation and sticky header behavior

## Migration Mapping

| Blogger theme item | WordPress target |
| --- | --- |
| Search Console token | Site Kit or SEO plugin verification field |
| GA4 tag | Site Kit / Analytics connection |
| AdSense account meta | Site Kit / AdSense verification |
| Legal page links | Published WordPress pages and menu links |
| Accent color | `ieltstask-theme` palette |
| Editorial disclosure copy | Footer/trust content and article disclosure |
