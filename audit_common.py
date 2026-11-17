"""Shared helpers for the AI-built-site SEO/GEO check scripts.

Source logic: https://seogeo.cc/ai-built-site-seo-risks-quick-check
"""
import gzip
import re
import sys
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse

import requests

UA = (
    "Mozilla/5.0 (compatible; AI-Built-Site-SEO-Check/1.0; "
    "+https://seogeo.cc/ai-built-site-seo-risks-quick-check)"
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def normalize_base(raw):
    raw = (raw or "").strip()
    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw
    p = urlparse(raw)
    if not p.netloc:
        raise ValueError(f"Invalid domain: {raw}")
    return f"{p.scheme}://{p.netloc}"


def make_session(timeout=12):
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*"})
    return s


def safe_get(session, url, timeout=12):
    """Return dict with status, final url, redirect target, text, headers, error."""
    try:
        r = session.get(url, timeout=timeout, allow_redirects=True)
        return {
            "status": r.status_code,
            "url": r.url,
            "redirect": r.url if r.history else "",
            "history": [h.status_code for h in r.history],
            "text": r.text,
            "headers": dict(r.headers),
            "error": "",
        }
    except Exception as exc:
        return {
            "status": 0,
            "url": url,
            "redirect": "",
            "history": [],
            "text": "",
            "headers": {},
            "error": str(exc)[:160],
        }


def normalize_url(url):
    url = url.split("#", 1)[0]
    p = urlparse(url)
    path = p.path.rstrip("/") or "/"
    return f"{p.scheme}://{p.netloc}{path}" + (f"?{p.query}" if p.query else "")


def _decode_xml(content, url):
    if url.endswith(".gz") or content[:2] == b"\x1f\x8b":
        try:
            content = gzip.decompress(content)
        except Exception:
            pass
    return content.decode("utf-8", "ignore")


def _locs(root):
    out = []
    for el in root.iter():
        if el.tag.lower().endswith("loc") and el.text and el.text.strip().startswith("http"):
            out.append(el.text.strip())
    return out


def get_sitemap_urls(base, session, timeout=12):
    """Collect URLs from /robots.txt Sitemap lines and common sitemap paths."""
    candidates = ["/sitemap.xml", "/sitemap-index.xml", "/sitemap_index.xml", "/sitemap.xml.gz"]
    try:
        r = session.get(urljoin(base, "/robots.txt"), timeout=timeout)
        if r.status_code == 200:
            for line in r.text.splitlines():
                line = line.strip()
                if line.lower().startswith("sitemap:"):
                    su = line.split(":", 1)[1].strip()
                    if su:
                        candidates.insert(0, su)
    except Exception:
        pass

    docs = []
    seen_doc = set()
    for c in candidates:
        u = urljoin(base, c)
        if u in seen_doc:
            continue
        seen_doc.add(u)
        try:
            r = session.get(u, timeout=timeout)
            if r.status_code == 200 and "<" in r.text[:4000]:
                docs.append((u, r.content))
        except Exception:
            pass

    urls = []
    for u, content in docs:
        try:
            root = ET.fromstring(_decode_xml(content, u))
        except Exception:
            continue
        if "sitemapindex" in root.tag.lower():
            for child in _locs(root):
                try:
                    rr = session.get(child, timeout=timeout)
                    if rr.status_code == 200:
                        urls.extend(_locs(ET.fromstring(_decode_xml(rr.content, child))))
                except Exception:
                    pass
        else:
            urls.extend(_locs(root))

    seen, out = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def extract_head(html):
    title, canonical = "", ""
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    if m:
        title = re.sub(r"\s+", " ", m.group(1)).strip()
    m = re.search(r"<link[^>]+rel=['\"]?canonical['\"]?[^>]*>", html, re.I)
    if m:
        mm = re.search(r"href=['\"]([^'\"]+)", m.group(0), re.I)
        if mm:
            canonical = mm.group(1).strip()
    return title, canonical


def write_report(out_path, lines):
    text = "\n".join(lines) + "\n"
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)
    print(text)
