# GLaDOS 自动签到

基于 GitHub Actions 的 GLaDOS 自动签到系统，支持飞书通知。

## 功能特性

- ✅ 每日自动签到
- ✅ 飞书通知（成功/失败）
- ✅ 显示积分、连续天数、余额
- ✅ Cookie 过期自动提醒
- ✅ 零成本（GitHub Actions 免费额度）

## 快速开始

### 1. 获取 Cookie

1. 登录 [GLaDOS](https://glados.one)
2. 打开浏览器开发者工具 (F12)
3. 切换到 Network 标签
4. 刷新页面，找到任意请求
5. 复制 Request Headers 中的 `Cookie` 值（完整字符串）

### 2. 创建 GitHub 仓库

1. Fork 或创建新仓库
2. 进入仓库 → Settings → Secrets and variables → Actions
3. 添加以下 Secrets：

| Secret 名称 | 值 | 说明 |
|------------|-----|------|
| `GLADOS_COOKIE` | `koa:sess=...; koa:sess.sig=...` | GLaDOS 的完整 Cookie |
| `FEISHU_WEBHOOK` | `https://open.feishu.cn/open-apis/bot/v2/hook/xxx` | 飞书机器人 Webhook（可选） |

### 3. 启用 Actions

1. 进入仓库 → Actions
2. 点击 "I understand my workflows, go ahead and enable them"
3. 选择 "GLaDOS Auto Checkin" workflow
4. 点击 "Run workflow" 手动测试

### 4. 查看结果

- 签到结果会在飞书收到通知
- 也可在 Actions 页面查看运行日志

## 配置说明

### 签到时间

默认每天北京时间 08:30 执行，修改 `.github/workflows/checkin.yml`：

```yaml
schedule:
  - cron: '30 0 * * *'  # UTC 时间，北京时间 = UTC + 8
```

常用时间：
- 08:00 → `cron: '0 0 * * *'`
- 09:00 → `cron: '0 1 * * *'`
- 12:00 → `cron: '0 4 * * *'`

### 飞书通知

1. 在飞书群聊中添加自定义机器人
2. 复制 Webhook 地址
3. 添加到 GitHub Secrets：`FEISHU_WEBHOOK`

不配置则只在 GitHub Actions 日志中显示结果。

## Cookie 有效期

- Cookie 通常有效期 1-3 个月
- 过期后签到会失败，飞书会收到失败通知
- 需要重新登录 GLaDOS 获取新 Cookie

## 本地测试

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export GLADOS_COOKIE="你的cookie"
export FEISHU_WEBHOOK="你的webhook"  # 可选

# 运行脚本
python glados_checkin.py
```

## 常见问题

### Q: Cookie 过期了怎么办？
A: 重新登录 GLaDOS，获取新 Cookie，更新 GitHub Secret 即可。

### Q: 如何修改签到时间？
A: 修改 `.github/workflows/checkin.yml` 中的 `cron` 字段。

### Q: 收不到飞书通知？
A: 检查 `FEISHU_WEBHOOK` Secret 是否正确配置。

### Q: Actions 没有自动运行？
A: GitHub Actions 默认禁用定时任务，需要手动触发一次或推送代码激活。

## 技术细节

- 签到 API: `POST https://glados.one/api/user/checkin`
- 认证方式: Cookie
- 运行环境: GitHub Actions (Ubuntu latest)
- Python 版本: 3.11

## License

MIT
