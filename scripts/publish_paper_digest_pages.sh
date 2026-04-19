#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="/home/XiaomiaoClaw/.openclaw/workspace"
SRC_DIR="$WORKSPACE/reports/paper_digest"
TMP_ROOT="${TMPDIR:-/tmp}/paper-digest-main-sync"
REPO_DIR="$TMP_ROOT/repo"
REPO_URL="https://github.com/Xiaomiao-Fsd/xiaomiao-paper-digest.git"
BRANCH="main"

export HTTPS_PROXY="${HTTPS_PROXY:-http://127.0.0.1:7897}"
export HTTP_PROXY="${HTTP_PROXY:-http://127.0.0.1:7897}"

mkdir -p "$TMP_ROOT"
rm -rf "$REPO_DIR"

git clone --branch "$BRANCH" --single-branch "$REPO_URL" "$REPO_DIR"

cp "$SRC_DIR/index.html" "$REPO_DIR/index.html"
cp "$SRC_DIR/desktop.html" "$REPO_DIR/desktop.html"
cp "$SRC_DIR/mobile.html" "$REPO_DIR/mobile.html"
cp "$SRC_DIR/latest.json" "$REPO_DIR/latest.json"

cd "$REPO_DIR"
git config user.name "OpenClaw"
git config user.email "openclaw@local"

if git diff --quiet -- index.html desktop.html mobile.html latest.json; then
  echo "No pages changes to publish."
  exit 0
fi

git add index.html desktop.html mobile.html latest.json
git commit -m "Update pages digest artifacts"
git push origin "$BRANCH"

echo "Published paper digest pages to $BRANCH"
