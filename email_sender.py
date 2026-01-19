#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CCF论文投稿截止日期邮件提醒程序
自动发送CCF会议投稿截止日期信息到指定邮箱
"""

import smtplib
import json
import os
import sys
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from typing import List, Dict
import argparse

# Windows控制台编码修复
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())


class CCFDeadlineEmailer:
    """CCF会议截止日期邮件发送器"""

    def __init__(self, config_file: str = "config.json"):
        """初始化邮件发送器

        Args:
            config_file: 配置文件路径
        """
        self.load_config(config_file)
        self.load_conferences()

    def load_config(self, config_file: str):
        """加载配置文件"""
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 邮件服务器配置
        self.smtp_server = os.getenv('SMTP_SERVER', config.get('smtp_server'))
        self.smtp_port = int(os.getenv('SMTP_PORT', config.get('smtp_port', 587)))
        self.smtp_user = os.getenv('SMTP_USER', config.get('smtp_user'))
        self.smtp_password = os.getenv('SMTP_PASSWORD', config.get('smtp_password'))

        # 发件人和收件人
        self.from_email = os.getenv('FROM_EMAIL', config.get('from_email'))
        self.from_name = os.getenv('FROM_NAME', config.get('from_name', 'CCF会议提醒'))
        self.to_emails = os.getenv('TO_EMAILS', config.get('to_emails', ''))

        if isinstance(self.to_emails, str):
            self.to_emails = [email.strip() for email in self.to_emails.split(',') if email.strip()]

        # 验证必需配置
        if not all([self.smtp_server, self.smtp_user, self.smtp_password, self.from_email]):
            raise ValueError("缺少必需的邮件配置信息")

    def load_conferences(self):
        """加载会议信息"""
        with open('conferences.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.conferences = data.get('conferences', [])

    def get_upcoming_deadlines(self, days_ahead: int = 30) -> List[Dict]:
        """获取即将到来的截止日期

        Args:
            days_ahead: 查询未来多少天内的截止日期

        Returns:
            即将截止的会议列表
        """
        today = datetime.now()
        upcoming = []

        for conf in self.conferences:
            deadline_str = conf.get('deadline')
            if not deadline_str:
                continue

            try:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
                days_until = (deadline - today).days

                if 0 <= days_until <= days_ahead:
                    conf['days_until'] = days_until
                    conf['deadline_date'] = deadline
                    upcoming.append(conf)
            except ValueError:
                continue

        # 按截止日期排序
        upcoming.sort(key=lambda x: x['deadline_date'])
        return upcoming

    def generate_email_content(self, upcoming: List[Dict]) -> str:
        """生成邮件内容

        Args:
            upcoming: 即将截止的会议列表

        Returns:
            HTML格式的邮件内容
        """
        today = datetime.now().strftime('%Y年%m月%d日')

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 28px; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
        .content {{ background: #f9f9f9; padding: 20px; border-radius: 10px; margin-top: 20px; }}
        .conference {{ background: white; padding: 20px; margin: 15px 0; border-left: 4px solid #667eea; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .conference.urgent {{ border-left-color: #e74c3c; }}
        .conference.moderate {{ border-left-color: #f39c12; }}
        .conference-name {{ font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 10px; }}
        .ccf-rank {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; margin-left: 10px; }}
        .ccf-a {{ background: #e74c3c; color: white; }}
        .ccf-b {{ background: #3498db; color: white; }}
        .ccf-c {{ background: #2ecc71; color: white; }}
        .info-row {{ display: flex; margin: 8px 0; }}
        .info-label {{ font-weight: bold; color: #7f8c8d; width: 120px; }}
        .info-value {{ color: #2c3e50; }}
        .deadline {{ font-size: 18px; color: #e74c3c; font-weight: bold; }}
        .days-count {{ background: #667eea; color: white; padding: 5px 15px; border-radius: 20px; font-size: 14px; margin-left: 10px; }}
        .footer {{ text-align: center; margin-top: 30px; padding: 20px; color: #7f8c8d; font-size: 14px; }}
        .no-deadlines {{ text-align: center; padding: 40px; color: #7f8c8d; }}
        .section-title {{ font-size: 18px; font-weight: bold; margin: 20px 0 15px 0; color: #2c3e50; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 CCF会议投稿截止提醒</h1>
            <p>{today} 汇总</p>
        </div>

        <div class="content">
        """

        if not upcoming:
            html += """
            <div class="no-deadlines">
                <h2>🎉 未来30天没有即将截止的CCF会议</h2>
                <p>您可以安心休息，或开始准备下一个季度的投稿！</p>
            </div>
            """
        else:
            # 按紧急程度分组
            urgent = [c for c in upcoming if c['days_until'] <= 7]
            moderate = [c for c in upcoming if 7 < c['days_until'] <= 15]
            normal = [c for c in upcoming if c['days_until'] > 15]

            if urgent:
                html += '<div class="section-title">🔥 紧急（7天内截止）</div>'
                for conf in urgent:
                    html += self._render_conference(conf, 'urgent')

            if moderate:
                html += '<div class="section-title">⚠️ 需关注（15天内截止）</div>'
                for conf in moderate:
                    html += self._render_conference(conf, 'moderate')

            if normal:
                html += '<div class="section-title">📅 即将到来</div>'
                for conf in normal:
                    html += self._render_conference(conf, '')

        html += f"""
        </div>

        <div class="footer">
            <p>💡 更多会议信息请访问：<a href="https://ccfddl.top/">CCF Conference Deadlines</a></p>
            <p>📧 如需取消订阅，请回复此邮件</p>
            <p style="margin-top: 10px;">---<br>本邮件由CCF会议提醒系统自动发送</p>
        </div>
    </div>
</body>
</html>
        """

        return html

    def _render_conference(self, conf: Dict, urgency: str) -> str:
        """渲染单个会议信息

        Args:
            conf: 会议信息字典
            urgency: 紧急程度标识

        Returns:
            HTML字符串
        """
        deadline_str = conf['deadline_date'].strftime('%Y年%m月%d日')
        days_text = f"还剩 {conf['days_until']} 天" if conf['days_until'] > 0 else "今天截止"

        rank_class = f"ccf-{conf.get('rank', 'C').lower()}"

        html = f"""
        <div class="conference {urgency}">
            <div class="conference-name">
                {conf['name']}
                <span class="ccf-rank {rank_class}">CCF-{conf.get('rank', 'C')}</span>
            </div>
            <div class="info-row">
                <span class="info-label">投稿截止：</span>
                <span class="info-value deadline">
                    {deadline_str}
                    <span class="days-count">{days_text}</span>
                </span>
            </div>
        """

        if conf.get('conference_date'):
            html += f"""
            <div class="info-row">
                <span class="info-label">会议日期：</span>
                <span class="info-value">{conf['conference_date']}</span>
            </div>
            """

        if conf.get('website'):
            html += f"""
            <div class="info-row">
                <span class="info-label">官方网站：</span>
                <span class="info-value"><a href="{conf['website']}">{conf['website']}</a></span>
            </div>
            """

        if conf.get('description'):
            html += f"""
            <div class="info-row">
                <span class="info-label">简介：</span>
                <span class="info-value">{conf['description']}</span>
            </div>
            """

        html += "</div>"
        return html

    def send_email(self, subject: str, content: str):
        """发送邮件

        Args:
            subject: 邮件主题
            content: 邮件内容（HTML格式）
        """
        # 创建邮件
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        # 163邮箱要求From地址必须与登录账号完全一致
        msg['From'] = self.from_email
        msg['To'] = ', '.join(self.to_emails)

        # 添加HTML内容
        html_part = MIMEText(content, 'html', 'utf-8')
        msg.attach(html_part)

        # 发送邮件
        try:
            # 根据端口选择SMTP或SMTP_SSL
            # 465端口使用SSL，587/25端口使用TLS
            if self.smtp_port == 465:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                if self.smtp_port == 587:
                    server.starttls()

            # 开启调试模式，查看详细通信日志
            server.set_debuglevel(1)
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
            server.quit()
            print(f"✅ 邮件发送成功！收件人: {', '.join(self.to_emails)}")
        except Exception as e:
            print(f"❌ 邮件发送失败: {str(e)}")
            raise

    def run(self, days_ahead: int = 30, recipients=None):
        """运行邮件发送流程

        Args:
            days_ahead: 查询未来多少天内的截止日期
            recipients: 收件人列表（可选），如果不指定则使用配置中的收件人
        """
        print(f"🔍 正在查找未来 {days_ahead} 天内的CCF会议截止日期...")

        upcoming = self.get_upcoming_deadlines(days_ahead)

        if upcoming:
            print(f"📊 找到 {len(upcoming)} 个即将截止的会议")
            for conf in upcoming:
                print(f"   - {conf['name']} (CCF-{conf.get('rank', 'C')}): {conf['days_until']} 天后截止")
        else:
            print("📭 未来30天没有即将截止的会议")

        subject = f"📚 CCF会议投稿截止提醒 - {datetime.now().strftime('%Y-%m-%d')}"
        content = self.generate_email_content(upcoming)

        # 使用指定的收件人或配置中的收件人
        to_emails = recipients if recipients else self.to_emails

        if isinstance(to_emails, str):
            to_emails = [to_emails]

        print(f"\n📧 正在发送邮件给 {len(to_emails)} 个收件人...")
        success_count = 0
        fail_count = 0

        for i, email in enumerate(to_emails, 1):
            try:
                print(f"\n[{i}/{len(to_emails)}] 发送给 {email}...")
                # 临时修改收件人
                original_to_emails = self.to_emails
                self.to_emails = [email]

                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = self.from_email
                msg['To'] = email
                html_part = MIMEText(content, 'html', 'utf-8')
                msg.attach(html_part)

                # 发送邮件
                if self.smtp_port == 465:
                    server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
                else:
                    server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                    if self.smtp_port == 587:
                        server.starttls()

                server.set_debuglevel(0)
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
                server.quit()
                print(f"   ✅ 发送成功")
                success_count += 1

                # 恢复原收件人列表
                self.to_emails = original_to_emails

            except Exception as e:
                print(f"   ❌ 发送失败: {str(e)}")
                fail_count += 1

        print(f"\n{'='*60}")
        print(f"📊 发送统计：成功 {success_count} 个，失败 {fail_count} 个")
        print(f"{'='*60}\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='CCF会议截止日期邮件提醒')
    parser.add_argument('-d', '--days', type=int, default=30,
                        help='查询未来多少天内的截止日期 (默认: 30)')
    parser.add_argument('-c', '--config', type=str, default='config.json',
                        help='配置文件路径 (默认: config.json)')
    parser.add_argument('--customers', action='store_true',
                        help='从customers.json读取客户列表并发送')

    args = parser.parse_args()

    try:
        emailer = CCFDeadlineEmailer(args.config)

        # 如果指定了--customers参数，从customers.json读取客户列表
        if args.customers:
            try:
                with open('customers.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    customers = [c for c in data.get('customers', []) if c.get('enabled', True)]
                    customer_emails = [c['email'] for c in customers]

                if not customer_emails:
                    print("❌ 没有启用的客户邮箱")
                    return 1

                print(f"📋 从customers.json读取到 {len(customer_emails)} 个启用的客户")
                emailer.run(days_ahead=args.days, recipients=customer_emails)
            except FileNotFoundError:
                print("❌ 未找到customers.json文件")
                print("   请先使用 manage_customers.py 添加客户")
                return 1
        else:
            emailer.run(days_ahead=args.days)

    except Exception as e:
        print(f"❌ 程序执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
