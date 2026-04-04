#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

UTC = timezone.utc
WORKSPACE = Path("/home/XiaomiaoClaw/.openclaw/workspace")
DEFAULT_TUNNEL_STATE_FILE = WORKSPACE / ".openclaw" / "paper_digest_tunnel.json"
DEFAULT_NOTIFY_STATE_FILE = WORKSPACE / ".openclaw" / "paper_digest_tunnel_notify_state.json"
DEFAULT_NOTIFY_SCRIPT = WORKSPACE / "scripts" / "openclaw_notify_session.py"


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Watch the paper digest tunnel state and notify the QQ direct session when the public URL changes.")
    ap.add_argument("--session-key", required=True)
    ap.add_argument("--tunnel-state-file", default=str(DEFAULT_TUNNEL_STATE_FILE))
    ap.add_argument("--notify-state-file", default=str(DEFAULT_NOTIFY_STATE_FILE))
    ap.add_argument("--notify-script", default=str(DEFAULT_NOTIFY_SCRIPT))
    ap.add_argument("--poll-seconds", type=float, default=20.0)
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--once", action="store_true")
    return ap.parse_args()


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def get_current_public_url(path: Path) -> str | None:
    data = load_json(path)
    if data.get("status") != "active":
        return None
    url = data.get("public_url")
    if isinstance(url, str) and url.strip():
        return url.strip().rstrip("/")
    return None


def build_message(base_url: str) -> str:
    base = base_url.rstrip("/")
    return "\n".join(
        [
            "论文晨报外链更新了，最新地址在这里：",
            "",
            f"- 主入口\n{base}/paper_digest/index.html",
            f"- PC 版\n{base}/paper_digest/desktop.html",
            f"- 手机版\n{base}/paper_digest/mobile.html",
            "",
            "旧链接已经失效，收藏新的这个就行。=^･ω･^=",
        ]
    )


def send_notification(notify_script: Path, session_key: str, message: str, timeout: int) -> tuple[bool, str]:
    cmd = [
        sys.executable,
        str(notify_script),
        "--session-key",
        session_key,
        "--message",
        message,
        "--timeout",
        str(timeout),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    output = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode == 0, output.strip()


def ensure_state_defaults(state: dict) -> dict:
    return {
        "initialized": bool(state.get("initialized", False)),
        "last_seen_url": state.get("last_seen_url") if isinstance(state.get("last_seen_url"), str) else None,
        "last_notified_url": state.get("last_notified_url") if isinstance(state.get("last_notified_url"), str) else None,
        "updated_at": state.get("updated_at") if isinstance(state.get("updated_at"), str) else None,
    }


def run_once(args: argparse.Namespace) -> None:
    tunnel_state_path = Path(args.tunnel_state_file)
    notify_state_path = Path(args.notify_state_file)
    notify_script = Path(args.notify_script)

    current_url = get_current_public_url(tunnel_state_path)
    state = ensure_state_defaults(load_json(notify_state_path))

    if not state["initialized"]:
        state.update(
            {
                "initialized": True,
                "last_seen_url": current_url,
                "last_notified_url": current_url,
                "updated_at": now_iso(),
            }
        )
        save_json(notify_state_path, state)
        print(f"initialized notify baseline: {current_url or '(no active url)'}")
        return

    changed = current_url is not None and current_url != state["last_notified_url"]
    if changed:
        message = build_message(current_url)
        ok, output = send_notification(notify_script, args.session_key, message, args.timeout)
        if ok:
            state["last_notified_url"] = current_url
            print(f"notification sent for updated url: {current_url}")
        else:
            print(f"notification failed for url: {current_url}")
            if output:
                print(output)
    elif current_url != state["last_seen_url"]:
        print(f"observed url/state change without notification: {state['last_seen_url']} -> {current_url}")

    state["last_seen_url"] = current_url
    state["updated_at"] = now_iso()
    save_json(notify_state_path, state)


def main() -> int:
    args = parse_args()
    poll_seconds = max(5.0, float(args.poll_seconds))
    try:
        while True:
            run_once(args)
            if args.once:
                return 0
            time.sleep(poll_seconds)
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
