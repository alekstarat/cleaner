#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${HOME}/.local/bin"
APP_DIR="${HOME}/.cleaner"
SOURCE="${SCRIPT_DIR}/cleaner.py"
TARGET="${BIN_DIR}/cleaner"
CONFIG="${APP_DIR}/cleaner.conf"

if [[ ! -f "$SOURCE" ]]; then
  echo "Error: cleaner.py was not found next to install.sh" >&2
  exit 1
fi

mkdir -p "$BIN_DIR" "$APP_DIR"
install -m 755 "$SOURCE" "$TARGET"

if [[ ! -e "$CONFIG" ]]; then
  if [[ -f "${SCRIPT_DIR}/cleaner.conf" ]]; then
    install -m 644 "${SCRIPT_DIR}/cleaner.conf" "$CONFIG"
  else
    echo "Error: cleaner.conf was not found next to install.sh" >&2
    exit 1
  fi
else
  echo "Existing config preserved: $CONFIG"
fi

echo "Installed: $TARGET"
echo "Config:    $CONFIG"
case ":${PATH}:" in
  *":${BIN_DIR}:"*) ;;
  *) echo "Add this to your shell profile if cleaner is not found:"
     echo 'export PATH="$HOME/.local/bin:$PATH"' ;;
esac
echo "Run 'cleaner --dry-run' to preview cleanup in the current directory."
