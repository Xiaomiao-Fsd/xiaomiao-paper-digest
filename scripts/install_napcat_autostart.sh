#!/usr/bin/env bash
set -euo pipefail

AUTOSTART_DIR="${HOME}/.config/autostart"
DESKTOP_FILE="${AUTOSTART_DIR}/napcat-qq.desktop"
START_SCRIPT="/home/huangchengbin/.openclaw/workspace/scripts/start_napcat_qq.sh"

mkdir -p "${AUTOSTART_DIR}"

cat > "${DESKTOP_FILE}" <<EOF
[Desktop Entry]
Type=Application
Version=1.0
Name=NapCat QQ Background
Comment=Start NapCat-injected QQ in background on login
Exec=/usr/bin/env NAPCAT_AUTOSTART=1 NAPCAT_AUTOSTART_DELAY=8 ${START_SCRIPT}
Terminal=false
X-GNOME-Autostart-enabled=true
StartupNotify=false
Categories=Utility;
EOF

printf 'Installed autostart entry: %s\n' "${DESKTOP_FILE}"
