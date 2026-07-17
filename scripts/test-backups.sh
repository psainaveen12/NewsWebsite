#!/usr/bin/env bash
set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"
require_command docker
require_command gzip
load_env

DB_BACKUP="${1:-$(find "$(backup_root)/db" -type f -name '*.sql.gz' -print 2>/dev/null | sort | tail -1)}"
MEDIA_BACKUP="${2:-$(find "$(backup_root)/media" -type f -name '*.tar.gz' -print 2>/dev/null | sort | tail -1)}"
[ -f "$DB_BACKUP" ] || { echo "No database backup found." >&2; exit 1; }
[ -f "$MEDIA_BACKUP" ] || { echo "No media backup found." >&2; exit 1; }

gzip -t "$DB_BACKUP"
tar -tzf "$MEDIA_BACKUP" >/dev/null

VERIFY_DB="restore_verify_$(date +%s)"
cleanup() { docker_compose exec -T db dropdb -U "$POSTGRES_USER" --if-exists "$VERIFY_DB" >/dev/null 2>&1 || true; }
trap cleanup EXIT
docker_compose exec -T db createdb -U "$POSTGRES_USER" "$VERIFY_DB"
gzip -dc "$DB_BACKUP" | docker_compose exec -T db psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$VERIFY_DB" >/dev/null
docker_compose exec -T db psql -U "$POSTGRES_USER" -d "$VERIFY_DB" -Atc "SELECT count(*) FROM articles" >/dev/null
echo "Database and media backups passed an isolated restore verification."
