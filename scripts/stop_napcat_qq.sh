#!/usr/bin/env bash
set -euo pipefail

PROFILE_DIR="${NAPCAT_PROFILE_DIR:-/home/huangchengbin/.openclaw/qq-napcat-profile-x11fix}"
NAPCAT_ROOT="${NAPCAT_ROOT:-/home/huangchengbin/.openclaw/napcat-shell}"
PID_FILE="${NAPCAT_PID_FILE:-${NAPCAT_ROOT}/napcat-qq.pid}"
QQ_BIN="${QQ_BIN:-/opt/QQ/qq}"

mapfile -t PIDS < <(ps -eo pid=,cmd= | awk -v profile="${PROFILE_DIR}" -v q="${QQ_BIN}" 'index($0, profile) && index($0, q) && $0 !~ /awk -v/ {print $1}')

if [[ ${#PIDS[@]} -eq 0 ]]; then
  echo "NapCat QQ is not running."
  rm -f "${PID_FILE}"
  exit 0
fi

kill -TERM "${PIDS[@]}" 2>/dev/null || true
sleep 2

mapfile -t REMAINING < <(ps -eo pid=,cmd= | awk -v profile="${PROFILE_DIR}" -v q="${QQ_BIN}" 'index($0, profile) && index($0, q) && $0 !~ /awk -v/ {print $1}')
if [[ ${#REMAINING[@]} -gt 0 ]]; then
  kill -KILL "${REMAINING[@]}" 2>/dev/null || true
fi

rm -f "${PID_FILE}"
echo "Stopped NapCat QQ (${#PIDS[@]} process(es))."
