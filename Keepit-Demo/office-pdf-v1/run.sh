#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ ! -x .venv/bin/python ]]; then
  echo 'Run ./setup.sh first, or use your own Python environment with requirements.txt.' >&2
  exit 1
fi
# Default is local-only. For a proxied preview use: ./run.sh --host 0.0.0.0 --port 8120
exec .venv/bin/python server.py "$@"
