#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-}"

supports_project() {
    "$1" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' >/dev/null 2>&1
}

if [[ -n "$PYTHON_BIN" ]]; then
    if ! supports_project "$PYTHON_BIN"; then
        printf 'Error: %s is unavailable or older than Python 3.9.\n' "$PYTHON_BIN" >&2
        exit 1
    fi
else
    for candidate in python3.12 python3.11 python3.10 python3.9 python3; do
        if command -v "$candidate" >/dev/null 2>&1 && supports_project "$candidate"; then
            PYTHON_BIN="$candidate"
            break
        fi
    done
fi

if [[ -z "$PYTHON_BIN" ]]; then
    printf 'Error: Python 3.9 or newer is required; Python 3.12 is recommended.\n' >&2
    printf 'Install it, then run: PYTHON_BIN=/path/to/python3.12 ./setup.sh\n' >&2
    exit 1
fi

# Remove only the incompatible virtual environment created by an earlier setup.
if [[ -x "$APP_DIR/.venv/bin/python" ]] && ! supports_project "$APP_DIR/.venv/bin/python"; then
    printf 'Removing the virtual environment created by an unsupported Python...\n'
    rm -rf "$APP_DIR/.venv"
fi

printf 'Using Python: '
"$PYTHON_BIN" --version
printf 'Creating Python virtual environment...\n'
"$PYTHON_BIN" -m venv "$APP_DIR/.venv"

printf 'Installing dependencies...\n'
"$APP_DIR/.venv/bin/python" -m pip install -r "$APP_DIR/requirements.txt"

printf 'Checking Python syntax...\n'
"$APP_DIR/.venv/bin/python" -m py_compile "$APP_DIR/transcribe.py"

printf 'Setup complete. Run:\n'
printf '  %s/run.sh "/path/to/audio.mp3"\n' "$APP_DIR"
