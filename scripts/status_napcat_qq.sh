#!/usr/bin/env bash
set -euo pipefail

PROFILE_DIR="${NAPCAT_PROFILE_DIR:-/home/huangchengbin/.openclaw/qq-napcat-profile-x11fix}"
LOG_FILE="${NAPCAT_LOG_FILE:-/home/huangchengbin/.openclaw/napcat-shell/napcat-x11fix.log}"
QQ_BIN="${QQ_BIN:-/opt/QQ/qq}"

if ps -eo pid=,etime=,cmd= | awk -v profile="${PROFILE_DIR}" -v q="${QQ_BIN}" 'index($0, profile) && index($0, q) && $0 !~ /awk -v/ {found=1; print} END {exit found ? 0 : 1}'; then
  echo
  echo "WebUI listeners:"
  ss -ltnp 2>/dev/null | grep ':6099 ' || true
  echo
  echo "Last log lines:"
  tail -n 20 "${LOG_FILE}" 2>/dev/null || true
else
  echo "NapCat QQ is not running."
fi
