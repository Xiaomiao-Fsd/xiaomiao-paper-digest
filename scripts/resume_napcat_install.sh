#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="/home/XiaomiaoClaw/.openclaw/napcat-shell"
INSTALLER="/home/XiaomiaoClaw/.openclaw/workspace/tmp/napcat-install.sh"
ZIP_PATH="$TARGET_DIR/NapCat.Shell.zip"

cd "$TARGET_DIR"

echo "[resume] cwd: $(pwd)"
if [[ -f "$ZIP_PATH" ]]; then
  echo "[resume] found local package:"
  ls -lh "$ZIP_PATH"
  sha256sum "$ZIP_PATH" || true
else
  echo "[resume] local package missing: $ZIP_PATH"
fi

echo "[resume] launching installer: $INSTALLER"
bash "$INSTALLER"
