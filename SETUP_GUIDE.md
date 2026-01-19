# CCF邮件提醒系统配置指南

## 需要配置的资源

### 1. 必需资源

#### Python环境
- **版本要求**: Python 3.7 或更高版本
- **检查方式**: 运行 `python --version`
- **下载地址**: https://www.python.org/downloads/

#### 邮箱账号
- **推荐**: Gmail（或其他支持SMTP的邮箱）
- **要求**: 能够发送邮件的邮箱账号

---

### 2. 必需配置

#### A. 获取SMTP凭证（以Gmail为例）

**步骤1: 启用两步验证**
1. 访问 https://myaccount.google.com/security
2. 找到"两步验证"并开启

**步骤2: 生成应用专用密码**
1. 访问 https://myaccount.google.com/apppasswords
2. 选择"邮件" → "其他（自定义名称）"
3. 输入名称（如"CCF提醒系统"）
4. 点击"生成"
5. 复制生成的16位密码（格式：`xxxx xxxx xxxx xxxx`）

**步骤3: 记录配置信息**
- SMTP服务器: `smtp.gmail.com`
- SMTP端口: `587`
- 邮箱账号: `your_email@gmail.com`
- 应用密码: `xxxx xxxx xxxx xxxx`（刚才生成的）

#### B. 其他邮箱服务商配置

**QQ邮箱**
- SMTP服务器: `smtp.qq.com`
- SMTP端口: `587` (TLS) 或 `465` (SSL)
- 获取授权码: 邮箱设置 → 账户 → 开启SMTP服务 → 生成授权码

**163邮箱**
- SMTP服务器: `smtp.163.com`
- SMTP端口: `465` (SSL) 或 `25`
- 获取授权码: 邮箱设置 → POP3/SMTP/IMAP → 开启SMTP服务

**Outlook/Hotmail**
- SMTP服务器: `smtp-mail.outlook.com`
- SMTP端口: `587`

---

### 3. 配置方式（二选一）

#### 方式一：本地配置文件（用于本地运行）

编辑 `config.json` 文件：

```json
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_user": "your_email@gmail.com",
  "smtp_password": "应用密码（去掉空格）",
  "from_email": "your_email@gmail.com",
  "from_name": "CCF会议提醒助手",
  "to_emails": "recipient@example.com,recipient2@example.com"
}
```

**注意事项**:
- `smtp_password` 填写应用密码时，去掉中间的空格
- `to_emails` 多个收件人用逗号分隔
- ⚠️ **重要**: 不要将 `config.json` 提交到公共仓库

#### 方式二：环境变量（用于GitHub Actions）

1. **创建GitHub仓库**并推送代码
2. **配置GitHub Secrets**:

   在GitHub仓库页面:
   - Settings → Secrets and variables → Actions
   - 点击 "New repository secret"
   - 添加以下Secrets:

   | Secret名称 | 值 | 说明 |
   |-----------|---|------|
   | `SMTP_SERVER` | `smtp.gmail.com` | SMTP服务器地址 |
   | `SMTP_PORT` | `587` | SMTP端口 |
   | `SMTP_USER` | `your_email@gmail.com` | 邮箱账号 |
   | `SMTP_PASSWORD` | `应用密码（无空格）` | 应用专用密码 |
   | `FROM_EMAIL` | `your_email@gmail.com` | 发件人邮箱 |
   | `TO_EMAILS` | `recipient@example.com,recipient2@example.com` | 收件人邮箱 |

---

### 4. 运行方式（二选一）

#### 方式一：本地运行

**直接运行**:
```bash
python email_sender.py
```

**自定义查询天数**:
```bash
# 查询未来60天内的截止日期
python email_sender.py --days 60

# 查询未来7天内的截止日期
python email_sender.py -d 7
```

**Windows定时任务**:
1. 创建 `run_email_reminder.bat`:
   ```batch
   @echo off
   cd /d D:\AI\cc+glm\submit_paper
   python email_sender.py --days 30
   pause
   ```

2. 打开任务计划程序（Win+R，输入 `taskschd.msc`）
3. 创建基本任务 → 设置每周一上午9点运行
4. 选择刚才创建的 `.bat` 文件

#### 方式二：GitHub Actions自动化（推荐）

**优势**:
- ✅ 免费
- ✅ 无需服务器
- ✅ 自动运行
- ✅ 运行日志可查看

**步骤**:
1. 将代码推送到GitHub仓库
2. 按照上面"方式二"配置GitHub Secrets
3. 推送代码后自动运行（每周一上午9点）
4. 可在 Actions 标签页手动触发或查看运行日志

---

### 5. 测试配置

**本地测试**:
```bash
# 测试是否能正常发送邮件
python email_sender.py --days 30
```

**GitHub Actions测试**:
1. 在GitHub仓库页面，点击 "Actions" 标签
2. 选择 "CCF会议截止日期提醒" 工作流
3. 点击 "Run workflow" 手动触发
4. 查看运行日志确认是否成功

---

### 6. 维护建议

**定期更新会议信息**:
- 访问 https://ccfddl.top/ 获取最新截止日期
- 编辑 `conferences.json` 更新会议信息
- 提交更新到仓库

**检查邮件发送状态**:
- 本地运行: 查看控制台输出
- GitHub Actions: 在 Actions 标签页查看运行日志

---

### 7. 常见问题

**Q1: 提示认证失败**
- 确认已启用两步验证
- 确认使用的是应用专用密码，不是登录密码
- 检查应用密码是否正确（去掉空格）

**Q2: 找不到应用密码生成入口**
- 先启用两步验证，才能看到应用密码选项
- 访问: https://myaccount.google.com/apppasswords

**Q3: GitHub Actions运行失败**
- 检查所有Secrets是否正确配置
- 在Actions页面查看详细错误日志
- 确认 `conferences.json` 和 `email_sender.py` 已提交

**Q4: 邮件未收到**
- 检查垃圾邮件文件夹
- 确认收件人邮箱地址正确
- 查看发送程序是否成功执行

---

### 8. 资源清单

**必需资源**:
- ✅ Python 3.7+
- ✅ 邮箱账号（Gmail推荐）
- ✅ 应用专用密码

**可选资源**:
- ⭐ GitHub账号（用于GitHub Actions自动化）
- ⭐ Windows/Linux系统（用于本地定时任务）

**无需资源**:
- ❌ 无需购买服务器
- ❌ 无需安装第三方Python包
- ❌ 无需数据库

---

### 9. 快速开始检查清单

- [ ] 已安装Python 3.7+
- [ ] 已有邮箱账号
- [ ] 已启用两步验证（Gmail）
- [ ] 已生成应用专用密码
- [ ] 已编辑 `config.json` 配置文件
- [ ] 已测试运行 `python email_sender.py`
- [ ] 已成功收到测试邮件
- [ ] （可选）已配置GitHub Actions自动化
- [ ] （可选）已设置定时任务

---

## 配置完成！

现在您可以：
1. 本地运行: `python email_sender.py`
2. 配置自动化: 设置GitHub Actions或系统定时任务
3. 定期更新会议信息: 编辑 `conferences.json`

如有问题，请参考 `README.md` 或查看运行日志。
