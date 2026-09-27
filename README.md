# 极致网络社网站

极致网络社（TOPSOFT-international）的静态网站，使用原生 HTML、CSS 和少量 JavaScript；没有构建步骤或前端框架，可直接部署到 GitHub Pages。此仓库原为 TopSoft 网站的 GitHub 镜像，便于维护；原 README 也说明镜像站更新可能更频繁。

## 页面与文件

- `index.html`：社团介绍、仍在讨论中的方向、负责人待补充位置和友情链接。
- `people.html`：现任负责人/创始人待补充项，以及按旧站资料整理的往期负责人和成员档案。
- `awcyvan.html`、`clock.html`、`memorygame.html`、`eyes.html`、`zen.html`：保留的旧个人页与小工具。
- `static/css/modern.css`、`static/js/site.js`：首页与档案页共用样式和移动导航。
- `static/images/bg.png`：沿用旧站页头照片。

## 内容来源与维护

旧站成员信息来自原网站 `https://awcyvan.github.io/exclub.github.io/` 的成员记录，保留了原姓名、年级、职务/自述和联系方式。旧站使用的“现任”只是旧页面当时的历史文字，不代表现在仍任职；年级也没有被推定为任期。档案中标为待补充的现任社长、副社长和创始人，需要负责人核实后再更新。

社团方向目前仍在讨论，详见[社团发展方向讨论稿](https://github.com/zzh10425/club-work/blob/main/%E5%BA%94%E5%AF%B9%E7%AD%96%E7%95%A5.md)。不要将未确认人员信息或讨论内容写成已确定事实。更新人员资料时请核实本人同意公开的字段，并同步首页状态与 `people.html` 档案。

旧站资源和友情链接可能失效。新增或调整外链前请核对目标；待建页不作为现有项目入口展示。

`awcyvan.html` 原有引用 `./static/css/google-front.css`，但仓库中没有该文件。这是旧个人页遗留问题；本次未替换该页面风格。

## 本地预览

无需安装依赖。在仓库根目录启动任意静态 HTTP 服务，例如：

```sh
python3 -m http.server 4173
```

然后访问 `http://127.0.0.1:4173/` 和 `http://127.0.0.1:4173/people.html`。也可以直接用浏览器打开 HTML 文件；HTTP 方式更接近 GitHub Pages。
