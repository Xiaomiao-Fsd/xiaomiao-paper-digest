#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="/home/XiaomiaoClaw/.openclaw/workspace"
RUNTIME="$WORKSPACE/.n8n-runtime"
NODE="$RUNTIME/node_modules/node/bin/node"
N8N="$RUNTIME/node_modules/n8n/bin/n8n"

if [[ ! -x "$NODE" || ! -f "$N8N" ]]; then
  echo "n8n runtime is missing: $RUNTIME" >&2
  exit 1
fi

export N8N_USER_FOLDER="$WORKSPACE/.n8n-data"
export N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=false
export N8N_RUNNERS_ENABLED=true
export N8N_HOST=127.0.0.1
export N8N_PORT=5678
export N8N_PROTOCOL=http
export N8N_DIAGNOSTICS_ENABLED=false
export N8N_PERSONALIZATION_ENABLED=false
export N8N_VERSION_NOTIFICATIONS_ENABLED=false
export N8N_TEMPLATES_ENABLED=false
export N8N_SECURE_COOKIE=false

exec "$NODE" "$N8N" start
