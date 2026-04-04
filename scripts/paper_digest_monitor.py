#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from html import unescape
from pathlib import Path
from typing import Iterable
from zoneinfo import ZoneInfo
import xml.etree.ElementTree as ET

import requests

UTC = timezone.utc
CN_TZ = ZoneInfo("Asia/Shanghai")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123 Safari/537.36"

ARXIV_QUERY = "((all:\"integrated circuit\" OR all:microelectronic OR all:microelectronics OR all:semiconductor OR all:\"semiconductor device\" OR all:wafer OR all:interconnect OR all:dielectric OR all:ferroelectric OR all:epitaxy OR all:transistor OR all:mosfet OR all:finfet OR all:cfet OR all:cmos OR all:\"gate-all-around\" OR all:nanosheet OR all:Intel OR all:TSMC) AND (cat:physics.app-ph OR cat:cond-mat.mtrl-sci OR cat:cond-mat.mes-hall OR cat:eess.EE OR cat:cond-mat.other))"
SCI_ADV_ISSN = "2375-2548"
NATURE_FEEDS = {
    "Nature Electronics": "http://feeds.nature.com/natelectron/rss/current",
    "Nature Materials": "http://feeds.nature.com/nmat/rss/current",
}

COMPANY_TERMS = {
    "Intel": ["intel", "intel corporation"],
    "TSMC": ["tsmc", "taiwan semiconductor", "taiwan semiconductor manufacturing"],
}
DEVICE_TERMS = [
    "transistor",
    "transistors",
    "mosfet",
    "mosfets",
    "fet",
    "finfet",
    "finfets",
    "cfet",
    "cfets",
    "cmos",
    "tft",
    "nanosheet",
    "nanosheets",
    "gate-all-around",
    "gate all around",
    "gaa",
    "logic device",
    "tunnel transistor",
]
MATERIAL_TERMS = [
    "microelectronic",
    "microelectronics",
    "semiconductor",
    "semiconductors",
    "dielectric",
    "dielectrics",
    "ferroelectric",
    "oxide semiconductor",
    "2d material",
    "2d materials",
    "interconnect",
    "interconnects",
    "contact resistance",
    "wafer",
    "epitaxy",
    "deposition",
    "etch",
    "lithography",
    "gallium oxide",
    "gan",
    "sic",
    "hfo2",
    "high-k",
    "low-k",
]
BROAD_TERMS = [
    "integrated circuit",
    "integrated circuits",
    "microelectronic",
    "microelectronics",
    "semiconductor",
    "semiconductors",
    "semiconductor device",
    "chip",
    "chips",
    "wafer",
    "interconnect",
    "interconnects",
    "dielectric",
    "dielectrics",
    "ferroelectric",
    "epitaxy",
    "transistor",
    "transistors",
    "mosfet",
    "mosfets",
    "finfet",
    "finfets",
    "cfet",
    "cfets",
    "cmos",
    "nanosheet",
    "nanosheets",
    "gate-all-around",
    "2d material",
    "2d materials",
    "gan",
    "sic",
]
EXCLUDE_TERMS = [
    "digital circuit",
    "digital circuits",
    "digital integrated circuit",
    "digital integrated circuits",
    "integrated circuit design",
    "ic design",
    "vlsi",
    "ulsi",
    "asic",
    "fpga",
    "logic synthesis",
    "rtl",
    "register-transfer",
    "standard cell",
    "place and route",
    "physical design",
    "eda tool",
    "electronic design automation",
    "microarchitecture",
    "processor architecture",
    "cpu architecture",
]
SOURCE_BONUS = {
    "arXiv": 0,
    "Science Advances": 2,
    "Nature Electronics": 3,
    "Nature Materials": 2,
}


@dataclass
class Paper:
    source: str
    uid: str
    title: str
    url: str
    published: str
    authors: list[str] = field(default_factory=list)
    summary: str = ""
    score: int = 0
    priority: int = 0
    highlights: list[str] = field(default_factory=list)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Build a daily paper digest for microelectronics / transistor related papers.")
    ap.add_argument("--state-file", required=True)
    ap.add_argument("--proxy", default="")
    ap.add_argument("--days-back", type=int, default=7)
    ap.add_argument("--max-items", type=int, default=8)
    return ap.parse_args()


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return normalize_space(unescape(text))


def short(text: str, limit: int = 108) -> str:
    text = normalize_space(text)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def parse_dt(text: str | None) -> datetime | None:
    if not text:
        return None
    text = text.strip()
    candidates = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d",
    ]
    for fmt in candidates:
        try:
            dt = datetime.strptime(text, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=UTC)
            return dt.astimezone(UTC)
        except ValueError:
            continue
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt.astimezone(UTC)
    except ValueError:
        return None


def extract_crossref_date(item: dict) -> datetime | None:
    for key in ("published-print", "published-online", "published", "issued", "created", "indexed"):
        value = item.get(key) or {}
        if isinstance(value, dict) and value.get("date-time"):
            return parse_dt(value["date-time"])
        parts = value.get("date-parts") if isinstance(value, dict) else None
        if parts and parts[0]:
            raw = parts[0]
            y = raw[0]
            m = raw[1] if len(raw) > 1 else 1
            d = raw[2] if len(raw) > 2 else 1
            return datetime(y, m, d, tzinfo=UTC)
    return None


def localname(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def child_text(elem: ET.Element, name: str) -> str:
    for child in list(elem):
        if localname(child.tag) == name:
            return child.text or ""
    return ""


def get_with_retries(session: requests.Session, url: str, proxy: str = "", **kwargs) -> requests.Response:
    last_error: Exception | None = None
    modes = [None]
    if proxy:
        modes.append({"http": proxy, "https": proxy})
    for proxies in modes:
        for attempt in range(3):
            try:
                req_kwargs = dict(kwargs)
                if proxies:
                    req_kwargs["proxies"] = proxies
                resp = session.get(url, **req_kwargs)
                resp.raise_for_status()
                return resp
            except Exception as exc:  # pragma: no cover - best effort retry path
                last_error = exc
                time.sleep(1 + attempt)
    assert last_error is not None
    raise last_error


def load_state(path: Path) -> dict:
    if not path.exists():
        return {"seen_ids": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {"seen_ids": {}}
        data.setdefault("seen_ids", {})
        return data
    except Exception:
        return {"seen_ids": {}}


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_session(proxy: str) -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": UA})
    s.trust_env = False
    return s


def fetch_arxiv(session: requests.Session, cutoff: datetime, proxy: str) -> list[Paper]:
    params = {
        "search_query": ARXIV_QUERY,
        "start": 0,
        "max_results": 80,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    last_error: Exception | None = None
    resp = None
    for url in ("https://export.arxiv.org/api/query", "http://export.arxiv.org/api/query"):
        try:
            resp = get_with_retries(session, url, proxy=proxy, params=params, timeout=30)
            break
        except Exception as exc:
            last_error = exc
    if resp is None:
        assert last_error is not None
        raise last_error
    root = ET.fromstring(resp.text)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    papers: list[Paper] = []
    for entry in root.findall("a:entry", ns):
        published = parse_dt(entry.findtext("a:published", default="", namespaces=ns))
        if not published or published < cutoff:
            continue
        entry_id = entry.findtext("a:id", default="", namespaces=ns).strip()
        arxiv_id = entry_id.rstrip("/").split("/")[-1]
        authors = [a.findtext("a:name", default="", namespaces=ns).strip() for a in entry.findall("a:author", ns)]
        papers.append(
            Paper(
                source="arXiv",
                uid=f"arxiv:{arxiv_id}",
                title=normalize_space(entry.findtext("a:title", default="", namespaces=ns)),
                url=entry_id.replace("http://", "https://"),
                published=published.astimezone(CN_TZ).strftime("%Y-%m-%d"),
                authors=[a for a in authors if a],
                summary=normalize_space(entry.findtext("a:summary", default="", namespaces=ns)),
            )
        )
    return papers


def fetch_science_advances(session: requests.Session, cutoff: datetime, proxy: str) -> list[Paper]:
    url = f"https://api.crossref.org/journals/{SCI_ADV_ISSN}/works"
    params = {
        "filter": f"from-pub-date:{cutoff.date().isoformat()}",
        "sort": "published",
        "order": "desc",
        "rows": 40,
    }
    resp = get_with_retries(session, url, proxy=proxy, params=params, timeout=30)
    items = resp.json().get("message", {}).get("items", [])
    papers: list[Paper] = []
    for item in items:
        if item.get("type") not in (None, "journal-article"):
            continue
        published = extract_crossref_date(item)
        if not published or published < cutoff:
            continue
        title = normalize_space((item.get("title") or [""])[0])
        doi = item.get("DOI")
        authors = []
        for author in item.get("author", []) or []:
            name = " ".join(part for part in [author.get("given", ""), author.get("family", "")] if part).strip()
            if name:
                authors.append(name)
        papers.append(
            Paper(
                source="Science Advances",
                uid=f"doi:{doi}" if doi else f"scienceadv:{title}",
                title=title,
                url=item.get("URL") or (f"https://doi.org/{doi}" if doi else "https://www.science.org/journal/sciadv"),
                published=published.astimezone(CN_TZ).strftime("%Y-%m-%d"),
                authors=authors,
                summary=strip_html(item.get("abstract", "")),
            )
        )
    return papers


def fetch_nature_feed(session: requests.Session, source: str, url: str, cutoff: datetime, proxy: str) -> list[Paper]:
    resp = get_with_retries(session, url, proxy=proxy, timeout=30)
    root = ET.fromstring(resp.text)
    papers: list[Paper] = []
    for elem in root.iter():
        if localname(elem.tag) != "item":
            continue
        published = parse_dt(child_text(elem, "date"))
        if not published:
            source_line = child_text(elem, "source")
            m = re.search(r"(\d{4}-\d{2}-\d{2})", source_line)
            if m:
                published = parse_dt(m.group(1))
        if not published or published < cutoff:
            continue
        doi = child_text(elem, "doi") or child_text(elem, "identifier")
        title = normalize_space(child_text(elem, "title"))
        summary = strip_html(child_text(elem, "encoded") or child_text(elem, "description"))
        link = child_text(elem, "url") or child_text(elem, "link")
        if doi.startswith("doi:"):
            doi = doi[4:]
        uid = f"{source}:{doi or link or title}"
        papers.append(
            Paper(
                source=source,
                uid=uid,
                title=title,
                url=link,
                published=published.astimezone(CN_TZ).strftime("%Y-%m-%d"),
                authors=[],
                summary=summary,
            )
        )
    return papers


def unique_terms(text: str, terms: Iterable[str]) -> list[str]:
    found = []
    for term in terms:
        pattern = re.escape(term).replace(r"\ ", r"\s+")
        if re.search(rf"(?<![A-Za-z0-9]){pattern}(?![A-Za-z0-9])", text, flags=re.IGNORECASE):
            if term not in found:
                found.append(term)
    return found


def pretty_term(term: str) -> str:
    mapping = {
        "gate-all-around": "GAA",
        "gate all around": "GAA",
        "gaa": "GAA",
        "mosfet": "MOSFET",
        "mosfets": "MOSFET",
        "fet": "FET",
        "finfet": "FinFET",
        "finfets": "FinFET",
        "cfet": "CFET",
        "cfets": "CFET",
        "cmos": "CMOS",
        "tft": "TFT",
        "transistor": "transistor",
        "transistors": "transistor",
        "2d material": "2D materials",
        "2d materials": "2D materials",
        "hfo2": "HfO2",
        "gan": "GaN",
        "sic": "SiC",
        "high-k": "high-k",
        "low-k": "low-k",
        "microelectronic": "microelectronics",
        "microelectronics": "microelectronics",
        "semiconductor": "semiconductor",
        "semiconductors": "semiconductor",
        "contact resistance": "contact resistance",
        "interconnect": "interconnect",
        "interconnects": "interconnect",
        "dielectric": "dielectric",
        "dielectrics": "dielectric",
        "ferroelectric": "ferroelectric",
    }
    return mapping.get(term.lower(), term)


def score_paper(paper: Paper) -> Paper | None:
    title_text = paper.title
    body_text = f"{paper.summary} {' '.join(paper.authors)}"
    score = SOURCE_BONUS.get(paper.source, 0)
    priority = 0
    highlights: list[str] = []

    company_hits = []
    for label, terms in COMPANY_TERMS.items():
        if unique_terms(title_text, terms) or unique_terms(body_text, terms):
            company_hits.append(label)
            score += 8
            priority += 2
    highlights.extend(company_hits)

    broad_title_hits = unique_terms(title_text, BROAD_TERMS)
    broad_body_hits = [t for t in unique_terms(body_text, BROAD_TERMS) if t not in broad_title_hits]
    negative_title_hits = unique_terms(title_text, EXCLUDE_TERMS)
    negative_body_hits = [t for t in unique_terms(body_text, EXCLUDE_TERMS) if t not in negative_title_hits]

    device_title_hits = unique_terms(title_text, DEVICE_TERMS)
    device_body_hits = [t for t in unique_terms(body_text, DEVICE_TERMS) if t not in device_title_hits]
    material_title_hits = unique_terms(title_text, MATERIAL_TERMS)
    material_body_hits = [t for t in unique_terms(body_text, MATERIAL_TERMS) if t not in material_title_hits]

    score += min(3, len(broad_title_hits)) * 1
    score += min(2, len(broad_body_hits)) * 1
    score += min(4, len(device_title_hits)) * 4
    score += min(3, len(device_body_hits)) * 2
    score += min(4, len(material_title_hits)) * 2
    score += min(3, len(material_body_hits)) * 1

    if device_title_hits:
        priority += 1
    if material_title_hits and (device_title_hits or company_hits):
        priority += 1

    for term in device_title_hits[:3] + material_title_hits[:2]:
        pretty = pretty_term(term)
        if pretty not in highlights:
            highlights.append(pretty)

    has_broad = bool(broad_title_hits or broad_body_hits)
    has_device = bool(device_title_hits or device_body_hits)
    has_material = bool(material_title_hits or material_body_hits)
    has_company = bool(company_hits)

    if not has_company and not has_broad:
        return None

    # 用户希望范围先放宽到微电子 / IC，但过滤掉偏数字电路 / IC 设计方向的内容。
    if negative_title_hits and not (has_company or device_title_hits or material_title_hits):
        return None
    if len(negative_body_hits) >= 2 and not (has_company or device_title_hits or material_title_hits):
        return None

    if not has_company and not has_device and not has_material:
        return None
    if not has_company and not has_device and len(material_title_hits) + len(material_body_hits) < 2:
        return None
    if score < 4:
        return None

    paper.score = score
    paper.priority = priority
    paper.highlights = highlights[:4]
    return paper


def rank_and_filter(papers: list[Paper]) -> list[Paper]:
    out = []
    for paper in papers:
        scored = score_paper(paper)
        if scored is not None:
            out.append(scored)
    out.sort(key=lambda p: (p.priority, p.score, p.published, p.source), reverse=True)
    return out


def build_message(items: list[Paper], errors: list[str], run_dt: datetime) -> str:
    header = f"论文晨报｜微电子材料 / 晶体管（{run_dt.astimezone(CN_TZ).strftime('%Y-%m-%d')}）"
    checked = "来源：arXiv / Science Advances / Nature Electronics / Nature Materials"
    if not items:
        lines = [header, checked, "今天暂时没刷到新的高相关论文。"]
        if errors:
            lines.append("抓取异常：" + "、".join(errors))
        return "\n".join(lines)

    focus_count = sum(1 for item in items if any(tag in ("Intel", "TSMC") for tag in item.highlights))
    lines = [header, checked, f"命中 {len(items)} 篇；Intel/TSMC 重点 {focus_count} 篇"]
    for idx, item in enumerate(items, 1):
        star = "⭐ " if any(tag in ("Intel", "TSMC") for tag in item.highlights) else ""
        lines.append(f"{idx}. {star}[{item.source}] {short(item.title, 92)}")
        if item.highlights:
            lines.append(f"   关键词：{', '.join(item.highlights)}")
        lines.append(f"   日期：{item.published}")
        if item.authors:
            author_text = ", ".join(item.authors[:3])
            if len(item.authors) > 3:
                author_text += " 等"
            lines.append(f"   作者：{author_text}")
        lines.append(f"   {item.url}")
    if errors:
        lines.append("注：以下源本次抓取失败：" + "、".join(errors))
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    state_path = Path(args.state_file)
    state = load_state(state_path)
    seen_ids: dict[str, int] = {k: int(v) for k, v in state.get("seen_ids", {}).items() if isinstance(v, (int, float, str))}
    now_ts = int(time.time())
    seen_ids = {k: v for k, v in seen_ids.items() if now_ts - int(v) < 90 * 86400}

    cutoff = datetime.now(UTC) - timedelta(days=args.days_back)
    session = build_session(args.proxy)

    all_papers: list[Paper] = []
    errors: list[str] = []

    try:
        all_papers.extend(fetch_arxiv(session, cutoff, args.proxy))
    except Exception:
        errors.append("arXiv")
    try:
        all_papers.extend(fetch_science_advances(session, cutoff, args.proxy))
    except Exception:
        errors.append("Science Advances")
    for source, url in NATURE_FEEDS.items():
        try:
            all_papers.extend(fetch_nature_feed(session, source, url, cutoff, args.proxy))
        except Exception:
            errors.append(source)

    ranked = rank_and_filter(all_papers)
    unseen = [paper for paper in ranked if paper.uid not in seen_ids]
    selected = unseen[: args.max_items]

    run_dt = datetime.now(UTC)
    message = build_message(selected, errors, run_dt)

    for paper in unseen:
        seen_ids[paper.uid] = now_ts

    save_state(
        state_path,
        {
            "seen_ids": seen_ids,
            "last_run_at": run_dt.isoformat(),
            "last_selected_ids": [paper.uid for paper in selected],
        },
    )

    print(
        json.dumps(
            {
                "ok": True,
                "new_count": len(unseen),
                "selected_count": len(selected),
                "message": message,
                "papers": [asdict(paper) for paper in selected],
                "errors": errors,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
