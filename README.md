# CCF论文投稿截止日期提醒系统

支持**邮件**和**飞书机器人**两种提醒方式的Python程序，自动追踪CCF会议投稿截止日期并发送提醒。

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ✨ 功能特点

- 📊 **自动追踪**CCF会议投稿截止日期
- 🔥 **智能分类**按紧急程度（7天/15天/30天内）
- 🎨 **精美格式**HTML邮件 / 飞书卡片
- 👥 **客户管理**批量发送给多个客户
- 🔄 **自动化**支持GitHub Actions定时运行
- 📱 **多端支持**PC端 / 移动端查看

---

## 📋 功能对比

| 特性 | 邮件通知 | 飞书机器人 |
|------|---------|-----------|
| **配置难度** | ⭐⭐⭐ 需要SMTP | ⭐ 仅需webhook |
| **即时性** | ⭐⭐ 可能有延迟 | ⭐⭐⭐ 立即送达 |
| **消息格式** | ⭐⭐ HTML邮件 | ⭐⭐⭐ 富文本卡片 |
| **手机推送** | ⭐⭐ 需要邮件APP | ⭐⭐⭐ 飞书原生 |
| **批量发送** | ⭐⭐⭐ 支持客户列表 | ⭐⭐⭐ 单群发送 |
| **推荐场景** | 个人/客户提醒 | 团队协作 |

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd submit_paper
```

### 2. 配置文件

#### 方式A：飞书机器人（推荐⭐）

创建 `feishu_config.json`：

```json
{
  "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxxxxxxxxxxxxxxxxxx"
}
```

#### 方式B：邮件通知

创建 `config.json`：

```json
{
  "smtp_server": "smtp.qq.com",
  "smtp_port": 587,
  "smtp_user": "your_email@qq.com",
  "smtp_password": "your_auth_code",
  "from_email": "your_email@qq.com",
  "from_name": "CCF会议提醒助手",
  "to_emails": "recipient@example.com"
}
```

#### 方式C：客户管理（可选）

创建 `customers.json`：

```json
{
  "customers": [
    {
      "email": "customer1@example.com",
      "name": "客户1",
      "enabled": true,
      "added_date": "2026-01-19"
    }
  ]
}
```

⚠️ **重要**：配置文件包含敏感信息，已添加到 `.gitignore`，不会上传到Git。

### 3. 运行程序

```bash
# 发送飞书提醒
python feishu_notifier.py --days 30

# 发送邮件提醒
python email_sender.py --days 30

# 批量发送给所有客户
python email_sender.py --customers --days 30
```

---

## 📖 详细文档

- [飞书机器人配置指南](FEISHU_SETUP.md)
- [邮件配置指南](SETUP_GUIDE.md)
- [客户管理指南](CUSTOMER_GUIDE.md)

---

## 🔧 配置说明

### 邮箱配置

#### QQ邮箱（推荐）

1. 登录 https://mail.qq.com
2. 设置 → 账户 → 开启 **IMAP/SMTP服务**
3. 生成授权码（16位）
4. 配置 `config.json`

```json
{
  "smtp_server": "smtp.qq.com",
  "smtp_port": 587,
  "smtp_user": "your_email@qq.com",
  "smtp_password": "your_auth_code",
  "from_email": "your_email@qq.com"
}
```

#### 163邮箱

1. 登录 https://mail.163.com
2. 设置 → POP3/SMTP/IMAP → 开启服务
3. 生成授权码
4. 配置 `config.json`

```json
{
  "smtp_server": "smtp.163.com",
  "smtp_port": 465,
  "smtp_user": "your_email@163.com",
  "smtp_password": "your_auth_code",
  "from_email": "your_email@163.com"
}
```

#### Gmail

1. 启用两步验证
2. 生成应用专用密码
3. 配置 `config.json`

```json
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_user": "your_email@gmail.com",
  "smtp_password": "your_app_password",
  "from_email": "your_email@gmail.com"
}
```

### 飞书机器人配置

1. 在飞书中创建群聊
2. 群设置 → 群机器人 → 添加机器人 → 自定义机器人
3. 复制webhook地址
4. 配置 `feishu_config.json`

---

## 🛠️ 使用命令

### 飞书机器人

```bash
# 发送未来30天内的会议提醒
python feishu_notifier.py

# 发送未来60天内的会议提醒
python feishu_notifier.py --days 60

# 使用自定义webhook
python feishu_notifier.py --webhook "https://..."
```

### 邮件发送

```bash
# 发送给单个收件人
python email_sender.py --days 30

# 批量发送给所有启用的客户
python email_sender.py --customers --days 30

# 使用自定义配置文件
python email_sender.py --config custom_config.json
```

### 客户管理

```bash
# 查看客户列表
python manage_customers.py list

# 添加客户
python manage_customers.py add --email client@qq.com --name "客户名称"

# 删除客户
python manage_customers.py remove --email client@qq.com

# 启用/禁用客户
python manage_customers.py enable --email client@qq.com
python manage_customers.py disable --email client@qq.com
```

---

## 📁 项目结构

```
submit_paper/
├── feishu_notifier.py          # 飞书机器人通知程序
├── email_sender.py              # 邮件通知程序
├── manage_customers.py          # 客户管理程序
├── test_feishu.py               # 飞书连接测试
├── test_email.py                # 邮件连接测试
├── conferences.json             # CCF会议数据
│
├── config.json                  # 邮件配置（敏感，不上传）
├── feishu_config.json           # 飞书配置（敏感，不上传）
├── customers.json               # 客户列表（敏感，不上传）
│
├── config.example.json          # 邮件配置模板
├── feishu_config.example.json   # 飞书配置模板
├── customers.example.json       # 客户列表模板
├── .env.example                 # 环境变量模板
│
├── .github/workflows/
│   └── ccf-reminder.yml         # GitHub Actions工作流
│
├── .gitignore                   # Git忽略文件
├── README.md                    # 本文件
├── FEISHU_SETUP.md              # 飞书配置详细指南
├── SETUP_GUIDE.md               # 邮件配置详细指南
└── CUSTOMER_GUIDE.md            # 客户管理详细指南
```

---

## ⚙️ 自动化部署

### GitHub Actions

1. 创建GitHub仓库
2. 配置Secrets：

**飞书方式**：
- `FEISHU_WEBHOOK_URL`: 飞书webhook地址

**邮件方式**：
- `SMTP_SERVER`: SMTP服务器
- `SMTP_PORT`: 端口号
- `SMTP_USER`: 邮箱账号
- `SMTP_PASSWORD`: 授权码
- `TO_EMAILS`: 收件人邮箱

3. 提交代码，自动每周运行

### Windows定时任务

创建批处理文件 `send_reminders.bat`：

```batch
@echo off
cd /d D:\AI\cc+glm\submit_paper
python feishu_notifier.py --days 30
python email_sender.py --customers --days 30
pause
```

在任务计划程序中设置每周一运行。

---

## 📊 会议数据

CCF会议信息存储在 `conferences.json` 中，包含：

- **name**: 会议名称
- **rank**: CCF等级（A/B/C）
- **deadline**: 投稿截止日期（YYYY-MM-DD）
- **conference_date**: 会议召开日期
- **website**: 官方网站
- **description**: 会议简介

**更新会议信息**：定期从 https://ccfddl.top/ 获取最新截止日期。

---

## 🔒 安全与隐私

### 敏感信息保护

以下文件**已添加到 `.gitignore`**，不会上传到Git：

- ❌ `config.json` - 包含邮箱、授权码
- ❌ `feishu_config.json` - 包含webhook地址
- ❌ `customers.json` - 包含客户邮箱

### 配置模板

提供配置模板文件（可以上传）：

- ✅ `config.example.json` - 邮件配置模板
- ✅ `feishu_config.example.json` - 飞书配置模板
- ✅ `customers.example.json` - 客户列表模板

---

## 🎯 使用场景

### 个人使用

- 使用飞书机器人接收提醒（最简单）
- 或使用邮件接收提醒（归档）

### 团队协作

- 飞书群聊：团队成员共享提醒
- 邮件批量：发送给多个客户

### 自动化运营

- GitHub Actions：自动每周运行
- 定时任务：Windows/Linux cron

---

## 📝 常见问题

### Q: 如何获取邮箱授权码？

**QQ邮箱**：设置 → 账户 → 开启IMAP/SMTP → 生成授权码
**163邮箱**：设置 → POP3/SMTP/IMAP → 开启服务 → 新增授权密码
**Gmail**：账户安全 → 两步验证 → 应用专用密码

### Q: 飞书机器人如何获取？

1. 飞书群聊 → 群设置 → 群机器人 → 添加机器人 → 自定义机器人
2. 复制webhook地址
3. 配置到 `feishu_config.json`

### Q: 如何批量发送给多个客户？

1. 使用 `manage_customers.py add` 添加客户
2. 使用 `email_sender.py --customers` 批量发送

### Q: 定时自动发送？

- **GitHub Actions**：自动每周一运行
- **Windows任务计划**：设置定时运行批处理文件
- **Linux cron**：设置crontab定时任务

---

## 🆘 获取帮助

- [飞书官方文档](https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot)
- [CCF会议截止日期](https://ccfddl.top/)
- [QQ邮箱帮助中心](https://help.mail.qq.com)

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

感谢所有为本项目提供帮助的贡献者！

---

## 📮 联系方式

如有问题或建议，请提交Issue或Pull Request。

---

## ⭐ 如果这个项目对您有帮助，请给个Star！

**最后更新**: 2026-01-19
