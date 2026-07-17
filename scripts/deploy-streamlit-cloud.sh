#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENTRYPOINT="streamlit/streamlit_app.py"
REPOSITORY="${STREAMLIT_REPOSITORY:-psainaveen12/NewsWebsite}"
BRANCH="${STREAMLIT_BRANCH:-NewsWebsiteDocker}"

cd "$ROOT_DIR"

[[ -f "$ENTRYPOINT" ]] || { echo "Missing Streamlit entrypoint: $ENTRYPOINT" >&2; exit 1; }
[[ -f streamlit/requirements.txt ]] || { echo "Missing streamlit/requirements.txt" >&2; exit 1; }

python3 -m py_compile "$ENTRYPOINT"

if [[ "${1:-}" == "--local" ]]; then
  if ! python3 -c 'import streamlit' >/dev/null 2>&1; then
    echo "Streamlit is not installed. Run:" >&2
    echo "  python3 -m pip install -r streamlit/requirements.txt" >&2
    exit 1
  fi
  exec python3 -m streamlit run "$ENTRYPOINT"
fi

cat <<EOF
Streamlit deployment files passed validation.

Community Cloud deploy settings:
  Repository:      $REPOSITORY
  Branch:          $BRANCH
  Main file path:  $ENTRYPOINT
  Python version:  3.12 or newer

Deploy from: https://share.streamlit.io/

Optional Streamlit secret:
  NEWS_SITE_URL = "https://news.ieltstask.com"

Community Cloud performs the final deployment through its GitHub-authorized web
console. This entrypoint is a read-only frontend for the production RSS feed;
the FastAPI admin, PostgreSQL database, and Blogger importer remain in Docker.
EOF
