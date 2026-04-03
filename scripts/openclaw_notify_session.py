#!/usr/bin/env python3
import argparse
import base64
import json
import subprocess
import sys


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Resolve an OpenClaw session by key and deliver a message via that session.")
    ap.add_argument("--session-key", required=True)
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--message")
    grp.add_argument("--message-b64")
    ap.add_argument("--timeout", type=int, default=120)
    return ap.parse_args()


def load_message(args: argparse.Namespace) -> str:
    if args.message is not None:
        return args.message
    return base64.b64decode(args.message_b64).decode("utf-8")


def resolve_session_id(session_key: str) -> str:
    proc = subprocess.run(
        ["openclaw", "sessions", "--json"],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(proc.stdout)
    for sess in data.get("sessions", []):
        if sess.get("key") == session_key or sess.get("sessionId") == session_key:
            sid = sess.get("sessionId")
            if sid:
                return sid
    raise SystemExit(f"session not found: {session_key}")


def build_prompt(message: str) -> str:
    return (
        "Reply with EXACTLY the content between <BEGIN> and <END>. "
        "Do not add any other words. Preserve line breaks and tags like "
        "<qqimg>...</qqimg> verbatim.\n"
        "<BEGIN>\n"
        f"{message}\n"
        "<END>"
    )


def main() -> int:
    args = parse_args()
    message = load_message(args)
    session_id = resolve_session_id(args.session_key)
    prompt = build_prompt(message)
    proc = subprocess.run(
        [
            "openclaw",
            "agent",
            "--session-id",
            session_id,
            "--message",
            prompt,
            "--deliver",
            "--thinking",
            "off",
            "--timeout",
            str(args.timeout),
        ],
        check=True,
    )
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
