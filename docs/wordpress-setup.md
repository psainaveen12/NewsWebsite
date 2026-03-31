# WordPress Setup

## Baseline Install

After DNS resolves to the server and HTTPS is active:

1. Open `https://www.ieltstask.com`.
2. Complete the WordPress installation wizard.
3. Set both Site Address and WordPress Address to `https://www.ieltstask.com`.
4. Change permalinks to `Post name`.
5. Set timezone, homepage, posts page, discussion policy, and media defaults.
6. Remove unused themes and plugins.
7. Recreate the legal and trust pages that exist in Blogger before monetization cutover.

## Starter Theme

This repo includes `wordpress/wp-content/themes/ieltstask-theme/` as a lightweight starter theme.

Recommended next steps after install:

1. Activate `IELTSTask Theme`.
2. Create navigation menus.
3. Create trust pages:
   - About
   - Contact
   - Privacy Policy
   - Terms
   - Disclaimer
   - Editorial Policy

## Required Plugin Categories

Use the smallest plugin set that covers these needs:

- Site Kit by Google
- One SEO plugin
- Redirection
- SMTP / transactional email
- Security / login hardening
- Image optimization
- IndexNow

## Existing Blogger IDs To Reuse

These values were found in the current Blogger XML and should be migrated into WordPress integrations instead of creating disconnected replacements:

| Integration | Current value |
| --- | --- |
| Search Console verification | `6WbeH24Nl3cffMo0M_o9NYTXpI5weva3_Fknw0SP08` |
| GA4 | `G-SCBVGKWD97` |
| AdSense publisher | `ca-pub-9276619150182367` |

## Settings to Confirm

| Area | Expected value |
| --- | --- |
| Site URL | `https://www.ieltstask.com` |
| Permalinks | `Post name` |
| Users | Separate admin and editor accounts |
| Comments | Decide policy before importing Blogger content |
| Media | Confirm large upload handling and thumbnails |
