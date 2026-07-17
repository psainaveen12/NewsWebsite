#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"
require_command curl
load_env

[ "${APP_ENV:-}" = "production" ] || { echo "APP_ENV must be production." >&2; exit 1; }
curl -fsS --max-time 20 "$APP_BASE_URL/healthz" | grep -q '"status":"ok"'
curl -fsS --max-time 20 "$APP_BASE_URL/" | grep -qi '<title>'
curl -fsS --max-time 20 "$APP_BASE_URL/robots.txt" | grep -Fq "$APP_BASE_URL/sitemap.xml"
curl -fsS --max-time 20 "$APP_BASE_URL/sitemap.xml" | grep -q '<urlset'
curl -fsS --max-time 20 "$APP_BASE_URL/api/v1/articles?limit=1" | grep -q '"items"'
curl -fsSI --max-time 20 "$APP_BASE_URL/login" | grep -qi '^x-robots-tag: noindex, nofollow'
curl -fsSI --max-time 20 "$APP_BASE_URL/" | grep -qi '^strict-transport-security:'
curl -fsSI --max-time 20 "http://$APP_DOMAIN/" | grep -Eq '^HTTP/[^ ]+ (301|302|307|308)'

for page in about-us contact-us privacy-policy terms-and-conditions disclaimer editorial-policy; do
  status="$(curl -sS -o /dev/null -w '%{http_code}' "$APP_BASE_URL/p/$page")"
  [ "$status" = "200" ] || echo "WARNING: trust page /p/$page returned $status" >&2
done

echo "Production HTTPS, headers, public routes, JSON API, robots and sitemap checks passed."
