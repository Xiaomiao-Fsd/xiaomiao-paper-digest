# NapCat QQ 后台常驻

## 脚本

- 启动：`scripts/start_napcat_qq.sh`
- 停止：`scripts/stop_napcat_qq.sh`
- 状态：`scripts/status_napcat_qq.sh`
- 安装开机/登录自启：`scripts/install_napcat_autostart.sh`

## 当前配置

- NapCat 根目录：`/home/huangchengbin/.openclaw/napcat-shell`
- QQ profile：`/home/huangchengbin/.openclaw/qq-napcat-profile-x11fix`
- 日志：`/home/huangchengbin/.openclaw/napcat-shell/napcat-x11fix.log`
- 自启动入口：`~/.config/autostart/napcat-qq.desktop`

## 说明

这套方案通过桌面自动启动在用户登录图形界面后拉起 NapCat + QQ，避免 Wayland 下直接出窗异常，强制走 X11/XWayland 模式。

如果当前已经手动启动过，`start_napcat_qq.sh` 会检测同 profile 的 QQ 进程并直接退出，不会重复拉起。
