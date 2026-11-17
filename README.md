# AI 建站隐患快速排查工具（SEO / GEO）

> 把「[Codex 等 AI 建站隐患多，快速排查教程](https://seogeo.cc/ai-built-site-seo-risks-quick-check)」里的 3 条排查指令，做成**真能跑的脚本**。不用装尖叫青蛙、不用看懂原理，一条命令出报告，半小时定位 AI 建站最常见的收录、结构、内容隐患。

**原文（完整方法与作者）**：[SEO小平 · seogeo.cc — Codex 等 AI 建站隐患多，快速排查教程](https://seogeo.cc/ai-built-site-seo-risks-quick-check)

**作者站点**：[seogeo.cc — 外贸 SEO / GEO 实战](https://seogeo.cc)

---

## 为什么有这个工具

AI（Codex / Claude Code / WorkBuddy / Grok / Trae / DeepSeek Harness 等）建站又快又漂亮，但打开源码用 SEO/GEO 标准看，问题很多。原文归纳了最要命的 5 个：

1. **软 404**：不存在的网址返回 200，搜索引擎以为是真的，凭空多出无数重复页。
2. **canonical 全指向首页**：模板把 canonical 写死，500 篇都被判成首页复制品。
3. **全站 title 一样**：搜索结果那行蓝字全站相同，主题被判定重复、互相抢位。
4. **孤岛页面**：sitemap 里躺着 300 个 URL，200 个从首页点不到、没有任何内链指向。
5. **对 AI 爬虫关着门**：`robots.txt` 里 `Disallow: /` 挡住 GPTBot / ClaudeBot / PerplexityBot / Bytespider / Baiduspider；或纯前端渲染，关掉 JS 就白屏。

尖叫青蛙（Screaming Frog）能查全，但很多人装不上、看不懂、跑完一屏红叉不知先修哪个。这个工具把最要命的几项做成命令，直接出结论。

---

## 安装

需要 Python 3.8+：

```bash
pip install -r requirements.txt
```

---

## 三个脚本

| 脚本 | 对应原文 | 查什么 |
|------|----------|--------|
| [`route_audit.py`](route_audit.py) | 指令 1 · 全站路由体检 | sitemap 全路径 × 4 变体（原样/尾斜杠/.html/全大写）+ 假路径，输出状态码表，回答有无软 404、多少重复 URL、有无 301/404 |
| [`orphan_pages.py`](orphan_pages.py) | 指令 2 · 孤岛页面检测 | 从首页抓内链建有向图，算每页入度，列出孤岛页、弱连接页（只来自导航/页脚）、点击深度≥4 的页 |
| [`geo_check.py`](geo_check.py) | 指令 3 · AI 能不能读懂你 | 检查 robots.txt 是否屏蔽 5 类 AI 爬虫、关 JS 后正文是否还在、语义标签、JSON-LD、H1，评估被 AI 引用概率 |

### 用法

把 `https://你的域名` 换成你自己的网址：

```bash
# 1. 全站路由体检（假路径 /this-should-404-xyz123 是否返回 200）
python route_audit.py https://你的域名 --out route.md

# 2. 孤岛页面检测（最多抓 500 页）
python orphan_pages.py https://你的域名 --max-pages 500 --out orphans.md

# 3. GEO 审计（AI 爬虫能否抓取、关 JS 后有无正文）
python geo_check.py https://你的域名 --out geo.md
```

不限页数、调并发、改超时：

```bash
python route_audit.py https://你的域名 --limit 0 --workers 8 --timeout 12
```

> **在 AI 给建站的那个文件夹里直接跑更好**——源文件都在里面，查出问题方便直接改。原文也提到：Shopify / WordPress 站也可以试试这三个思路。

### 报告示例

见 [`report-example/`](report-example/)，包含三份真实运行输出。

---

## 输出怎么读

- **route_audit**：看「结论」3 问。假路径 200 = 有软 404；「多版本200」列 = 重复 URL；重定向目标列 = 301 情况。
- **orphan_pages**：清单 1 是必须修的孤岛（没有任何内链）；清单 3 是埋太深的页，用聚合页（分类页）放进导航/页脚/侧边栏，保证首页点击到任意页 ≤3 次。
- **geo_check**：5 项每项给「通过/不通过 + 证据」，最后给 AI 引用概率粗判。优先修 robots 屏蔽和关 JS 白屏——AI 爬虫抓不到正文就无从引用。

修完想核对，可再用 [Screaming Frog](https://www.screamingfrog.co.uk/seo-spider/) 全量爬一遍。

---

## 命令版 vs 提示词版

本仓库同时保留两种用法：

- **命令版（本工具）**：直接跑脚本，结果稳定、可复现、可进 CI。
- **提示词版**：[`prompts/`](prompts/) 里是原文 3 条指令原文，复制给 Codex / Claude Code / WorkBuddy / DeepSeek Harness 等**能执行命令的 AI 智能体**诊断（原文强调不要用网页聊天窗口的 Gemini / ChatGPT / DeepSeek，诊断不全面）。

两者检测逻辑一致，选你顺手的。

---

## 一句话总结

网站不是给自己看的。它唯一的价值，是让一个完全不认识你的人，在搜索框里打几个字，找到你。

---

## 延伸阅读

- [原文：Codex 等 AI 建站隐患多，快速排查教程 · seogeo.cc](https://seogeo.cc/ai-built-site-seo-risks-quick-check)
- [seogeo.cc 首页：外贸 SEO / GEO 实战](https://seogeo.cc)
- [配套项目：用 AI 智能体做外贸独立站 13 步 SOP](https://github.com/suikusales-hub/ai-agent-b2b-static-site-sop)

---

## License

MIT —— 脚本代码可自由使用修改。排查逻辑与提示词整理自 [seogeo.cc 原文](https://seogeo.cc/ai-built-site-seo-risks-quick-check)，原文著作权归作者 SEO小平 所有，转载请保留原文链接。
