#!/usr/bin/env bash
set -euo pipefail

USER_ID="$(id -u)"
RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/${USER_ID}}"
WORKSPACE="${WORKSPACE:-/home/XiaomiaoClaw/.openclaw/workspace}"
NAPCAT_ROOT="${NAPCAT_ROOT:-/home/XiaomiaoClaw/.openclaw/napcat-shell}"
PROFILE_DIR="${NAPCAT_PROFILE_DIR:-/home/XiaomiaoClaw/.openclaw/qq-napcat-profile-x11fix}"
LOG_FILE="${NAPCAT_LOG_FILE:-${NAPCAT_ROOT}/napcat-x11fix.log}"
PID_FILE="${NAPCAT_PID_FILE:-${NAPCAT_ROOT}/napcat-qq.pid}"
QQ_BIN="${QQ_BIN:-/opt/QQ/qq}"
DISPLAY_VALUE="${DISPLAY:-:0}"
AUTOSTART_DELAY="${NAPCAT_AUTOSTART_DELAY:-15}"
XAUTH_WAIT_SECONDS="${NAPCAT_XAUTH_WAIT_SECONDS:-30}"

log() {
  printf '[%s] %s\n' "$(date '+%F %T')" "$*"
}

find_xauthority() {
  if [[ -n "${XAUTHORITY:-}" && -f "${XAUTHORITY}" ]]; then
    printf '%s\n' "${XAUTHORITY}"
    return 0
  fi

  local candidate
  for candidate in \
    "${RUNTIME_DIR}"/.mutter-Xwaylandauth.* \
    "${HOME}/.Xauthority"
  do
    if [[ -f "${candidate}" ]]; then
      printf '%s\n' "${candidate}"
      return 0
    fi
  done

  return 1
}

wait_for_xauthority() {
  local waited=0
  local found

  while (( waited < XAUTH_WAIT_SECONDS )); do
    found="$(find_xauthority || true)"
    if [[ -n "${found}" ]]; then
      printf '%s\n' "${found}"
      return 0
    fi
    sleep 1
    waited=$((waited + 1))
  done

  return 1
}

is_running() {
  ps -eo cmd= | grep -F -- "${QQ_BIN} " | grep -F -- "--user-data-dir=${PROFILE_DIR}" >/dev/null 2>&1
}

if [[ ! -x "${QQ_BIN}" ]]; then
  echo "QQ binary not found or not executable: ${QQ_BIN}" >&2
  exit 1
fi

if [[ "${NAPCAT_AUTOSTART:-0}" == "1" ]]; then
  log "Autostart detected, delaying launch for ${AUTOSTART_DELAY}s."
  sleep "${AUTOSTART_DELAY}"
fi

mkdir -p "${NAPCAT_ROOT}" "${PROFILE_DIR}"
touch "${LOG_FILE}"

if is_running; then
  echo "NapCat QQ already running with profile ${PROFILE_DIR}"
  exit 0
fi

XAUTH_FILE="$(wait_for_xauthority || true)"
if [[ -z "${XAUTH_FILE}" ]]; then
  echo "Unable to locate XAUTHORITY file for X11 startup after ${XAUTH_WAIT_SECONDS}s." >&2
  exit 1
fi

cd "${NAPCAT_ROOT}"

log "Launching NapCat QQ on DISPLAY=${DISPLAY_VALUE} with profile ${PROFILE_DIR}."
nohup env -u WAYLAND_DISPLAY \
  DISPLAY="${DISPLAY_VALUE}" \
  XAUTHORITY="${XAUTH_FILE}" \
  NAPCAT_BOOTMAIN="${NAPCAT_ROOT}" \
  NAPCAT_WORKDIR="${NAPCAT_ROOT}" \
  LD_PRELOAD=./libnapcat_launcher.so \
  "${QQ_BIN}" --no-sandbox --user-data-dir="${PROFILE_DIR}" \
  >> "${LOG_FILE}" 2>&1 &

CHILD_PID=$!
printf '%s\n' "${CHILD_PID}" > "${PID_FILE}"
echo "Started NapCat QQ (pid ${CHILD_PID})"
