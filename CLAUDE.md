# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个CCF论文投稿截止日期邮件提醒系统，使用Python标准库实现，无需第三方依赖。

## 核心文件

- `email_sender.py` - 主程序，包含邮件发送逻辑和HTML生成
- `config.json` - 邮件服务器配置（包含敏感信息，已在.gitignore中）
- `conferences.json` - CCF会议信息数据库
- `.env.example` - 环境变量示例文件
- `.github/workflows/ccf-reminder.yml` - GitHub Actions自动化工作流

## 开发命令

### 运行邮件发送程序
```bash
# 查询未来30天内的截止日期（默认）
python email_sender.py

# 自定义查询天数
python email_sender.py --days 60
python email_sender.py -d 7

# 使用自定义配置文件
python email_sender.py --config custom_config.json
```

### 测试
本项目使用Python标准库，无需安装依赖。直接运行即可测试：
```bash
python email_sender.py --days 30
```

## 架构说明

### 邮件发送流程
1. `CCFDeadlineEmailer.__init__()` - 加载配置和会议数据
2. `get_upcoming_deadlines()` - 筛选即将截止的会议
3. `generate_email_content()` - 生成HTML格式邮件内容
4. `send_email()` - 通过SMTP发送邮件

### 配置加载优先级
环境变量 > config.json

支持的环境变量：
- `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`
- `FROM_EMAIL`, `FROM_NAME`, `TO_EMAILS`

### 会议数据结构
```json
{
  "name": "会议名称",
  "rank": "A/B/C",
  "deadline": "YYYY-MM-DD",
  "conference_date": "会议日期",
  "website": "官网URL",
  "description": "会议简介"
}
```

## 邮件HTML生成

邮件内容按紧急程度分为三类：
- 紧急（7天内截止）- 红色标识
- 需关注（15天内截止）- 橙色标识
- 即将到来（30天内）- 蓝色标识

使用CSS实现响应式设计，支持移动端查看。

## 自动化部署

### GitHub Actions
- 工作流文件: `.github/workflows/ccf-reminder.yml`
- 运行时间: 每周一上午9点（北京时间）
- 需要配置的Secrets: `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `FROM_EMAIL`, `TO_EMAILS`

### 本地定时任务
- Windows: 使用任务计划程序运行 `.bat` 文件
- Linux: 使用cron定时任务

## 维护任务

### 更新会议信息
编辑 `conferences.json`，从 https://ccfddl.top/ 获取最新截止日期。

### 修改邮件样式
编辑 `email_sender.py` 中的 `generate_email_content()` 方法的HTML/CSS部分。

### 添加新功能
- 支持 `--rank` 参数筛选特定CCF等级的会议
- 添加 `--field` 参数按研究领域筛选
- 实现会议信息自动抓取功能

## 安全注意事项

- ⚠️ 不要将 `config.json` 或 `.env` 文件提交到公共仓库
- ⚠️ `.gitignore` 已配置忽略这些文件
- ⚠️ GitHub Actions使用Secrets存储敏感信息
- ⚠️ 应用专用密码不是登录密码，需要单独生成

## 参考资源

- CCF会议截止日期: https://ccfddl.top/
- Gmail应用密码: https://myaccount.google.com/apppasswords
