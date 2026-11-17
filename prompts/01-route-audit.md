# 指令 1 · 全站路由体检

复制给 AI 智能体，用前把 `https://你的域名` 换成你的网址。

```
你是技术SEO审计员。目标站点：https://你的域名  请实际发HTTP请求，不要凭经验推测。  1. 从 sitemap.xml 取出全部页面路径 2. 每个路径测4种变体：原样 / 加尾斜杠 / 加.html / 全大写 3. 再测一个假路径 /this-should-404-xyz123 4. 记录每个请求的状态码和重定向目标  输出一张表：路径 | 各变体状态码 | 是否多版本200 | 假路径状态码  最后回答三个问题： - 有没有软404（假路径返回200） - 多少页面存在多版本200（重复URL） - 是否存在301 是否存在404  如果查出上述问题并告知如何修改
```

对应的可执行脚本：[`route_audit.py`](../route_audit.py)

原文：[https://seogeo.cc/ai-built-site-seo-risks-quick-check](https://seogeo.cc/ai-built-site-seo-risks-quick-check)
