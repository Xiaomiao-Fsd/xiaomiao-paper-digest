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
