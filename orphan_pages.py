#!/usr/bin/env python3
"""指令 2 · 孤岛页面检测

从首页出发抓取全站内链，构建有向图，计算每个页面的入度。
输出三份清单：入度=0（孤岛）、入度≥1 但全部来自导航/页脚（弱连接）、点击深度≥4（埋太深）。

 adapted from https://seogeo.cc/ai-built-site-seo-risks-quick-check
用法: python orphan_pages.py https://你的域名 [--out report.md]
"""
import argparse
from collections import defaultdict, deque
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from audit_common import make_session, normalize_base, normalize_url, safe_get, write_report


def nav_link_set(soup, base_host):
    """Links that live inside header/nav/footer = site-wide navigation links."""
    out = set()
    for tag in soup.find_all(["header", "nav", "footer"]):
        for a in tag.find_all("a", href=True):
            u = normalize_url(urljoin(base_url_holder[0], a["href"]))
            if urlparse(u).netloc == base_host:
                out.add(u)
    return out


base_url_holder = [""]


def main():
    ap = argparse.ArgumentParser(description="孤岛页面检测 - 入度 / 点击深度")
    ap.add_argument("domain", help="目标站点，如 https://example.com")
    ap.add_argument("--out", help="报告输出路径（.md）")
    ap.add_argument("--max-pages", type=int, default=500, help="最多抓取页数，默认 500")
    ap.add_argument("--timeout", type=int, default=12)
    args = ap.parse_args()

    base = normalize_base(args.domain)
    base_url_holder[0] = base
    host = urlparse(base).netloc
    session = make_session(args.timeout)

    print(f"[1/3] 从首页出发抓取内链（最多 {args.max_pages} 页）: {base}")
    graph = defaultdict(set)      # target -> set(sources)
    depth = {normalize_url(base): 0}
    nav_links = set()
    q = deque([base])
    visited = set()
    fetched = 0

    while q and fetched < args.max_pages:
        url = q.popleft()
        nu = normalize_url(url)
        if nu in visited:
            continue
        visited.add(nu)
        fetched += 1
        r = safe_get(session, url, args.timeout)
        if not r["text"]:
            continue
        soup = BeautifulSoup(r["text"], "html.parser")
        if fetched == 1:
            nav_links = nav_link_set(soup, host)
        d = depth.get(nu, 0)
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if not href or href.startswith(("javascript:", "mailto:", "tel:", "#")):
                continue
            target = normalize_url(urljoin(base, href))
            if urlparse(target).netloc != host:
                continue
            graph[target].add(nu)
            if target not in depth:
                depth[target] = d + 1
                if len(visited) + len(q) < args.max_pages:
                    q.append(target)

    print(f"  已抓取 {fetched} 页，发现 {len(graph)} 个有入链的页面")

    all_pages = set(visited) | set(graph.keys())
    in_deg = {p: len(graph.get(p, set())) for p in all_pages}

    islands = sorted(p for p in all_pages if in_deg[p] == 0 and p != normalize_url(base))
    weak = []
    for p in all_pages:
        srcs = graph.get(p, set())
        if not srcs or p in islands or p == normalize_url(base):
            continue
        if srcs.issubset(nav_links):
            weak.append(p)
    weak.sort()
    deep = sorted(p for p in all_pages if depth.get(p, 0) >= 4)

    lines = [
        "# 孤岛页面检测报告",
        "",
        f"目标站点：{base}",
        f"抓取页面：{fetched}",
        "",
        "## 1. 入度 = 0 的页面（孤岛，只能靠 sitemap 被发现）",
        "",
    ]
    lines += [f"- {p}" for p in islands] or ["- 无"]
    lines += [
        "",
        "## 2. 入度 ≥ 1 但全部来自导航/页脚的页面（弱连接）",
        "",
    ]
    lines += [f"- {p}" for p in weak] or ["- 无"]
    lines += [
        "",
        "## 3. 点击深度 ≥ 4 的页面（埋太深，不利于收录）",
        "",
    ]
    lines += [f"- {p}（深度 {depth.get(p)}）" for p in deep] or ["- 无"]
    lines += [
        "",
        "## 修复建议",
        "",
        "- 孤岛页：从相关分类页/正文/页脚加真实 `<a href>` 链接指过去，不要只留在 sitemap 里。",
        "- 弱连接页：补正文内链，避免只靠导航/页脚被发现。",
        "- 埋太深页：用聚合页（产品分类页、文章分类页）放进导航/页脚/侧边栏，让首页点击到任意页面不超过 3 次。",
        "",
        "参考原文：https://seogeo.cc/ai-built-site-seo-risks-quick-check",
    ]
    write_report(args.out, lines)


if __name__ == "__main__":
    main()
