# n8n Workflows

## `Seele_Leaks_HI3rd_public_monitor.workflow.json`

用途：监看公开 Telegram 页面 `https://t.me/s/Seele_Leaks`，只保留“开头括号标签里包含 `HI3rd`”的帖子，下载前 4 张图片，并把可直接发送的消息体产出到 `message` 字段。

### 当前 workflow 已完成

- 每 5 分钟轮询
- 通过本机 Clash 代理 `http://127.0.0.1:7897`
- 调用工作区脚本：
  - `/home/XiaomiaoClaw/.openclaw/workspace/scripts/telegram_public_monitor.py`
- 使用状态文件去重：
  - `/home/XiaomiaoClaw/.openclaw/workspace/.openclaw/seele_leaks_state.json`
- 下载图片到：
  - `/home/XiaomiaoClaw/.openclaw/workspace/tmp/telegram_public_monitor_media`
- 命中时输出：
  - `channel`
  - `latest_id`
  - `new_count`
  - `message`
  - `new_posts_json`

### 现在已经直接接好 QQ 通知

当前 JSON 版本已经包含最终通知节点，不需要你再手动补最后一步。

它会这样做：

1. n8n 轮询公开 Telegram 页面
2. 过滤“开头括号标签里包含 `HI3rd`”的帖子
3. 去重
4. 下载前 4 张图
5. 生成单条通知消息（文字 + `<qqimg>` 标签）
6. 调用本地 helper：
   - `/home/XiaomiaoClaw/.openclaw/workspace/scripts/openclaw_notify_session.py`
7. 通过 OpenClaw 把消息送回当前这个 QQ 私聊会话

### 依赖的本地脚本

- 监看脚本：
  - `/home/XiaomiaoClaw/.openclaw/workspace/scripts/telegram_public_monitor.py`
- QQ 通知 helper：
  - `/home/XiaomiaoClaw/.openclaw/workspace/scripts/openclaw_notify_session.py`

### 说明

这个方案仍然复用 OpenClaw 做最终 QQ 投递，因此不会直接绕过现有消息路由。

---

## `Microelectronics_Paper_Digest.workflow.json`

用途：每天早上生成一条“微电子 / 集成电路相关论文晨报”。策略上先宽泛覆盖微电子与集成电路方向，再过滤偏数字电路 / IC 设计的话题，最后优先保留晶体管与材料相关论文，并额外关注 Intel / TSMC 相关内容。

### 当前 workflow 已完成

- 每天 08:30 定时执行
- 通过本机 Clash 代理 `http://127.0.0.1:7897`
- 调用工作区脚本：
  - `/home/XiaomiaoClaw/.openclaw/workspace/scripts/paper_digest_monitor.py`
- 使用状态文件去重：
  - `/home/XiaomiaoClaw/.openclaw/workspace/.openclaw/paper_digest_state.json`
- 汇总来源：
  - arXiv
  - Science Advances（Crossref）
  - Nature Electronics RSS
  - Nature Materials RSS
- 输出字段：
  - `new_count`
  - `selected_count`
  - `message`
  - `papers`
  - `errors`

### 现在已经直接接好 QQ 通知

当前 JSON 版本已经包含最终通知节点，不需要再手动补最后一步。

它会这样做：

1. 每天早上拉取各来源最新论文
2. 先按“微电子 / 集成电路”相关关键词做宽泛召回
3. 过滤偏数字电路 / IC 设计方向的内容
4. 再按“晶体管 / FET / CMOS / GAA / 材料”做优先级打分
5. 对 Intel / TSMC 显式提及项进一步提高优先级
6. 生成单条中文晨报消息
7. 调用本地 helper：
   - `/home/XiaomiaoClaw/.openclaw/workspace/scripts/openclaw_notify_session.py`
8. 通过 OpenClaw 把消息送回当前这个 QQ 私聊会话

### 依赖的本地脚本

- 论文晨报脚本：
  - `/home/XiaomiaoClaw/.openclaw/workspace/scripts/paper_digest_monitor.py`
- QQ 通知 helper：
  - `/home/XiaomiaoClaw/.openclaw/workspace/scripts/openclaw_notify_session.py`

### 说明

这个方案默认使用更贴近目标方向的 Nature 系列来源：`Nature Electronics` 和 `Nature Materials`。如果之后想切到别的 Nature 子刊或扩展更多期刊，可以直接在脚本和 workflow 上继续加源。
