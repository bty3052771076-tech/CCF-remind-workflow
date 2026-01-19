#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
163邮箱SMTP连接测试脚本
用于验证授权码是否正确
"""

import smtplib
import sys

# Windows控制台编码修复
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# 邮箱配置
SMTP_SERVER = "smtp.163.com"
SMTP_PORT = 465
EMAIL = "bty58356717@163.com"
PASSWORD = "GRR76uf6JbuGGDpV"  # 请替换为新的授权码

def test_connection():
    """测试SMTP连接和认证"""
    print("=" * 60)
    print("163邮箱SMTP连接测试")
    print("=" * 60)
    print(f"服务器: {SMTP_SERVER}")
    print(f"端口: {SMTP_PORT}")
    print(f"邮箱: {EMAIL}")
    print(f"授权码: {PASSWORD[:4]}...{PASSWORD[-4:]}")
    print("=" * 60)

    try:
        print("\n正在连接服务器...")
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        print("✅ 服务器连接成功！")

        print("\n正在验证授权码...")
        server.login(EMAIL, PASSWORD)
        print("✅ 授权码验证成功！")

        server.quit()
        print("\n" + "=" * 60)
        print("🎉 所有测试通过！配置正确！")
        print("=" * 60)
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ 认证失败: {e}")
        print("\n可能的原因：")
        print("1. 授权码不正确")
        print("2. 授权码是在开启SMTP服务之前生成的")
        print("3. 需要重新生成授权码")
        print("\n建议：")
        print("1. 登录 https://mail.163.com")
        print("2. 设置 → POP3/SMTP/IMAP")
        print("3. 确认IMAP/SMTP服务已开启")
        print("4. 删除旧授权码，重新生成新的授权码")
        print("5. 复制新的授权码并更新此脚本")
        return False

    except Exception as e:
        print(f"\n❌ 连接失败: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
