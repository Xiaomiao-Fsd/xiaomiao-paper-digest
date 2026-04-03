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

### 你导入 n8n 后还需要做的最后一步

把 `Prepare Notification Payload` 后面接一个你自己的通知节点。

推荐做法：

1. 如果你已经有自己的 Webhook / IM 通知链路：
   - 直接把 `message` 发出去
2. 如果你以后要把消息再送回 OpenClaw / QQ：
   - 可以在 n8n 里再接一个 Execute Command / HTTP Request 节点
   - 把 `message` 原样推给你的通知入口

### 为什么 workflow 里不直接写死最终通知节点

因为你当前的提醒终点还是通过 OpenClaw 的会话路由在走，n8n 那边的最终投递方式后面可能还会变。先把“抓取、过滤、去重、抓图”这段稳定下来，后接通知渠道会更灵活。
