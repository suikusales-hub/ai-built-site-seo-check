#!/usr/bin/env python3
"""指令 1 · 全站路由体检

从 sitemap 取全部页面，每页测 4 种变体（原样 / 尾斜杠 / .html / 全大写），
再测一个假路径，记录状态码与重定向，输出表格并回答 3 个问题。

 adapted from https://seogeo.cc/ai-built-site-seo-risks-quick-check
用法: python route_audit.py https://你的域名 [--out report.md]
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse

from audit_common import (
    extract_head, get_sitemap_urls, make_session, normalize_base,
    safe_get, write_report,
)

FAKE_PATH = "/this-should-404-xyz123"


def variants(url):
    p = urlparse(url)
    base = f"{p.scheme}://{p.netloc}"
    path = p.path or "/"
    return {
        "原样": url,
        "尾斜杠": url if path.endswith("/") else base + path + "/",
        ".html": base + (path.rstrip("/") + ".html"),
        "全大写": base + path.upper(),
    }


def check_route(session, url):
    vs = variants(url)
    result = {}
    seen = {}
    for name, u in vs.items():
        # 同一个 URL 只请求一次，避免 "/" 原样与尾斜杠重复计算 200
        if u in seen:
            result[name] = result[seen[u]]
            continue
        seen[u] = name
        result[name] = safe_get(session, u)
    return result


def main():
    ap = argparse.ArgumentParser(description="全站路由体检 - soft404 / 重复URL / 301 / 404")
    ap.add_argument("domain", help="目标站点，如 https://example.com")
    ap.add_argument("--out", help="报告输出路径（.md）")
    ap.add_argument("--workers", type=int, default=8, help="并发数，默认 8")
    ap.add_argument("--timeout", type=int, default=12, help="单请求超时秒数")
    ap.add_argument("--limit", type=int, default=0, help="最多检测页数，0=全部")
    args = ap.parse_args()

    base = normalize_base(args.domain)
    session = make_session(args.timeout)
    print(f"[1/3] 读取 sitemap: {base}")
    urls = get_sitemap_urls(base, session, args.timeout)
    if not urls:
        urls = [base + "/"]
        print("  ! 未找到 sitemap，仅检测首页")
    if args.limit:
        urls = urls[: args.limit]
    print(f"  检测到 {len(urls)} 个页面，开始请求 {len(urls)*4+1} 次...")

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        results = list(ex.map(lambda u: check_route(session, u), urls))
    fake = safe_get(session, base + FAKE_PATH)

    lines = [f"# 全站路由体检报告", "", f"目标站点：{base}", f"检测页面：{len(urls)}", ""]
    lines.append("| 路径 | 原样 | 尾斜杠 | .html | 全大写 | 多版本200 | 重定向目标 |")
    lines.append("|---|---|---|---|---|---|---|")
    multi_200 = 0
    redirect_301 = 0
    any_404 = 0
    for url, r in zip(urls, results):
        codes = {k: v["status"] for k, v in r.items()}
        # 按最终 URL 去重后再数 200，避免同一地址被算成多版本
        ok_urls = {v["url"] for v in r.values() if v["status"] == 200}
        n200 = len(ok_urls)
        if n200 > 1:
            multi_200 += 1
        for v in r.values():
            if 300 <= v["status"] < 400:
                redirect_301 += 1
            if v["status"] == 404:
                any_404 += 1
        redirects = sorted({v["redirect"] for v in r.values() if v["redirect"]})
        rd = "<br>".join(redirects[:2]) if redirects else "—"
        lines.append(
            f"| {urlparse(url).path or '/'} | {codes['原样']} | {codes['尾斜杠']} | "
            f"{codes['.html']} | {codes['全大写']} | {'⚠️ 是' if n200>1 else '否'} | {rd} |"
        )

    soft404 = fake["status"] == 200
    lines += [
        "",
        "## 结论（3 个问题）",
        "",
        f"- **有没有软 404（假路径返回 200）**：{'有 ⚠️ — ' + FAKE_PATH + ' 返回 200' if soft404 else '没有 — 假路径返回 ' + str(fake['status']) }",
        f"- **多少页面存在多版本 200（重复 URL）**：{multi_200} 个",
        f"- **301 是否存在**：{'有，共 ' + str(redirect_301) + ' 次重定向' if redirect_301 else '无'}",
        f"- **404 是否存在**：{'有，共 ' + str(any_404) + ' 次' if any_404 else '无'}",
        "",
        "> 修复建议：假路径返回 200 通常是路由回退首页（soft 404），需在服务端/构建配置里让未知路径返回真正 404；",
        "> 多版本 200 需在 canonical 与服务器层统一到唯一 URL，非首选版本做 301；",
        "> 检查每个页面 canonical 是否为绝对 URL 且指向自身，不要被模板写死。",
        "",
        "参考原文：https://seogeo.cc/ai-built-site-seo-risks-quick-check",
    ]
    write_report(args.out, lines)


if __name__ == "__main__":
    main()
