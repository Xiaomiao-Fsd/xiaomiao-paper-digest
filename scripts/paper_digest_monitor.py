#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from html import escape, unescape
from pathlib import Path
from typing import Iterable
from urllib.parse import urlsplit, urlunsplit
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

WORKSPACE = Path("/home/XiaomiaoClaw/.openclaw/workspace")
DEFAULT_REPORT_DIR = WORKSPACE / "reports" / "paper_digest"
DEFAULT_HTML_FILE = DEFAULT_REPORT_DIR / "index.html"
DEFAULT_JSON_FILE = DEFAULT_REPORT_DIR / "latest.json"
DEFAULT_WEB_URL = "/paper_digest/index.html"


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
    abstract_cn: str = ""
    overview_cn: str = ""


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Build a daily paper digest for microelectronics / transistor related papers.")
    ap.add_argument("--state-file", required=True)
    ap.add_argument("--proxy", default="")
    ap.add_argument("--days-back", type=int, default=7)
    ap.add_argument("--max-items", type=int, default=8)
    ap.add_argument("--html-file", default=str(DEFAULT_HTML_FILE))
    ap.add_argument("--json-file", default=str(DEFAULT_JSON_FILE))
    ap.add_argument("--web-url", default=DEFAULT_WEB_URL)
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


def term_cn(term: str) -> str:
    mapping = {
        "Intel": "Intel",
        "TSMC": "TSMC",
        "transistor": "晶体管",
        "MOSFET": "MOSFET",
        "FET": "FET",
        "FinFET": "FinFET",
        "CFET": "CFET",
        "CMOS": "CMOS",
        "TFT": "TFT",
        "GAA": "GAA / 全环栅",
        "2D materials": "二维材料",
        "microelectronics": "微电子",
        "semiconductor": "半导体",
        "contact resistance": "接触电阻",
        "interconnect": "互连",
        "dielectric": "介电材料",
        "ferroelectric": "铁电材料",
        "GaN": "GaN",
        "SiC": "SiC",
        "high-k": "high-k 介质",
        "low-k": "low-k 介质",
        "HfO2": "HfO2",
    }
    return mapping.get(term, term)


def split_sentences(text: str) -> list[str]:
    text = normalize_space(text)
    if not text:
        return []
    return [part.strip() for part in re.split(r"(?<=[.!?;])\s+", text) if part.strip()]


def focus_terms_cn(paper: Paper) -> str:
    tags = [term_cn(tag) for tag in paper.highlights if tag not in ("Intel", "TSMC")]
    if not tags:
        return "微电子器件与材料"
    return "、".join(tags[:3])


def company_suffix_cn(paper: Paper) -> str:
    company = [tag for tag in paper.highlights if tag in ("Intel", "TSMC")]
    return f"，并与{' / '.join(company)}相关" if company else ""


def infer_action_cn(text: str) -> str:
    lowered = text.lower()
    rules = [
        (["propose", "present", "introduce", "develop"], "提出并实现一套新的方案或器件思路"),
        (["demonstrate", "show", "report", "reveal"], "展示器件/材料方案的关键结果"),
        (["investigate", "study", "explore", "analyze"], "系统研究其机理、结构或性能变化"),
        (["fabricate", "process", "deposition", "epitaxy"], "完成制备流程并结合实验进行验证"),
        (["integrate", "integration", "coupling", "compatible"], "强调与现有工艺或系统的集成兼容性"),
    ]
    for needles, text_cn in rules:
        if any(needle in lowered for needle in needles):
            return text_cn
    return "围绕目标器件与材料给出实验、分析与性能说明"


def infer_result_cn(text: str) -> str:
    lowered = text.lower()
    hints = []
    rules = [
        (["performance", "high performance", "enhance", "improve"], "性能提升"),
        (["efficiency", "coupling", "light-emitting", "emission"], "效率/耦合表现"),
        (["reliability", "stable", "stability", "robust"], "可靠性与稳定性"),
        (["scaling", "scaled", "sub-", "nanosheet", "gate-all-around"], "先进尺度下的可扩展性"),
        (["low power", "power consumption", "energy"], "功耗或能效表现"),
        (["contact resistance", "interconnect", "resistance"], "接触/互连相关指标"),
        (["integration", "compatible", "silicon", "cmos"], "与既有工艺平台的集成价值"),
    ]
    for needles, label in rules:
        if any(needle in lowered for needle in needles):
            hints.append(label)
    if not hints:
        return "器件性能、实验结果和潜在应用价值"
    uniq = list(dict.fromkeys(hints))
    return "、".join(uniq[:3])


def infer_body_flow_cn(text: str) -> str:
    lowered = text.lower()
    steps = []
    if any(word in lowered for word in ["structure", "architecture", "device", "stack"]):
        steps.append("器件结构与设计思路")
    if any(word in lowered for word in ["fabricate", "process", "deposition", "etch", "epitaxy", "wafer"]):
        steps.append("制备流程与工艺条件")
    if any(word in lowered for word in ["measure", "measurement", "characterization", "electrical", "optical"]):
        steps.append("电学/光学表征与测试结果")
    if any(word in lowered for word in ["simulation", "model", "mechanism", "physics"]):
        steps.append("机理分析或模型解释")
    if not steps:
        return "背景问题、方案设计、结果验证和应用讨论"
    uniq = list(dict.fromkeys(steps))
    return "、".join(uniq[:4])


def build_abstract_cn(paper: Paper) -> str:
    text = strip_html(paper.summary)
    focus = focus_terms_cn(paper)
    company_text = company_suffix_cn(paper)
    action = infer_action_cn(f"{paper.title} {text}")
    result = infer_result_cn(f"{paper.title} {text}")
    if not text:
        return f"该来源没有给出英文摘要；从标题看，论文主要围绕{focus}{company_text}展开，重点可能落在{result}。"
    return f"这段摘要主要在说：作者{action}，研究对象是{focus}{company_text}；摘要里最值得先关注的是{result}。"


def build_overview_cn(paper: Paper) -> str:
    focus = focus_terms_cn(paper)
    company_text = company_suffix_cn(paper)
    text = strip_html(paper.summary)
    flow = infer_body_flow_cn(f"{paper.title} {text}")
    result = infer_result_cn(f"{paper.title} {text}")
    if not text:
        return f"从标题推测，正文大概率会先交代{focus}{company_text}相关背景，再展开{flow}，最后落到{result}与应用意义。"
    return f"如果按正文展开来看，这篇文章大概率会先说明{focus}{company_text}的研究背景与问题设置，再依次介绍{flow}，最后用{result}来支撑其结论与应用价值。"


def sibling_url(base_url: str, filename: str) -> str:
    parts = urlsplit(base_url)
    path = parts.path or "/"
    if path.endswith("/"):
        new_path = path + filename
    else:
        idx = path.rfind("/")
        new_path = (path[: idx + 1] if idx >= 0 else "/") + filename
    return urlunsplit((parts.scheme, parts.netloc, new_path, parts.query, parts.fragment))


def render_error_html(errors: list[str]) -> str:
    if not errors:
        return ""
    return '<div class="note warning">本次抓取异常：' + escape("、".join(errors)) + "</div>"


def render_desktop_html(items: list[Paper], errors: list[str], run_dt: datetime, mobile_url: str) -> str:
    date_label = run_dt.astimezone(CN_TZ).strftime("%Y-%m-%d %H:%M")
    rows = []
    for idx, item in enumerate(items, 1):
        authors = escape(", ".join(item.authors)) if item.authors else "—"
        keywords = item.highlights or []
        keyword_html = " ".join(f'<span class="kw">{escape(tag)}</span>' for tag in keywords) if keywords else "—"
        abstract = escape(item.summary or "（该来源未提供 abstract / summary）")
        abstract_cn = escape(item.abstract_cn or "—")
        overview = escape(item.overview_cn or "—")
        title = escape(item.title)
        link = escape(item.url)
        rows.append(
            f"""
            <tr>
              <td>{idx}</td>
              <td>{escape(item.source)}</td>
              <td>{escape(item.published)}</td>
              <td><a href=\"{link}\" target=\"_blank\" rel=\"noopener noreferrer\">{title}</a></td>
              <td>{authors}</td>
              <td>{keyword_html}</td>
              <td class=\"abstract\">{abstract}</td>
              <td class=\"abstract-cn\">{abstract_cn}</td>
              <td class=\"overview\">{overview}</td>
            </tr>
            """.strip()
        )

    if not rows:
        rows.append('<tr><td colspan="9">今天暂时没有命中的新论文。</td></tr>')

    return f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>微电子论文晨报｜PC版</title>
  <style>
    :root {{ color-scheme: dark; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 24px; background: #0b1020; color: #eaf0ff; }}
    h1 {{ margin: 0 0 8px; font-size: 28px; }}
    .sub {{ color: #a9b6d3; margin-bottom: 18px; }}
    .topbar {{ display: flex; justify-content: space-between; gap: 16px; align-items: center; margin-bottom: 18px; flex-wrap: wrap; }}
    .nav a {{ color: #dce6ff; text-decoration: none; background: #1e2a50; padding: 8px 12px; border-radius: 999px; margin-left: 8px; }}
    .note {{ padding: 12px 14px; border-radius: 10px; margin: 12px 0 20px; background: #18203a; }}
    .warning {{ background: #3a2318; color: #ffd4b5; }}
    .meta {{ display: flex; gap: 18px; flex-wrap: wrap; margin: 14px 0 18px; color: #b6c2de; }}
    .badge {{ display: inline-block; padding: 3px 8px; border-radius: 999px; background: #22305a; color: #dce6ff; font-size: 12px; margin-right: 6px; }}
    .table-wrap {{ overflow-x: auto; border-radius: 14px; box-shadow: 0 0 0 1px #243054 inset; }}
    table {{ width: 100%; min-width: 1900px; border-collapse: collapse; background: #121933; }}
    th, td {{ border: 1px solid #243054; padding: 12px; vertical-align: top; text-align: left; }}
    th {{ background: #18203a; position: sticky; top: 0; z-index: 1; }}
    tr:nth-child(even) td {{ background: #0f1730; }}
    a {{ color: #8bc4ff; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .abstract {{ min-width: 360px; white-space: pre-wrap; line-height: 1.55; }}
    .abstract-cn, .overview {{ min-width: 300px; white-space: pre-wrap; line-height: 1.6; }}
    .kw {{ display: inline-block; padding: 4px 8px; border-radius: 999px; background: #22305a; margin: 0 6px 6px 0; }}
    .hint {{ color: #8fa1c9; font-size: 13px; margin-top: 10px; }}
  </style>
</head>
<body>
  <div class=\"topbar\">
    <div>
      <h1>微电子 / 集成电路论文晨报 · PC版</h1>
      <div class=\"sub\">更新时间：{escape(date_label)}（Asia/Shanghai）</div>
    </div>
    <div class=\"nav\"><a href=\"{escape(mobile_url)}\">切到手机版</a></div>
  </div>
  <div class=\"meta\">
    <div><span class=\"badge\">来源</span>arXiv / Science Advances / Nature Electronics / Nature Materials</div>
    <div><span class=\"badge\">策略</span>先宽泛覆盖微电子 / IC，再过滤数字电路 / IC 设计，最后优先晶体管与材料</div>
  </div>
  {render_error_html(errors)}
  <div class=\"table-wrap\">
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>来源</th>
          <th>日期</th>
          <th>标题 / 链接</th>
          <th>作者</th>
          <th>关键词</th>
          <th>Abstract 原文</th>
          <th>中文摘要概括</th>
          <th>正文概括（基于标题/摘要）</th>
        </tr>
      </thead>
      <tbody>
        {''.join(rows)}
      </tbody>
    </table>
  </div>
  <div class=\"hint\">说明：右侧“正文概括”目前是基于标题与摘要自动生成的阅读导向版总结；如果后面要进一步抓正文，我也可以继续补。</div>
</body>
</html>
"""


def render_mobile_html(items: list[Paper], errors: list[str], run_dt: datetime, desktop_url: str) -> str:
    date_label = run_dt.astimezone(CN_TZ).strftime("%Y-%m-%d %H:%M")
    cards = []
    for idx, item in enumerate(items, 1):
        authors = escape(", ".join(item.authors)) if item.authors else "—"
        keyword_html = " ".join(f'<span class="kw">{escape(tag)}</span>' for tag in (item.highlights or [])) or '<span class="kw muted">无高亮关键词</span>'
        cards.append(
            f"""
            <article class=\"card\">
              <div class=\"card-head\">
                <div class=\"index\">#{idx}</div>
                <div class=\"meta-line\">{escape(item.source)} · {escape(item.published)}</div>
              </div>
              <h2><a href=\"{escape(item.url)}\" target=\"_blank\" rel=\"noopener noreferrer\">{escape(item.title)}</a></h2>
              <div class=\"authors\">作者：{authors}</div>
              <div class=\"keywords\">{keyword_html}</div>
              <section>
                <h3>Abstract 原文</h3>
                <p>{escape(item.summary or '（该来源未提供 abstract / summary）')}</p>
              </section>
              <section>
                <h3>中文摘要概括</h3>
                <p>{escape(item.abstract_cn or '—')}</p>
              </section>
              <section>
                <h3>正文概括（基于标题/摘要）</h3>
                <p>{escape(item.overview_cn or '—')}</p>
              </section>
            </article>
            """.strip()
        )

    if not cards:
        cards.append('<article class="card"><p>今天暂时没有命中的新论文。</p></article>')

    return f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\" />
  <title>微电子论文晨报｜手机版</title>
  <style>
    :root {{ color-scheme: dark; }}
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0b1020; color: #eef3ff; }}
    .shell {{ padding: 16px 14px 28px; max-width: 900px; margin: 0 auto; }}
    h1 {{ font-size: 24px; margin: 0 0 6px; }}
    .sub {{ color: #a9b6d3; margin-bottom: 12px; font-size: 14px; }}
    .nav a {{ display: inline-block; color: #dce6ff; text-decoration: none; background: #1e2a50; padding: 8px 12px; border-radius: 999px; margin-bottom: 14px; }}
    .meta, .note {{ background: #121933; border: 1px solid #243054; border-radius: 14px; padding: 12px; margin-bottom: 12px; }}
    .warning {{ background: #3a2318; color: #ffd4b5; }}
    .card {{ background: #121933; border: 1px solid #243054; border-radius: 16px; padding: 14px; margin-bottom: 14px; box-shadow: 0 8px 24px rgba(0,0,0,.18); }}
    .card-head {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; color: #b7c6e6; font-size: 13px; margin-bottom: 10px; }}
    .index {{ font-weight: 700; color: #7cc2ff; }}
    h2 {{ font-size: 18px; line-height: 1.45; margin: 0 0 10px; }}
    h2 a {{ color: #eef3ff; text-decoration: none; }}
    h3 {{ margin: 14px 0 6px; font-size: 15px; color: #8bc4ff; }}
    p {{ margin: 0; white-space: pre-wrap; line-height: 1.65; color: #e4ebff; font-size: 14px; }}
    .authors {{ color: #b7c6e6; font-size: 13px; margin-bottom: 10px; }}
    .kw {{ display: inline-block; padding: 4px 8px; border-radius: 999px; background: #22305a; margin: 0 6px 6px 0; font-size: 12px; }}
    .muted {{ color: #b7c6e6; }}
    .hint {{ color: #8fa1c9; font-size: 12px; margin-top: 8px; line-height: 1.6; }}
  </style>
</head>
<body>
  <div class=\"shell\">
    <h1>微电子 / 集成电路论文晨报 · 手机版</h1>
    <div class=\"sub\">更新时间：{escape(date_label)}（Asia/Shanghai）</div>
    <div class=\"nav\"><a href=\"{escape(desktop_url)}\">切到PC版</a></div>
    <div class=\"meta\">来源：arXiv / Science Advances / Nature Electronics / Nature Materials<br>策略：先宽泛覆盖微电子 / IC，再过滤数字电路 / IC 设计，最后优先晶体管与材料</div>
    {render_error_html(errors)}
    {''.join(cards)}
    <div class=\"hint\">说明：正文概括目前是基于标题与摘要自动生成，适合手机快速扫读。</div>
  </div>
</body>
</html>
"""


def render_index_html(desktop_url: str, mobile_url: str) -> str:
    return f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>微电子论文晨报</title>
  <script>
    (function () {{
      var mobile = window.matchMedia && window.matchMedia('(max-width: 860px)').matches;
      window.location.replace(mobile ? {json.dumps(mobile_url)} : {json.dumps(desktop_url)});
    }})();
  </script>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0b1020; color: #eef3ff; display: grid; place-items: center; min-height: 100vh; margin: 0; }}
    .box {{ background: #121933; border: 1px solid #243054; border-radius: 18px; padding: 24px; width: min(92vw, 520px); }}
    a {{ color: #8bc4ff; }}
  </style>
</head>
<body>
  <div class=\"box\">
    <h1>微电子论文晨报</h1>
    <p>正在根据设备跳转到合适版本。</p>
    <p>如果没有自动跳转，可以手动选择：</p>
    <ul>
      <li><a href=\"{escape(desktop_url)}\">PC版</a></li>
      <li><a href=\"{escape(mobile_url)}\">手机版</a></li>
    </ul>
  </div>
</body>
</html>
"""


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
    html_path = Path(args.html_file)
    desktop_html_path = html_path.with_name("desktop.html")
    mobile_html_path = html_path.with_name("mobile.html")
    json_path = Path(args.json_file)
    desktop_url = sibling_url(args.web_url, "desktop.html")
    mobile_url = sibling_url(args.web_url, "mobile.html")
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
    for paper in selected:
        paper.abstract_cn = build_abstract_cn(paper)
        paper.overview_cn = build_overview_cn(paper)
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

    html_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "ok": True,
        "new_count": len(unseen),
        "selected_count": len(selected),
        "message": message,
        "papers": [asdict(paper) for paper in selected],
        "errors": errors,
        "report_url": args.web_url,
        "report_url_pc": desktop_url,
        "report_url_mobile": mobile_url,
        "generated_at": run_dt.isoformat(),
    }

    html_path.write_text(render_index_html(desktop_url, mobile_url), encoding="utf-8")
    desktop_html_path.write_text(render_desktop_html(selected, errors, run_dt, mobile_url), encoding="utf-8")
    mobile_html_path.write_text(render_mobile_html(selected, errors, run_dt, desktop_url), encoding="utf-8")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
