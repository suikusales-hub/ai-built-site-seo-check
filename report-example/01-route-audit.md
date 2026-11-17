# 全站路由体检报告

目标站点：https://seogeo.cc
检测页面：5

| 路径 | 原样 | 尾斜杠 | .html | 全大写 | 多版本200 | 重定向目标 |
|---|---|---|---|---|---|---|
| / | 200 | 200 | 0 | 200 | 否 | — |
| /about | 200 | 200 | 200 | 404 | 否 | https://seogeo.cc/about |
| /ai-knowledge-base | 200 | 200 | 200 | 404 | 否 | https://seogeo.cc/ai-knowledge-base |
| /contact | 200 | 200 | 200 | 404 | 否 | https://seogeo.cc/contact |
| /course-prep | 200 | 200 | 200 | 404 | 否 | https://seogeo.cc/course-prep |

## 结论（3 个问题）

- **有没有软 404（假路径返回 200）**：没有 — 假路径返回 404
- **多少页面存在多版本 200（重复 URL）**：0 个
- **301 是否存在**：无
- **404 是否存在**：有，共 4 次

> 修复建议：假路径返回 200 通常是路由回退首页（soft 404），需在服务端/构建配置里让未知路径返回真正 404；
> 多版本 200 需在 canonical 与服务器层统一到唯一 URL，非首选版本做 301；
> 检查每个页面 canonical 是否为绝对 URL 且指向自身，不要被模板写死。

参考原文：https://seogeo.cc/ai-built-site-seo-risks-quick-check
