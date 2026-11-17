# GEO 审计报告 · AI 能不能读懂你

目标站点：https://seogeo.cc

## 检查 5 项（通过/不通过 + 证据）

### 1. robots.txt 是否屏蔽 AI 爬虫
- **通过** — 未发现 GPTBot / ClaudeBot / PerplexityBot / Bytespider / Baiduspider 被全站屏蔽

### 2. 关掉 JavaScript 后正文是否还在
- **通过** — 原始 HTML 可见文本约 7596 字符

### 3. 正文是否纯 HTML 可读
- **通过** — 语义标签 main/article：有
- **通过** — 图片缺 alt：0 张

### 4. 是否有结构化数据（JSON-LD）
- **不通过** — 页面不含 `application/ld+json`

### 5. 标题层级与事实表达
- **通过** — H1：有
- 提示：品牌名、地址、认证、产能等事实要写成明确句子，不要只放在图片里。

## AI 引用概率评估（粗判）

- 5 项中约 1 项不通过/存疑。
- 如果用户在豆包、DeepSeek、ChatGPT、Gemini、Grok、Perplexity 里问这个领域的问题：被引用概率**中等偏高** — 基础可读性与抓取通道基本正常，建议补充结构化数据与明确事实句。
- 依据：AI 爬虫多数不执行 JS、且遵循 robots.txt；抓不到正文就无法引用。

参考原文：https://seogeo.cc/ai-built-site-seo-risks-quick-check
