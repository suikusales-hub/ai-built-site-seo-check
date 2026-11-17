# AI 建站 5 项自查清单（可打印）

> 来自 [seogeo.cc 原文](https://seogeo.cc/ai-built-site-seo-risks-quick-check)。这 5 项修起来通常不复杂，半小时能改完，难的是先知道问题在哪。

## 跑工具前的准备

- [ ] 确认目标站点的正式域名（不是 `localhost`、不是临时 `pages.dev` 预览地址）
- [ ] Python 3.8+，`pip install -r requirements.txt` 已完成

## 5 项排查

- [ ] **软 404**：不存在的网址（如 `/this-should-404-xyz123`）是否返回真正 404，而不是 200 回退首页
  - 工具：`python route_audit.py https://你的域名`
- [ ] **canonical**：每页 canonical 是否指向自身、是绝对 URL，没有全站写死指向首页
  - 工具：`python route_audit.py`（看重定向/重复 URL）
- [ ] **title 唯一**：全站 title 是否每页不同、搜索结果蓝字不撞车
  - 可用 Screaming Frog 的 Page Titles → Duplicate 复核
- [ ] **孤岛页面**：每页是否至少有 1 条内链指向；首页点击到任意页 ≤3 次
  - 工具：`python orphan_pages.py https://你的域名`
- [ ] **AI 抓取通道**：robots.txt 未屏蔽 GPTBot/ClaudeBot/PerplexityBot/Bytespider/Baiduspider；关掉 JS 后正文还在
  - 工具：`python geo_check.py https://你的域名`

## 修完复核

- [ ] 用 [Screaming Frog](https://www.screamingfrog.co.uk/seo-spider/) 全量爬一遍，404 与异常 301 已处理
- [ ] Page Titles、Meta Description 无 Missing、无 Duplicate
- [ ] 确认 robots.txt 与 sitemap 完整地址能打开并指向正确域名

---

原文：[https://seogeo.cc/ai-built-site-seo-risks-quick-check](https://seogeo.cc/ai-built-site-seo-risks-quick-check)
