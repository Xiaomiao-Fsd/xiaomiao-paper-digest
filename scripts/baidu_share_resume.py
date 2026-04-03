#!/usr/bin/env python3
import argparse
import json
import os
import pathlib
import re
import sqlite3
import sys
import time
import urllib.parse

import requests

APP_ID = "250528"
DEFAULT_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122 Safari/537.36"
)


class AuthExpired(RuntimeError):
    pass


class DownloadError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Resume Baidu share downloads with auto re-auth.")
    p.add_argument("share_url")
    p.add_argument("password")
    p.add_argument("target_root")
    p.add_argument("--cookie-db", default=os.path.expanduser("~/.config/baidunetdisk/Cookies"))
    p.add_argument("--log", default="")
    p.add_argument("--refresh-interval", type=int, default=300, help="Seconds before proactively refreshing share auth")
    p.add_argument("--max-attempts", type=int, default=6)
    p.add_argument("--continue-on-failure", action="store_true", help="Log failed files and continue with remaining ones")
    return p.parse_args()


class Logger:
    def __init__(self, path: pathlib.Path | None):
        self.path = path
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text("", encoding="utf-8")

    def __call__(self, *parts: object) -> None:
        msg = " ".join(str(x) for x in parts)
        print(msg, flush=True)
        if self.path:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(msg + "\n")


class BaiduShareDownloader:
    def __init__(self, share_url: str, password: str, target_root: pathlib.Path, cookie_db: str, log: Logger,
                 refresh_interval: int = 300, max_attempts: int = 6, continue_on_failure: bool = False,
                 ua: str = DEFAULT_UA):
        self.share_url = share_url
        self.password = password
        self.target_root = target_root
        self.cookie_db = cookie_db
        self.log = log
        self.refresh_interval = refresh_interval
        self.max_attempts = max_attempts
        self.continue_on_failure = continue_on_failure
        self.ua = ua
        self.session = requests.Session()
        self.base_headers = {"User-Agent": self.ua, "Referer": self.share_url}
        self.shorturl = self._shorturl_from_share(self.share_url)
        self.shareid = ""
        self.from_uk = ""
        self.root_path = ""
        self.auth: dict[str, object] = {}

    @staticmethod
    def _shorturl_from_share(url: str) -> str:
        m = re.search(r"/s/([^/?#]+)", url)
        if not m:
            raise SystemExit(f"bad share url: {url}")
        surl = m.group(1)
        return surl[1:] if surl.startswith("1") else surl

    def load_login_cookies(self) -> None:
        con = sqlite3.connect(f"file:{self.cookie_db}?mode=ro", uri=True)
        cur = con.cursor()
        rows = cur.execute(
            "select host_key,name,value from cookies where host_key like '%baidu%' and value != ''"
        ).fetchall()
        count = 0
        for host, name, value in rows:
            dom = host if host.startswith(".") else "." + host
            try:
                self.session.cookies.set(name, value, domain=dom)
                count += 1
            except Exception:
                pass
        self.log("COOKIE_DB", self.cookie_db, "cookies", count)

    def verify_share(self) -> str:
        headers = {"User-Agent": self.ua, "Referer": "https://pan.baidu.com/"}
        r = self.session.post(
            f"https://pan.baidu.com/share/verify?surl={self.shorturl}",
            headers=headers,
            data={"pwd": self.password, "vcode": "", "vcode_str": ""},
            timeout=30,
        )
        try:
            j = r.json()
        except Exception as e:
            raise DownloadError(f"verify json parse failed: {e}; body={r.text[:300]}") from e
        self.log("VERIFY", r.status_code, json.dumps(j, ensure_ascii=False)[:300])
        if j.get("errno") != 0:
            raise DownloadError(f"verify failed: {j}")
        sekey = urllib.parse.unquote(self.session.cookies.get("BDCLND") or j.get("randsk", ""))
        if not sekey:
            raise DownloadError("missing sekey after verify")
        return sekey

    def fetch_meta(self) -> None:
        r = self.session.get(self.share_url, headers=self.base_headers, timeout=30)
        text = r.text
        shareid = re.search(r'shareid:\"?(\d+)\"?', text)
        from_uk = re.search(r'share_uk:\"?(\d+)\"?', text)
        root_path = re.search(r'\"path\":\"(/[^\"]+)\"', text)
        if not (shareid and from_uk and root_path):
            raise DownloadError("failed to parse share metadata from page")
        self.shareid = shareid.group(1)
        self.from_uk = from_uk.group(1)
        self.root_path = root_path.group(1).replace("\\/", "/")
        self.log("META", f"shareid={self.shareid}", f"from_uk={self.from_uk}", f"root={self.root_path}")

    def fetch_tpl(self) -> tuple[str, int]:
        url = (
            f"https://pan.baidu.com/share/tplconfig?surl=1{self.shorturl}"
            f"&fields=sign,timestamp&view_mode=1&channel=chunlei&web=1"
            f"&app_id={APP_ID}&bdstoken=&clienttype=0"
        )
        r = self.session.get(url, headers=self.base_headers, timeout=30)
        j = r.json()
        if j.get("errno") != 0:
            raise DownloadError(f"tplconfig failed: {j}")
        return j["data"]["sign"], int(j["data"]["timestamp"])

    def refresh_auth(self, reason: str = "manual") -> None:
        sekey = self.verify_share()
        sign, timestamp = self.fetch_tpl()
        self.auth = {
            "sekey": sekey,
            "sign": sign,
            "timestamp": timestamp,
            "refreshed_at": time.time(),
        }
        self.log("AUTH_REFRESH", reason, f"timestamp={timestamp}")

    def maybe_refresh_auth(self) -> None:
        refreshed_at = float(self.auth.get("refreshed_at", 0) or 0)
        if not self.auth or (time.time() - refreshed_at >= self.refresh_interval):
            self.refresh_auth("proactive")

    def list_dir(self, dir_path: str) -> list[dict]:
        all_items: list[dict] = []
        page_no = 1
        while True:
            params = {
                "is_from_web": "false",
                "sekey": "",
                "uk": self.from_uk,
                "shareid": self.shareid,
                "order": "name",
                "desc": "0",
                "showempty": "0",
                "view_mode": "1",
                "web": "1",
                "page": str(page_no),
                "num": "100",
                "dir": dir_path,
                "channel": "chunlei",
                "app_id": APP_ID,
                "bdstoken": "",
                "clienttype": "0",
            }
            r = self.session.get("https://pan.baidu.com/share/list", headers=self.base_headers, params=params, timeout=30)
            j = r.json()
            if j.get("errno") != 0:
                raise DownloadError(f"list_dir failed for {dir_path}: {j}")
            items = j.get("list", [])
            all_items.extend(items)
            self.log("LIST", dir_path, "page", page_no, "count", len(items))
            if len(items) < 100:
                break
            page_no += 1
        return all_items

    def enumerate_files(self) -> list[dict]:
        files: list[dict] = []
        queue = [self.root_path]
        seen: set[str] = set()
        while queue:
            current = queue.pop(0)
            if current in seen:
                continue
            seen.add(current)
            for item in self.list_dir(current):
                if item.get("isdir") == 1:
                    queue.append(item["path"])
                else:
                    files.append(item)
        files.sort(key=lambda x: x["path"])
        total = sum(int(x.get("size") or 0) for x in files)
        self.log("TOTAL_FILES", len(files), "TOTAL_SIZE", total)
        return files

    def get_dlink(self, item: dict) -> str:
        self.maybe_refresh_auth()
        api = (
            f"https://pan.baidu.com/api/sharedownload?sign={self.auth['sign']}"
            f"&timestamp={self.auth['timestamp']}&channel=chunlei&web=1"
            f"&app_id={APP_ID}&clienttype=0"
        )
        body = {
            "encrypt": "0",
            "extra": json.dumps({"sekey": self.auth["sekey"]}, ensure_ascii=False),
            "fid_list": f"[{item['fs_id']}]",
            "primaryid": self.shareid,
            "product": "share",
            "uk": self.from_uk,
            "type": "nolimit",
        }
        r = self.session.post(api, headers=self.base_headers, data=body, timeout=30)
        j = r.json()
        errno = j.get("errno")
        if errno == 0:
            if isinstance(j.get("list"), list):
                dlink = (j.get("list") or [{}])[0].get("dlink")
                if dlink:
                    return dlink
            if isinstance(j.get("dlink"), str) and j.get("dlink"):
                return j["dlink"]
            if isinstance(j.get("list"), str):
                raise DownloadError("sharedownload returned encoded list string; direct dlink unavailable")
            raise DownloadError(f"no dlink returned: {j}")
        show_msg = str(j.get("show_msg") or "")
        if errno == 112 or "验证码已过期" in show_msg:
            raise AuthExpired(str(j))
        raise DownloadError(f"sharedownload failed: {j}")

    def download_stream(self, dlink: str, out: pathlib.Path, expected_size: int, rel: str) -> int:
        tmp = out.with_suffix(out.suffix + ".part")
        existing = tmp.stat().st_size if tmp.exists() else 0
        if expected_size and existing > expected_size:
            tmp.unlink(missing_ok=True)
            existing = 0

        headers = {
            "User-Agent": "netdisk",
            "Referer": f"https://pan.baidu.com/share/init?surl={self.shorturl}",
        }
        if existing:
            headers["Range"] = f"bytes={existing}-"

        r = self.session.get(dlink, headers=headers, stream=True, timeout=(30, 120), allow_redirects=True)
        ct = (r.headers.get("content-type") or "").lower()

        if r.status_code == 416 and expected_size and existing == expected_size:
            os.replace(tmp, out)
            return expected_size

        if r.status_code not in (200, 206):
            preview = ""
            try:
                preview = r.text[:300]
            except Exception:
                pass
            raise DownloadError(f"download status={r.status_code} body={preview}")

        if "text/" in ct and "application/" not in ct and "image/" not in ct:
            preview = ""
            try:
                preview = r.text[:300]
            except Exception:
                pass
            raise DownloadError(f"unexpected content-type={ct} body={preview}")

        if existing and r.status_code == 206:
            mode = "ab"
            base_total = existing
        else:
            mode = "wb"
            base_total = 0

        tmp.parent.mkdir(parents=True, exist_ok=True)
        total = base_total
        started = time.time()
        last_log = started
        with open(tmp, mode) as f:
            for chunk in r.iter_content(1024 * 1024):
                if not chunk:
                    continue
                f.write(chunk)
                total += len(chunk)
                now = time.time()
                if now - last_log >= 30:
                    rate = (total - base_total) / max(now - started, 0.001) / 1024
                    self.log("PROGRESS", rel, f"{total}/{expected_size or '?'}", f"{rate:.1f}KiB/s")
                    last_log = now

        if expected_size and total != expected_size:
            raise DownloadError(f"size mismatch: expected={expected_size} got={total}")

        os.replace(tmp, out)
        return total

    def run(self) -> int:
        self.target_root.mkdir(parents=True, exist_ok=True)
        self.log("TARGET", self.target_root)
        self.log("SHORTURL", self.shorturl)
        self.load_login_cookies()
        self.refresh_auth("initial")
        self.fetch_meta()
        files = self.enumerate_files()

        skipped = 0
        done = 0
        failures: list[str] = []
        for idx, item in enumerate(files, 1):
            rel = item["path"].lstrip("/")
            out = self.target_root / rel
            size = int(item.get("size") or 0)
            if out.exists() and size > 0 and out.stat().st_size == size:
                skipped += 1
                self.log("SKIP", idx, "/", len(files), rel, size)
                continue

            out.parent.mkdir(parents=True, exist_ok=True)
            success = False
            last_error: Exception | None = None
            for attempt in range(1, self.max_attempts + 1):
                try:
                    self.log("START", idx, "/", len(files), rel, size, f"attempt={attempt}")
                    dlink = self.get_dlink(item)
                    got = self.download_stream(dlink, out, size, rel)
                    done += 1
                    self.log("OK", idx, "/", len(files), rel, got)
                    success = True
                    last_error = None
                    break
                except AuthExpired as e:
                    last_error = e
                    self.log("REAUTH_NEEDED", idx, rel, str(e)[:300])
                    self.refresh_auth("expired")
                    time.sleep(1)
                except Exception as e:
                    last_error = e
                    self.log("RETRY", attempt, idx, rel, repr(e))
                    if attempt % 2 == 0:
                        try:
                            self.refresh_auth(f"retry-{attempt}")
                        except Exception as refresh_error:
                            self.log("REFRESH_FAIL", repr(refresh_error))
                    time.sleep(min(2 * attempt, 12))
            if not success:
                msg = f"FAILED on {rel}: {last_error}"
                if self.continue_on_failure:
                    failures.append(msg)
                    self.log("FAILED_SKIP", msg)
                    continue
                raise SystemExit(msg)

        if failures:
            self.log("FAILURES", len(failures))
            for msg in failures:
                self.log("FAIL", msg)
        self.log("DONE", f"downloaded={done}", f"skipped={skipped}", f"failed={len(failures)}", f"target={self.target_root}")
        return 0 if not failures else 2


def main() -> int:
    args = parse_args()
    log_path = pathlib.Path(args.log) if args.log else None
    logger = Logger(log_path)
    downloader = BaiduShareDownloader(
        share_url=args.share_url,
        password=args.password,
        target_root=pathlib.Path(args.target_root),
        cookie_db=args.cookie_db,
        log=logger,
        refresh_interval=args.refresh_interval,
        max_attempts=args.max_attempts,
        continue_on_failure=args.continue_on_failure,
    )
    return downloader.run()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("INTERRUPTED", flush=True)
        raise
