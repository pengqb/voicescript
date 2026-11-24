#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$APP_DIR/.venv/bin/python"

if [[ ! -x "$PYTHON" ]]; then
    printf 'Dependencies are not installed. Run: %s/setup.sh\n' "$APP_DIR" >&2
    exit 1
fi

if (( $# == 0 )); then
    printf 'Usage: %s <audio.mp3> [-o output.txt] [--timestamps] [--overwrite]\n' "$0" >&2
    exit 1
fi

exec "$PYTHON" "$APP_DIR/transcribe.py" "$@"
