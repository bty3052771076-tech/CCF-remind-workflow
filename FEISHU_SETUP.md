# 飞书机器人配置指南

## 飞书机器人优势

相比邮件通知，飞书机器人具有以下优势：

- ✅ **配置简单**：无需SMTP服务器，只需一个webhook地址
- ✅ **即时提醒**：消息立即送达，支持手机推送
- ✅ **富文本支持**：支持卡片、颜色、按钮等丰富格式
- ✅ **免费使用**：完全免费，无发送频率限制
- ✅ **易于查看**：在群聊中直接查看，历史记录可追溯

## 快速开始（3步完成）

### 步骤1: 创建飞书群聊

1. 打开飞书客户端或网页版
2. 创建一个新群聊（或使用现有群聊）
3. 群名称建议：`CCF会议提醒` 或 `学术投稿提醒`

### 步骤2: 添加自定义机器人

1. 进入群聊设置
2. 点击 **「群机器人」** → **「添加机器人」**
3. 选择 **「自定义机器人」**
4. 设置机器人名称（如：`CCF会议提醒助手`）
5. 上传机器人头像（可选）
6. 点击 **「添加」**

### 步骤3: 获取Webhook地址

1. 添加成功后，会显示 **「Webhook地址」**
2. 复制完整的webhook地址（格式：`https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxxxxxxx`）
3. 将地址粘贴到 `feishu_config.json` 文件中

## 配置文件设置

编辑 `feishu_config.json`：

```json
{
  "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxxxxxxxxxxxxxxxxxx"
}
```

将 `xxxxxxxxxxxxxxxxxxxxxxxx` 替换为您复制的webhook地址。

## 运行程序

```bash
# 发送未来30天内的截止提醒
python feishu_notifier.py

# 发送未来60天内的截止提醒
python feishu_notifier.py --days 60

# 发送未来7天内的截止提醒
python feishu_notifier.py -d 7

# 使用自定义webhook地址
python feishu_notifier.py --webhook "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx"
```

## 消息效果示例

飞书机器人会发送精美的卡片消息，包含：

- 📊 统计信息：找到多少个即将截止的会议
- 🔥 按紧急程度分类（7天/15天/30天内）
- 📋 每个会议的详细信息：
  - 会议名称和CCF等级（带颜色标识）
  - 投稿截止日期
  - 剩余天数
  - 会议日期
  - 官方网站链接
- 🔗 快捷按钮：查看更多会议、访问CCF官网

## 自动化部署

### GitHub Actions

编辑 `.github/workflows/ccf-reminder.yml`：

```yaml
name: CCF会议截止日期提醒

on:
  schedule:
    - cron: '0 1 * * 1'  # 每周一上午9点（北京时间）
  workflow_dispatch:

jobs:
  send-reminder:
    runs-on: ubuntu-latest

    steps:
    - name: 检出代码
      uses: actions/checkout@v4

    - name: 设置Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'

    - name: 发送飞书通知
      env:
        WEBHOOK_URL: ${{ secrets.FEISHU_WEBHOOK_URL }}
      run: |
        python feishu_notifier.py --days 30
```

**配置GitHub Secrets**：
1. 在GitHub仓库设置中添加Secret
2. Secret名称：`FEISHU_WEBHOOK_URL`
3. Secret值：您的webhook地址

### Windows定时任务

创建 `run_feishu_reminder.bat`：

```batch
@echo off
cd /d D:\AI\cc+glm\submit_paper
python feishu_notifier.py --days 30
pause
```

然后在任务计划程序中设置每周一运行此脚本。

### Linux Cron

编辑crontab：

```bash
crontab -e
```

添加：

```cron
0 9 * * 1 cd /path/to/submit_paper && /usr/bin/python3 feishu_notifier.py --days 30
```

## 安全建议

- ⚠️ **不要将webhook地址泄露**：拥有webhook地址的人可以向群聊发送消息
- ⚠️ **提交到Git时忽略配置文件**：`feishu_config.json` 已在 `.gitignore` 中
- ✅ **使用环境变量**：在GitHub Actions等场景中使用Secrets存储webhook地址

## 故障排查

### 问题1: 提示"未配置webhook地址"

**解决方案**：
- 检查 `feishu_config.json` 文件是否存在
- 确认 `webhook_url` 字段已填写且格式正确

### 问题2: 发送失败，提示HTTP错误

**可能原因**：
- Webhook地址不正确
- 机器人已被删除

**解决方案**：
- 重新获取webhook地址
- 检查机器人是否仍然存在

### 问题3: 群聊中收不到消息

**可能原因**：
- 网络连接问题
- 机器人被禁用

**解决方案**：
- 检查网络连接
- 在群设置中确认机器人状态

## 对比：邮件 vs 飞书机器人

| 特性 | 邮件 | 飞书机器人 |
|------|------|-----------|
| 配置难度 | ⭐⭐⭐ 需要SMTP | ⭐ 仅需webhook |
| 即时性 | ⭐⭐ 可能延迟 | ⭐⭐⭐ 立即送达 |
| 格式支持 | ⭐⭐ HTML | ⭐⭐⭐ 富文本卡片 |
| 手机推送 | ⭐⭐ 需要设置 | ⭐⭐⭐ 原生支持 |
| 历史记录 | ⭐⭐ 收件箱 | ⭐⭐⭐ 群聊天 |
| 配置成本 | 免费/付费 | 完全免费 |

## 进阶功能

### 自定义消息样式

编辑 `feishu_notifier.py` 中的 `generate_card_content()` 方法，自定义卡片样式：

- 修改颜色主题
- 添加更多元素（图片、表格等）
- 自定义按钮文本和链接

### 多群聊通知

如果需要向多个群聊发送通知，可以：

1. 为每个群创建一个机器人
2. 修改程序支持多个webhook地址
3. 循环发送到每个群

### 富文本消息

除了卡片消息，飞书还支持：

- 纯文本消息
- Markdown消息
- 图片消息
- 文件消息

参考：https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot

## 参考资源

- [飞书自定义机器人使用指南](https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot)
- [手把手教你用飞书Webhook打造消息推送Bot](https://open.feishu.cn/community/articles/7271149634339422210)
- [通过飞书机器人发消息 - 帮助中心](https://www.feishu.cn/hc/zh-CN/articles/348229340087)

## 开始使用

现在您可以：
1. 创建飞书群聊并添加机器人
2. 获取webhook地址并配置到 `feishu_config.json`
3. 运行 `python feishu_notifier.py` 测试
4. 配置自动化任务（GitHub Actions 或 定时任务）
