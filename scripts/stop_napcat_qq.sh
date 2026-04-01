#!/usr/bin/env bash
set -euo pipefail

PROFILE_DIR="${NAPCAT_PROFILE_DIR:-/home/XiaomiaoClaw/.openclaw/qq-napcat-profile-x11fix}"
NAPCAT_ROOT="${NAPCAT_ROOT:-/home/XiaomiaoClaw/.openclaw/napcat-shell}"
PID_FILE="${NAPCAT_PID_FILE:-${NAPCAT_ROOT}/napcat-qq.pid}"
QQ_BIN="${QQ_BIN:-/opt/QQ/qq}"
STOP_TIMEOUT="${NAPCAT_STOP_TIMEOUT:-15}"

find_pids() {
  ps -eo pid=,cmd= | awk -v profile="${PROFILE_DIR}" -v q="${QQ_BIN}" 'index($0, profile) && index($0, q) && $0 !~ /awk -v/ {print $1}'
}

mapfile -t PIDS < <(find_pids)

if [[ ${#PIDS[@]} -eq 0 ]]; then
  echo "NapCat QQ is not running."
  rm -f "${PID_FILE}"
  exit 0
fi

kill -TERM "${PIDS[@]}" 2>/dev/null || true

for _ in $(seq 1 "${STOP_TIMEOUT}"); do
  mapfile -t REMAINING < <(find_pids)
  if [[ ${#REMAINING[@]} -eq 0 ]]; then
    rm -f "${PID_FILE}"
    echo "Stopped NapCat QQ gracefully (${#PIDS[@]} process(es))."
    exit 0
  fi
  sleep 1
done

mapfile -t REMAINING < <(find_pids)
if [[ ${#REMAINING[@]} -gt 0 ]]; then
  kill -KILL "${REMAINING[@]}" 2>/dev/null || true
fi

rm -f "${PID_FILE}"
echo "Stopped NapCat QQ forcefully after waiting ${STOP_TIMEOUT}s (${#PIDS[@]} process(es))."
