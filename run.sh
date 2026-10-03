#!/usr/bin/env bash
# One-command start: creates the venv on first run, installs deps, launches
# the app on http://localhost:8420
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
.venv/bin/pip install -q -r backend/requirements.txt

if [ ! -f .env ]; then
  echo "No .env found - copy .env.example to .env and set your ANTHROPIC_API_KEY first."
  exit 1
fi

exec .venv/bin/python3 -m backend.app
