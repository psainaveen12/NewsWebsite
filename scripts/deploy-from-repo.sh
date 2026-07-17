#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${REPO_URL:-${1:-}}"
BRANCH="${DEPLOY_BRANCH:-${2:-NewsWebsiteDocker}}"
TARGET_DIR="${DEPLOY_DIR:-${3:-$PWD/newswebsite}}"

if [ -z "$REPO_URL" ]; then
  echo "Usage: bash deploy-from-repo.sh REPO_URL [BRANCH] [TARGET_DIR]" >&2
  exit 1
fi
git check-ref-format --branch "$BRANCH" >/dev/null

if [ ! -d "$TARGET_DIR/.git" ]; then
  git clone --branch "$BRANCH" --single-branch "$REPO_URL" "$TARGET_DIR"
fi
if [ ! -f "$TARGET_DIR/.env" ]; then
  cp "$TARGET_DIR/.env.example" "$TARGET_DIR/.env"
  echo "Created $TARGET_DIR/.env. Set production secrets, then rerun." >&2
  exit 2
fi

DEPLOY_BRANCH="$BRANCH" bash "$TARGET_DIR/scripts/deploy.sh" "$BRANCH"
