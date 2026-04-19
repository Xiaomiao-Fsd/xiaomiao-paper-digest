#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="/home/XiaomiaoClaw/.openclaw/workspace"
SRC_DIR="$WORKSPACE/reports/paper_digest"
TMP_ROOT="${TMPDIR:-/tmp}/paper-digest-main-sync"
REPO_DIR="$TMP_ROOT/repo"
REPO_URL="https://github.com/Xiaomiao-Fsd/xiaomiao-paper-digest.git"
BRANCH="main"
MODE="latest-only"

if [[ "${1:-}" == "--mode" ]]; then
  MODE="${2:-latest-only}"
fi

export HTTPS_PROXY="${HTTPS_PROXY:-http://127.0.0.1:7897}"
export HTTP_PROXY="${HTTP_PROXY:-http://127.0.0.1:7897}"

mkdir -p "$TMP_ROOT"
rm -rf "$REPO_DIR"

git clone --branch "$BRANCH" --single-branch "$REPO_URL" "$REPO_DIR"

case "$MODE" in
  latest-only)
    cp "$SRC_DIR/latest.json" "$REPO_DIR/latest.json"
    TARGETS=(latest.json)
    COMMIT_MSG="Update paper digest latest.json only"
    ;;
  full)
    cp "$SRC_DIR/index.html" "$REPO_DIR/index.html"
    cp "$SRC_DIR/desktop.html" "$REPO_DIR/desktop.html"
    cp "$SRC_DIR/mobile.html" "$REPO_DIR/mobile.html"
    cp "$SRC_DIR/latest.json" "$REPO_DIR/latest.json"
    TARGETS=(index.html desktop.html mobile.html latest.json)
    COMMIT_MSG="Update pages digest artifacts"
    ;;
  *)
    echo "Unknown mode: $MODE" >&2
    exit 2
    ;;
esac

cd "$REPO_DIR"
git config user.name "OpenClaw"
git config user.email "openclaw@local"

if git diff --quiet -- "${TARGETS[@]}"; then
  echo "No pages changes to publish."
  exit 0
fi

git add "${TARGETS[@]}"
git commit -m "$COMMIT_MSG"
git push origin "$BRANCH"

echo "Published paper digest pages to $BRANCH with mode=$MODE"
