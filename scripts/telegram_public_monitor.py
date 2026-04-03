#!/usr/bin/env python3
import argparse
import json
import re
import sys
import time
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional
from urllib.parse import quote

import requests

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Safari/537.36"


@dataclass
class Post:
    post: str
    id: int
    url: str
    datetime: str
    time_label: str
    author: str
    text: str


class TelegramPublicPageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items: list[dict] = []
        self.cur: Optional[dict] = None
        self.capture_text = False
        self.text_depth = 0
        self.text_started = False
        self.capture_author = False
        self.capture_time = False

    def _finalize(self) -> None:
        if not self.cur:
            return
        text = self.cur["text"]
        text = text.replace("\xa0", " ")
        text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
        self.cur["text"] = text.strip()
        self.cur["author"] = self.cur["author"].strip()
        self.cur["time_label"] = self.cur["time_label"].strip()
        self.items.append(self.cur)
        self.cur = None
        self.capture_text = False
        self.text_depth = 0
        self.text_started = False
        self.capture_author = False
        self.capture_time = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        cls = attrs.get("class", "")
        if tag == "div" and "data-post" in attrs and "tgme_widget_message" in cls:
            self._finalize()
            self.cur = {
                "post": attrs["data-post"],
                "url": "",
                "datetime": "",
                "time_label": "",
                "author": "",
                "text": "",
            }
            return

        if not self.cur:
            return

        if self.capture_text and tag == "div":
            self.text_depth += 1
        elif tag == "div" and "tgme_widget_message_text" in cls and not self.text_started:
            self.capture_text = True
            self.text_started = True
            self.text_depth = 1
        elif tag == "br" and self.capture_text:
            self.cur["text"] += "\n"
        elif tag == "a" and "tgme_widget_message_date" in cls:
            self.cur["url"] = attrs.get("href", "")
        elif tag == "time":
            self.cur["datetime"] = attrs.get("datetime", "")
            self.capture_time = True
        elif tag == "span" and "tgme_widget_message_from_author" in cls:
            self.capture_author = True

    def handle_endtag(self, tag):
        if self.capture_text and tag == "div":
            self.text_depth -= 1
            if self.text_depth <= 0:
                self.capture_text = False
        if self.capture_author and tag == "span":
            self.capture_author = False
        if self.capture_time and tag == "time":
            self.capture_time = False

    def handle_data(self, data):
        if not self.cur:
            return
        if self.capture_text:
            self.cur["text"] += data
        elif self.capture_author:
            self.cur["author"] += data
        elif self.capture_time:
            self.cur["time_label"] += data

    def close(self):
        super().close()
        self._finalize()


def normalize_channel_url(raw: str) -> str:
    raw = raw.strip()
    raw = raw.removeprefix("https://")
    raw = raw.removeprefix("http://")
    raw = raw.removeprefix("t.me/")
    raw = raw.removeprefix("telegram.me/")
    raw = raw.removeprefix("s/")
    raw = raw.strip("/")
    if not raw:
        raise ValueError("empty channel path")
    return f"https://t.me/s/{quote(raw)}"


def fetch_page(url: str, before: Optional[int], proxy: Optional[str]) -> list[Post]:
    page_url = url if before is None else f"{url}?before={before}"
    proxies = None
    if proxy:
        proxies = {"http": proxy, "https": proxy}
    r = requests.get(page_url, headers={"User-Agent": UA}, proxies=proxies, timeout=30)
    r.raise_for_status()
    parser = TelegramPublicPageParser()
    parser.feed(r.text)
    parser.close()
    posts: list[Post] = []
    for item in parser.items:
        try:
            pid = int(item["post"].split("/")[-1])
        except Exception:
            continue
        posts.append(Post(
            post=item["post"],
            id=pid,
            url=item["url"],
            datetime=item["datetime"],
            time_label=item["time_label"],
            author=item["author"] or "频道",
            text=item["text"],
        ))
    posts.sort(key=lambda x: x.id)
    return posts


def load_state(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_message(channel: str, posts: list[Post]) -> str:
    lines = [f"{channel} 有 {len(posts)} 条新帖："]
    for i, post in enumerate(posts, 1):
        text = post.text or "[媒体帖 / 无正文]"
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) > 160:
            text = text[:157] + "..."
        lines.extend([
            f"{i}. #{post.id}  {post.time_label or post.datetime or ''}".rstrip(),
            f"   {text}",
            f"   {post.url}",
        ])
    return "\n".join(lines).strip()


def leading_bracket_content(text: str) -> Optional[str]:
    pairs = {
        "[": "]",
        "【": "】",
        "「": "」",
    }
    s = (text or "").lstrip()
    if not s:
        return None
    closer = pairs.get(s[0])
    if not closer:
        return None
    idx = s.find(closer, 1)
    if idx == -1:
        return None
    return s[1:idx]


def filter_posts(posts: list[Post], prefixes: list[str], bracket_contains: list[str]) -> list[Post]:
    cleaned = [p.strip() for p in prefixes if p and p.strip()]
    needles = [n.strip().lower() for n in bracket_contains if n and n.strip()]
    if not cleaned and not needles:
        return posts
    matched: list[Post] = []
    for post in posts:
        text = (post.text or "").lstrip()
        prefix_hit = any(text.startswith(prefix) for prefix in cleaned)
        content = leading_bracket_content(text)
        bracket_hit = bool(content) and any(needle in content.lower() for needle in needles)
        if prefix_hit or bracket_hit:
            matched.append(post)
    return matched


def collect_new_posts(url: str, last_seen_id: int, proxy: Optional[str], max_pages: int) -> tuple[list[Post], int]:
    all_new: dict[int, Post] = {}
    before: Optional[int] = None
    latest_seen_on_site = last_seen_id
    pages = 0
    while pages < max_pages:
        pages += 1
        posts = fetch_page(url, before, proxy)
        if not posts:
            break
        latest_seen_on_site = max(latest_seen_on_site, posts[-1].id)
        for post in posts:
            if post.id > last_seen_id:
                all_new[post.id] = post
        oldest_id = posts[0].id
        if oldest_id <= last_seen_id:
            break
        next_before = oldest_id
        if before is not None and next_before >= before:
            break
        before = next_before
    ordered = [all_new[k] for k in sorted(all_new.keys())]
    return ordered, latest_seen_on_site


def main() -> int:
    ap = argparse.ArgumentParser(description="Monitor a public Telegram channel page via https://t.me/s/...")
    ap.add_argument("channel")
    ap.add_argument("--state-file", required=True)
    ap.add_argument("--proxy", default="")
    ap.add_argument("--max-pages", type=int, default=8)
    ap.add_argument("--prefix", action="append", default=[], help="Only notify posts whose text starts with this prefix")
    ap.add_argument("--leading-bracket-contains", action="append", default=[], help="Only notify posts whose leading bracketed tag contains this string")
    ap.add_argument("--init", action="store_true")
    args = ap.parse_args()

    url = normalize_channel_url(args.channel)
    state_path = Path(args.state_file)
    state = load_state(state_path)
    last_seen_id = int(state.get("last_seen_id") or 0)

    posts = fetch_page(url, None, args.proxy or None)
    latest_id = posts[-1].id if posts else last_seen_id

    if args.init or not state_path.exists() or last_seen_id == 0:
        save_state(state_path, {
            "channel": args.channel,
            "url": url,
            "last_seen_id": latest_id,
            "initialized_at": int(time.time()),
        })
        print(json.dumps({
            "ok": True,
            "initialized": True,
            "channel": args.channel,
            "latest_id": latest_id,
            "new_count": 0,
            "message": "",
            "new_posts": [],
        }, ensure_ascii=False))
        return 0

    new_posts, latest_on_site = collect_new_posts(url, last_seen_id, args.proxy or None, args.max_pages)
    matched_posts = filter_posts(new_posts, args.prefix, args.leading_bracket_contains)
    if latest_on_site > last_seen_id:
        save_state(state_path, {
            "channel": args.channel,
            "url": url,
            "last_seen_id": latest_on_site,
            "updated_at": int(time.time()),
        })

    message = build_message(args.channel, matched_posts) if matched_posts else ""
    print(json.dumps({
        "ok": True,
        "initialized": False,
        "channel": args.channel,
        "latest_id": latest_on_site,
        "new_count": len(matched_posts),
        "seen_count": len(new_posts),
        "message": message,
        "new_posts": [post.__dict__ for post in matched_posts],
        "seen_posts": [post.__dict__ for post in new_posts],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
