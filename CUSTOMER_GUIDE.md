# 客户邮箱管理系统使用指南

## 📋 功能概述

客户邮箱管理系统允许您：
- ✅ 添加客户邮箱
- ✅ 删除客户邮箱
- ✅ 启用/禁用客户
- ✅ 批量发送提醒给所有客户
- ✅ 数据本地保存，隐私安全

---

## 🚀 快速开始

### 1. 查看客户列表

```bash
python manage_customers.py list
```

输出示例：
```
================================================================================
📋 客户邮箱列表
================================================================================
序号    状态     邮箱                             名称                   添加日期
--------------------------------------------------------------------------------
1     ✅启用    3052771076@qq.com              默认客户                 2026-01-19
2     ❌禁用    customer2@example.com          张三                     2026-01-18
--------------------------------------------------------------------------------
总计：2 个客户，其中 1 个已启用
================================================================================
```

### 2. 添加客户

```bash
# 基本添加（只提供邮箱）
python manage_customers.py add --email customer@example.com

# 添加客户并指定名称
python manage_customers.py add --email customer@example.com --name "张三"
```

### 3. 删除客户

```bash
python manage_customers.py remove --email customer@example.com
```

### 4. 启用/禁用客户

```bash
# 启用客户
python manage_customers.py enable --email customer@example.com

# 禁用客户（临时不发送提醒）
python manage_customers.py disable --email customer@example.com
```

---

## 📧 发送邮件给客户

### 方式1：发送给配置中的单个收件人

```bash
python email_sender.py --days 30
```

### 方式2：批量发送给所有启用的客户（推荐⭐）

```bash
python email_sender.py --customers --days 30
```

这会读取 `customers.json` 文件，自动发送给所有**启用状态**的客户。

---

## 📁 文件说明

### customers.json
存储客户邮箱列表的配置文件：

```json
{
  "customers": [
    {
      "email": "3052771076@qq.com",
      "name": "默认客户",
      "enabled": true,
      "added_date": "2026-01-19"
    },
    {
      "email": "customer2@example.com",
      "name": "张三",
      "enabled": false,
      "added_date": "2026-01-18"
    }
  ],
  "notes": "客户邮箱列表，用于批量发送CCF会议提醒",
  "last_updated": "2026-01-19 11:20:24"
}
```

**字段说明**：
- `email`: 客户邮箱地址（必需）
- `name`: 客户名称（可选）
- `enabled`: 是否启用（true/false）
- `added_date`: 添加日期

---

## 🔧 常用命令

### 管理客户

```bash
# 查看所有客户
python manage_customers.py list

# 添加客户
python manage_customers.py add --email xxx@qq.com --name "客户名称"

# 删除客户
python manage_customers.py remove --email xxx@qq.com

# 启用客户
python manage_customers.py enable --email xxx@qq.com

# 禁用客户
python manage_customers.py disable --email xxx@qq.com
```

### 发送邮件

```bash
# 发送给单个收件人（使用config.json中的配置）
python email_sender.py --days 30

# 批量发送给所有启用的客户
python email_sender.py --customers --days 30

# 查询未来60天内的截止日期
python email_sender.py --customers --days 60
```

---

## 💡 使用场景

### 场景1：管理多个客户

您有多个客户需要接收会议提醒：

```bash
# 添加多个客户
python manage_customers.py add --email client1@example.com --name "客户A"
python manage_customers.py add --email client2@example.com --name "客户B"
python manage_customers.py add --email client3@example.com --name "客户C"

# 查看所有客户
python manage_customers.py list

# 一次性发送给所有客户
python email_sender.py --customers --days 30
```

### 场景2：临时禁用某个客户

某个客户暂时不需要提醒：

```bash
# 禁用客户
python manage_customers.py disable --email client1@example.com

# 发送提醒（该客户不会收到）
python email_sender.py --customers --days 30

# 重新启用
python manage_customers.py enable --email client1@example.com
```

### 场景3：定期批量发送

创建批处理文件 `send_to_all_customers.bat`：

```batch
@echo off
cd /d D:\AI\cc+glm\submit_paper
echo 开始发送CCF会议提醒给所有客户...
python email_sender.py --customers --days 30
echo 发送完成！
pause
```

然后在Windows任务计划程序中设置每周一自动运行。

---

## 🔒 隐私安全

- ✅ `customers.json` 已添加到 `.gitignore`
- ✅ 数据保存在本地，不会上传到Git仓库
- ✅ 只有您可以访问客户列表

---

## 📝 命令参考

### manage_customers.py 命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `list` | 查看客户列表 | `python manage_customers.py list` |
| `add` | 添加客户 | `python manage_customers.py add --email xxx@qq.com --name "名称"` |
| `remove` | 删除客户 | `python manage_customers.py remove --email xxx@qq.com` |
| `enable` | 启用客户 | `python manage_customers.py enable --email xxx@qq.com` |
| `disable` | 禁用客户 | `python manage_customers.py disable --email xxx@qq.com` |

### email_sender.py 参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--days` | 查询天数 | `--days 60` |
| `--config` | 配置文件 | `--config custom_config.json` |
| `--customers` | 使用客户列表 | `--customers` |

---

## 🎯 完整工作流程示例

### 初次设置

```bash
# 1. 查看现有客户
python manage_customers.py list

# 2. 添加客户
python manage_customers.py add --email customer1@qq.com --name "腾讯邮箱客户"
python manage_customers.py add --email customer2@gmail.com --name "Gmail客户"

# 3. 确认客户列表
python manage_customers.py list

# 4. 发送测试邮件（只发送给config.json中的收件人）
python email_sender.py --days 7

# 5. 批量发送给所有客户
python email_sender.py --customers --days 30
```

### 日常维护

```bash
# 每周一自动发送给所有客户
python email_sender.py --customers --days 30

# 添加新客户
python manage_customers.py add --email newcustomer@example.com --name "新客户"

# 删除不需要的客户
python manage_customers.py remove --email oldcustomer@example.com

# 查看当前客户列表
python manage_customers.py list
```

---

## ❓ 常见问题

**Q: customers.json 文件在哪里？**
- A: 在项目根目录，与 `email_sender.py` 同级

**Q: 如何备份客户数据？**
- A: 直接复制 `customers.json` 文件即可

**Q: 批量发送时失败怎么办？**
- A: 程序会显示每个客户的发送状态，失败的客户可以单独重试

**Q: 可以同时发送飞书和邮件吗？**
- A: 可以！创建批处理文件同时调用两个程序

---

## 📊 示例：自动化批处理

创建 `send_all_reminders.bat`：

```batch
@echo off
cd /d D:\AI\cc+glm\submit_paper
echo ========================================
echo   CCF会议提醒系统 - 批量发送
echo ========================================
echo.
echo [%date% %time%] 开始发送飞书提醒...
python feishu_notifier.py --days 30
echo.
echo [%date% %time%] 开始发送邮件提醒给所有客户...
python email_sender.py --customers --days 30
echo.
echo ========================================
echo   发送完成！
echo ========================================
pause
```

在Windows任务计划程序中设置此脚本每周一上午9点自动运行。

---

## 🎉 开始使用

现在您可以：
1. 使用 `manage_customers.py` 管理客户邮箱
2. 使用 `email_sender.py --customers` 批量发送提醒
3. 客户数据安全保存在本地

享受自动化的CCF会议提醒服务！🎊
