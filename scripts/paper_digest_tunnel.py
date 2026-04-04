#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
import re

UTC = timezone.utc
WORKSPACE = Path("/home/XiaomiaoClaw/.openclaw/workspace")
DEFAULT_STATE_FILE = WORKSPACE / ".openclaw" / "paper_digest_tunnel.json"
URL_RE = re.compile(r"https?://[^\s\]]+")
VALID_SUFFIXES = (".lhr.life", ".lhr.rocks")
BLOCKED_LOCALHOST_RUN_HOSTS = {"localhost.run", "www.localhost.run", "admin.localhost.run"}


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Run a localhost.run tunnel for the paper digest and persist the current public URL.")
    ap.add_argument("--local-port", type=int, default=8091)
    ap.add_argument("--state-file", default=str(DEFAULT_STATE_FILE))
    ap.add_argument("--ssh-host", default="localhost.run")
    ap.add_argument("--ssh-user", default="nokey")
    return ap.parse_args()


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def write_state(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def extract_public_url(line: str) -> str | None:
    for raw in URL_RE.findall(line):
        cleaned = raw.rstrip(').,;\"\'')
        parsed = urlsplit(cleaned)
        host = (parsed.netloc or "").lower()
        if not host:
            continue
        is_tunnel_host = host.endswith(VALID_SUFFIXES) or (
            host.endswith(".localhost.run") and host not in BLOCKED_LOCALHOST_RUN_HOSTS
        )
        if is_tunnel_host:
            if parsed.path.startswith("/docs") or parsed.path.startswith("/faq"):
                continue
            return cleaned
    return None


def main() -> int:
    args = parse_args()
    state_path = Path(args.state_file)
    write_state(
        state_path,
        {
            "status": "starting",
            "updated_at": now_iso(),
            "local_port": args.local_port,
            "ssh_host": args.ssh_host,
            "ssh_user": args.ssh_user,
        },
    )

    cmd = [
        "/usr/bin/ssh",
        "-T",
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "UserKnownHostsFile=/dev/null",
        "-o",
        "ServerAliveInterval=30",
        "-o",
        "ExitOnForwardFailure=yes",
        "-R",
        f"80:127.0.0.1:{args.local_port}",
        f"{args.ssh_user}@{args.ssh_host}",
    ]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    current_url = None
    assert proc.stdout is not None
    for line in proc.stdout:
        sys.stdout.write(line)
        sys.stdout.flush()
        public_url = extract_public_url(line)
        if public_url and public_url != current_url:
            current_url = public_url
            write_state(
                state_path,
                {
                    "status": "active",
                    "updated_at": now_iso(),
                    "local_port": args.local_port,
                    "ssh_host": args.ssh_host,
                    "ssh_user": args.ssh_user,
                    "public_url": public_url,
                },
            )

    code = proc.wait()
    payload = {
        "status": "exited" if code == 0 else "error",
        "updated_at": now_iso(),
        "local_port": args.local_port,
        "ssh_host": args.ssh_host,
        "ssh_user": args.ssh_user,
        "exit_code": code,
    }
    if current_url:
        payload["last_public_url"] = current_url
    write_state(state_path, payload)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
