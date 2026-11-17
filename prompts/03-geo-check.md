# 指令 3 · AI 能不能读懂你

复制给 AI 智能体，用前把 `https://你的域名` 换成你的网址。

```
你是 AI 生成式引擎 GEO审计员。目标站点：https://你的域名  检查5项，每项给"通过/不通过 + 证据"：  1. robots.txt 是否 Disallow 了 GPTBot、ClaudeBot、PerplexityBot、Bytespider、Baiduspider 2. 关掉JavaScript后正文是否还在（AI爬虫多数不执行JS） 最后回答：如果用户在豆包，DeepSeek，ChatGPT，Gemini，Gork，Pperplexity里问这个领域的问题，这个站被上述AI引用的概率有多大？告诉我依据是什么？可以怎么提升优化现在的问题。
```

对应的可执行脚本：[`geo_check.py`](../geo_check.py)

原文：[https://seogeo.cc/ai-built-site-seo-risks-quick-check](https://seogeo.cc/ai-built-site-seo-risks-quick-check)
