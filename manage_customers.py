#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户邮箱管理脚本
用于添加、删除、查看和管理客户邮箱列表
"""

import json
import sys
from datetime import datetime

# Windows控制台编码修复
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())


class CustomerManager:
    """客户邮箱管理器"""

    def __init__(self, customers_file='customers.json'):
        """初始化管理器

        Args:
            customers_file: 客户数据文件路径
        """
        self.customers_file = customers_file
        self.load_customers()

    def load_customers(self):
        """加载客户数据"""
        try:
            with open(self.customers_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.customers = data.get('customers', [])
        except FileNotFoundError:
            print(f"⚠️  文件 {self.customers_file} 不存在，将创建新文件")
            self.customers = []
            self.save_customers()
        except json.JSONDecodeError:
            print(f"❌ 文件 {self.customers_file} 格式错误")
            self.customers = []

    def save_customers(self):
        """保存客户数据"""
        data = {
            "customers": self.customers,
            "notes": "客户邮箱列表，用于批量发送CCF会议提醒",
            "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(self.customers_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_customer(self, email, name=None):
        """添加客户

        Args:
            email: 客户邮箱
            name: 客户名称（可选）
        """
        # 检查邮箱是否已存在
        for customer in self.customers:
            if customer['email'] == email:
                print(f"⚠️  邮箱 {email} 已存在，无需重复添加")
                return False

        # 添加新客户
        customer = {
            "email": email,
            "name": name or f"客户{len(self.customers) + 1}",
            "enabled": True,
            "added_date": datetime.now().strftime('%Y-%m-%d')
        }
        self.customers.append(customer)
        self.save_customers()
        print(f"✅ 成功添加客户：{email} ({customer['name']})")
        return True

    def remove_customer(self, email):
        """删除客户

        Args:
            email: 客户邮箱
        """
        for i, customer in enumerate(self.customers):
            if customer['email'] == email:
                del self.customers[i]
                self.save_customers()
                print(f"✅ 成功删除客户：{email}")
                return True

        print(f"❌ 未找到邮箱：{email}")
        return False

    def enable_customer(self, email):
        """启用客户

        Args:
            email: 客户邮箱
        """
        for customer in self.customers:
            if customer['email'] == email:
                customer['enabled'] = True
                self.save_customers()
                print(f"✅ 已启用客户：{email}")
                return True

        print(f"❌ 未找到邮箱：{email}")
        return False

    def disable_customer(self, email):
        """禁用客户

        Args:
            email: 客户邮箱
        """
        for customer in self.customers:
            if customer['email'] == email:
                customer['enabled'] = False
                self.save_customers()
                print(f"✅ 已禁用客户：{email}")
                return True

        print(f"❌ 未找到邮箱：{email}")
        return False

    def list_customers(self):
        """列出所有客户"""
        if not self.customers:
            print("📭 客户列表为空")
            return

        print("\n" + "=" * 80)
        print("📋 客户邮箱列表")
        print("=" * 80)
        print(f"{'序号':<5} {'状态':<6} {'邮箱':<30} {'名称':<20} {'添加日期':<12}")
        print("-" * 80)

        for i, customer in enumerate(self.customers, 1):
            status = "✅启用" if customer.get('enabled', True) else "❌禁用"
            print(f"{i:<5} {status:<6} {customer['email']:<30} {customer.get('name', ''):<20} {customer.get('added_date', ''):<12}")

        print("-" * 80)
        enabled_count = sum(1 for c in self.customers if c.get('enabled', True))
        print(f"总计：{len(self.customers)} 个客户，其中 {enabled_count} 个已启用")
        print("=" * 80 + "\n")

    def get_enabled_emails(self):
        """获取所有启用的客户邮箱

        Returns:
            启用的客户邮箱列表
        """
        return [c['email'] for c in self.customers if c.get('enabled', True)]

    def get_enabled_customers(self):
        """获取所有启用的客户信息

        Returns:
            启用的客户列表
        """
        return [c for c in self.customers if c.get('enabled', True)]


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='客户邮箱管理工具')
    parser.add_argument('action', nargs='?', default='list',
                        choices=['list', 'add', 'remove', 'enable', 'disable'],
                        help='操作：list(查看), add(添加), remove(删除), enable(启用), disable(禁用)')
    parser.add_argument('--email', help='客户邮箱地址')
    parser.add_argument('--name', help='客户名称（可选，仅在添加时使用）')

    args = parser.parse_args()

    manager = CustomerManager()

    if args.action == 'list':
        manager.list_customers()

    elif args.action == 'add':
        if not args.email:
            print("❌ 请提供邮箱地址：--email xxx@qq.com")
            return 1
        manager.add_customer(args.email, args.name)

    elif args.action == 'remove':
        if not args.email:
            print("❌ 请提供邮箱地址：--email xxx@qq.com")
            return 1
        manager.remove_customer(args.email)

    elif args.action == 'enable':
        if not args.email:
            print("❌ 请提供邮箱地址：--email xxx@qq.com")
            return 1
        manager.enable_customer(args.email)

    elif args.action == 'disable':
        if not args.email:
            print("❌ 请提供邮箱地址：--email xxx@qq.com")
            return 1
        manager.disable_customer(args.email)

    return 0


if __name__ == '__main__':
    exit(main())
