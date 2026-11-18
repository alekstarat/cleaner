#!/usr/bin/env bash
set -euo pipefail

TARGET="${HOME}/.local/bin/cleaner"
APP_DIR="${HOME}/.cleaner"

if [[ -e "$TARGET" ]]; then
  rm -f -- "$TARGET"
  echo "Removed: $TARGET"
else
  echo "Executable not found: $TARGET"
fi

if [[ -d "$APP_DIR" ]]; then
  read -r -p "Remove config directory ${APP_DIR} too? [y/N] " answer
  case "${answer,,}" in
    y|yes)
      rm -rf -- "$APP_DIR"
      echo "Removed: $APP_DIR"
      ;;
    *)
      echo "Config preserved: $APP_DIR"
      ;;
  esac
fi

echo "Uninstallation complete."
