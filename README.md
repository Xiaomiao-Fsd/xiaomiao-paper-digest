# xiaomiao-paper-digest

微电子 / 集成电路论文晨报静态站点仓库。

这个仓库用于托管每日生成的论文晨报页面，方便通过 GitHub Pages 长期稳定访问，不再依赖易失效的临时隧道链接。

## 站点地址

- 主入口：<https://xiaomiao-fsd.github.io/xiaomiao-paper-digest/>
- PC 版：<https://xiaomiao-fsd.github.io/xiaomiao-paper-digest/desktop.html>
- 手机版：<https://xiaomiao-fsd.github.io/xiaomiao-paper-digest/mobile.html>

## 这个仓库里有什么

当前静态站点包含：

- `index.html`：自动分流入口页（PC / 手机）
- `desktop.html`：适合桌面端阅读的表格式页面
- `mobile.html`：适合手机查看的卡片式页面
- `latest.json`：最近一次生成结果的结构化数据

## 内容来源

论文晨报由本地脚本自动生成，当前会聚合并筛选这些来源：

- arXiv
- Science Advances
- Nature Electronics
- Nature Materials

筛选策略以**微电子 / 集成电路**为基础范围，过滤掉偏数字电路 / IC 设计方向的内容，并优先保留：

- 晶体管 / FET / CMOS / GAA 相关工作
- 微电子材料相关工作
- Intel / TSMC 显式提及内容

## 更新方式

站点内容由本地工作流生成后同步到这个仓库。

也就是说，这个仓库本身主要承担的是：

1. 存放最新一版静态页面
2. 作为 GitHub Pages 发布源
3. 提供稳定可分享的公开链接

## 备注

如果 GitHub Pages 刚开启或刚更新后短时间内出现 404，通常是 GitHub 还在部署，稍等几分钟再刷新即可。
