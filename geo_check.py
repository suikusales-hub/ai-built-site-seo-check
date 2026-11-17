#!/usr/bin/env python3
"""指令 3 · AI 能不能读懂你（GEO 审计）

检查 5 项，每项给"通过/不通过 + 证据"：
 1. robots.txt 是否 Disallow 了 GPTBot / ClaudeBot / PerplexityBot / Bytespider / Baiduspider
 2. 关掉 JavaScript 后正文是否还在
 3. 正文是否纯 HTML 可读（无 JS 也能拿到）
 4. 是否有结构化数据（JSON-LD）
 5. 品牌/事实是否写成明确句子（非仅图片）

 adapted from https://seogeo.cc/ai-built-site-seo-risks-quick-check
用法: python geo_check.py https://你的域名 [--out report.md]
"""
import argparse
import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from audit_common import make_session, normalize_base, safe_get, write_report

AI_BOTS = ["GPTBot", "ClaudeBot", "PerplexityBot", "Bytespider", "Baiduspider"]


def parse_robots(text):
    """Return dict bot -> list of Disallow paths (case-insensitive bot names)."""
    rules = {}
    current = None
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, val = [x.strip() for x in line.split(":", 1)]
        if key.lower() == "user-agent":
            current = val.lower()
            rules.setdefault(current, [])
        elif key.lower() == "disallow" and current:
            rules[current].append(val)
    return rules


def blocked_bots(robots_text):
    rules = parse_robots(robots_text)
    blocked = []
    for bot in AI_BOTS:
        for ua, disallows in rules.items():
            if ua == bot.lower() or ua == "*":
                if "/" in disallows or "" in disallows:
                    blocked.append((bot, "*" if ua == "*" else ua))
                    break
    return blocked


def main():
    ap = argparse.ArgumentParser(description="GEO 审计 - AI 爬虫与正文可读性")
    ap.add_argument("domain", help="目标站点，如 https://example.com")
    ap.add_argument("--out", help="报告输出路径（.md）")
    ap.add_argument("--timeout", type=int, default=12)
    args = ap.parse_args()

    base = normalize_base(args.domain)
    session = make_session(args.timeout)
    print(f"[1/5] 读取 robots.txt: {base}")

    rr = safe_get(session, urljoin(base, "/robots.txt"), args.timeout)
    robots_text = rr["text"] if rr["status"] == 200 else ""
    blocked = blocked_bots(robots_text) if robots_text else []

    print("[2/5] 检查首页正文（关 JS 后的原始 HTML）")
    home = safe_get(session, base, args.timeout)
    soup = BeautifulSoup(home["text"], "html.parser") if home["text"] else None
    for t in soup(["script", "style", "noscript"]) if soup else []:
        t.decompose()
    static_text = soup.get_text(" ", strip=True) if soup else ""
    text_len = len(static_text)

    has_jsonld = bool(soup and soup.find("script", attrs={"type": "application/ld+json"}))
    has_semantic = bool(soup and soup.find(["main", "article"]))
    h1 = bool(soup and soup.find("h1"))
    img_no_alt = 0
    if soup:
        for img in soup.find_all("img"):
            if not (img.get("alt") or "").strip():
                img_no_alt += 1

    lines = [
        "# GEO 审计报告 · AI 能不能读懂你",
        "",
        f"目标站点：{base}",
        "",
        "## 检查 5 项（通过/不通过 + 证据）",
        "",
        "### 1. robots.txt 是否屏蔽 AI 爬虫",
    ]
    if not robots_text:
        lines += ["- **不通过/存疑** — robots.txt 无法读取（HTTP " + str(rr["status"]) + "）"]
    elif blocked:
        lines += [f"- **不通过** — 以下爬虫被 `Disallow: /` 挡住：{', '.join(b for b,_ in blocked)}"]
        lines += ["- 证据（robots.txt 摘录）：", "```", "\n".join(robots_text.splitlines()[:30]), "```"]
    else:
        lines += ["- **通过** — 未发现 GPTBot / ClaudeBot / PerplexityBot / Bytespider / Baiduspider 被全站屏蔽"]

    lines += [
        "",
        "### 2. 关掉 JavaScript 后正文是否还在",
        f"- {'**通过**' if text_len >= 200 else '**不通过**'} — 原始 HTML 可见文本约 {text_len} 字符"
        + ("（<200 字符，疑似纯前端渲染的白屏站）" if text_len < 200 else ""),
    ]
    lines += [
        "",
        "### 3. 正文是否纯 HTML 可读",
        f"- {'**通过**' if has_semantic else '**不通过**'} — 语义标签 main/article：{'有' if has_semantic else '无'}",
        f"- {'**通过**' if img_no_alt == 0 else '**警告**'} — 图片缺 alt：{img_no_alt} 张",
    ]
    lines += [
        "",
        "### 4. 是否有结构化数据（JSON-LD）",
        f"- {'**通过**' if has_jsonld else '**不通过**'} — 页面{'含' if has_jsonld else '不含'} `application/ld+json`",
    ]
    lines += [
        "",
        "### 5. 标题层级与事实表达",
        f"- {'**通过**' if h1 else '**不通过**'} — H1：{'有' if h1 else '无'}",
        "- 提示：品牌名、地址、认证、产能等事实要写成明确句子，不要只放在图片里。",
    ]

    fail = sum([
        bool(blocked), text_len < 200, not has_semantic, not has_jsonld, not h1,
    ])
    lines += [
        "",
        "## AI 引用概率评估（粗判）",
        "",
        f"- 5 项中约 {fail} 项不通过/存疑。",
        "- 如果用户在豆包、DeepSeek、ChatGPT、Gemini、Grok、Perplexity 里问这个领域的问题："
        + ("被引用概率**偏低** — 先修上面不通过的项，尤其是 robots 屏蔽与关 JS 白屏。" if fail >= 2
           else "被引用概率**中等偏高** — 基础可读性与抓取通道基本正常，建议补充结构化数据与明确事实句。"),
        "- 依据：AI 爬虫多数不执行 JS、且遵循 robots.txt；抓不到正文就无法引用。",
        "",
        "参考原文：https://seogeo.cc/ai-built-site-seo-risks-quick-check",
    ]
    write_report(args.out, lines)


if __name__ == "__main__":
    main()
