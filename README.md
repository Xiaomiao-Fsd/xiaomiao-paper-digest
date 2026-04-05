# xiaomiao-paper-digest

微电子 / 集成电路论文晨报静态站点仓库。

这个仓库用于托管每日生成的论文晨报页面，方便通过 GitHub Pages 长期稳定访问，不再依赖容易失效的临时隧道链接。

## 站点地址

- 主入口：<https://xiaomiao-fsd.github.io/xiaomiao-paper-digest/>
- PC 版：<https://xiaomiao-fsd.github.io/xiaomiao-paper-digest/desktop.html>
- 手机版：<https://xiaomiao-fsd.github.io/xiaomiao-paper-digest/mobile.html>

## 仓库用途

这个仓库本身不负责抓取论文，而是承担下面这几个角色：

1. 存放最新一版静态页面
2. 作为 GitHub Pages 的发布源
3. 提供可长期分享的公开链接
4. 让晨报网页和数据结果可以留痕、可回看、可维护

## 当前包含的文件

- `index.html`：自动分流入口页
- `desktop.html`：桌面端页面
- `mobile.html`：手机端页面
- `latest.json`：最近一次生成结果的结构化数据
- `README.md`：仓库说明与维护备注

## 页面功能

当前页面支持：

- 英文 abstract 浏览
- 中文摘要概括
- 正文阅读导向概括
- PC / 手机双版本
- 浅色 / 深色模式切换
- 本地浏览器收藏夹（长期显示收藏论文）

## 内容来源

当前会聚合并筛选这些来源：

- arXiv
- Science Advances
- Nature Electronics
- Nature Materials

## 更新链路

1. 本地定时任务每天运行
2. 本地脚本抓取并筛选论文
3. 生成 HTML / JSON 发布产物
4. 同步到本仓库
5. GitHub Pages 对外发布静态页面

## 备注

如果 GitHub Pages 刚更新后短时间内出现 404，通常是 GitHub 还在部署，稍等几分钟再刷新即可。
