# Daily WeChat Sender (GitHub Actions)

每天北京时间 08:00 自动发送固定格式微信模板消息（支持动态字段），通过 GitHub Actions 调度执行。

## 1. 功能说明

- 发送通道：微信公众号测试号模板消息
- 调度方式：GitHub Actions (`cron`)
- 支持动态字段：日期、星期、纪念日天数、可选天气
- 安全策略：敏感配置走 GitHub Secrets
- 失败告警：GitHub Actions 任务失败邮件

## 2. 项目结构

```text
.
├── app
│   ├── config.py
│   ├── main.py
│   ├── message_builder.py
│   ├── providers/weather.py
│   └── wechat_client.py
├── tests
├── .github/workflows/daily-wechat.yml
├── .env.example
└── requirements.txt
```

## 3. 微信侧准备

1. 进入微信公众号测试号平台并创建测试号。
2. 获取 `appID`、`appSecret`。
3. 让接收人扫码关注测试号，记录该用户 `openid`。
4. 配置模板并拿到 `template_id`。
5. 确保模板参数名称与本项目字段映射一致（默认 `first/date/weekday/weather/anniversary/remark`）。

## 4. GitHub 仓库配置

在仓库 `Settings -> Secrets and variables -> Actions -> Secrets` 添加：

- `WECHAT_APP_ID`
- `WECHAT_APP_SECRET`
- `WECHAT_TEMPLATE_ID`
- `WECHAT_TO_USER_OPENIDS`
- `QWEATHER_API_KEY`（仅当 `ENABLE_WEATHER=true` 时需要）

## 5. 本地运行

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.main --dry-run
python -m app.main --send-now
```

## 6. 定时任务

工作流文件在 `.github/workflows/daily-wechat.yml`，默认配置：

- `cron: "0 0 * * *"`（UTC 00:00 = 北京时间 08:00）
- 支持 `workflow_dispatch` 手动触发。

注意：GitHub `schedule` 可能有分钟级延迟，不保证绝对秒级准点。

## 7. 常见问题

1. `Failed to get access_token`
   - 检查 `WECHAT_APP_ID` / `WECHAT_APP_SECRET` 是否正确。
2. `Template message rejected`
   - 检查模板字段映射是否和你在测试号后台的模板字段一致。
3. 天气字段为空
   - 检查 `ENABLE_WEATHER` 和 `QWEATHER_API_KEY`、`WEATHER_LOCATION`。
   - QWeather API 注册地址：https://console.qweather.com/
   - 免费版限制：1000次/天

## 8. 可扩展方向

1. 支持多接收人列表循环发送。
2. 增加备用告警通道（邮件/第三方推送）。
3. 根据星期几或节假日切换模板。
