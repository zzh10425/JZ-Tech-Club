# 极致网络社网站

极致网络社（TOPSOFT-international）的静态网站，使用原生 HTML、CSS 和少量 JavaScript；没有前端框架，成员页面由 Python 标准库脚本在部署前生成，可直接部署到 GitHub Pages。此仓库原为 TopSoft 网站的 GitHub 镜像，便于维护；原 README 也说明镜像站更新可能更频繁。

## 页面与文件

- `index.html`：社团介绍、仍在讨论中的方向、负责人待补充位置和友情链接。
- `people.html`：现任负责人/创始人待补充项，以及按旧站资料整理的往期负责人和成员档案。
- `awcyvan.html`、`clock.html`、`memorygame.html`、`eyes.html`、`zen.html`：保留的旧个人页与小工具。
- `static/css/modern.css`、`static/js/site.js`：首页与档案页共用样式和移动导航。
- `static/images/bg.png`：沿用旧站页头照片。
- `scripts/generate_people.py`：从 `data/people.csv` 生成首页负责人和成员信息静态 HTML。
- `scripts/view_server.py`：在临时目录生成并启动本地预览，不覆盖根目录 HTML。

页面使用仓库内打包的 JetBrains Mono Nerd Font Mono（西文、数字）和 Noto Sans Mono CJK SC（中文）字体文件，确保不同设备上的显示效果一致。字体文件随项目静态资源一同分发，不依赖用户系统是否安装对应字体，也不请求外部字体服务。

## 内容来源与维护

旧站成员信息来自原网站 `https://awcyvan.github.io/exclub.github.io/` 的成员记录，保留了原姓名、年级、职务/自述和联系方式。旧站使用的“现任”只是旧页面当时的历史文字，不代表现在仍任职；年级也没有被推定为任期。档案中标为待补充的现任社长、副社长和创始人，需要负责人核实后再更新。

### 更新及维护方式
工具:WPS/VSCode
使用编辑器打开 项目根目录/data/people.csv 
添加新成员,将已有条目中的 **"本期负责人"** 改为 **"往期负责人"**   
随后,在文件末尾添加以 **"本期负责人"** 为类别的新条目   
>注:(若使用VSCode)每个数据以英文(逗号) **__","__** 分隔 不建议使用中文(逗号) **__"，"__**

已有条目
```csv
序号,类别,职位,姓名,年级,自述,补充信息,QQ,Email,链接说明,链接
```

社团方向目前仍在讨论，详见[社团发展方向讨论稿](https://github.com/zzh10425/club-work/blob/main/%E5%BA%94%E5%AF%B9%E7%AD%96%E7%95%A5.md)。不要将未确认人员信息或讨论内容写成已确定事实。更新人员资料时请核实本人同意公开的字段；修改 `data/people.csv` 后运行 `python scripts/generate_people.py`，生成并更新 `index.html` 与 `people.html`。

旧站资源和友情链接可能失效。新增或调整外链前请核对目标；待建页不作为现有项目入口展示。

`awcyvan.html` 原有引用 `./static/css/google-front.css`，但仓库中没有该文件。这是旧个人页遗留问题；本次未替换该页面风格。

## 本地预览

推荐运行本地临时预览，生成的 HTML 和复制的静态资源会在退出时自动清理，不会覆盖根目录的页面：

```sh
python scripts/view_server.py
```

脚本会输出随机可用端口的 `http://127.0.0.1:PORT/` 地址，并尝试自动打开浏览器。修改 `data/people.csv` 后，预览会重新生成页面；正式更新仍运行 `python scripts/generate_people.py`。
