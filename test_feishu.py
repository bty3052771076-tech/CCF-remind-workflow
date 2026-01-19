#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书机器人连接测试脚本
用于验证webhook地址是否配置正确
"""

import json
import sys
import urllib.request
import urllib.error

# Windows控制台编码修复
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())


def test_webhook(webhook_url):
    """测试飞书webhook连接

    Args:
        webhook_url: 飞书机器人webhook地址
    """
    print("=" * 60)
    print("飞书机器人连接测试")
    print("=" * 60)
    print(f"Webhook地址: {webhook_url[:50]}...")
    print("=" * 60)

    # 发送测试消息
    test_message = {
        "msg_type": "text",
        "content": {
            "text": "✅ 飞书机器人配置成功！\n\nCCF会议提醒系统已就绪。"
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }

    data = json.dumps(test_message).encode('utf-8')

    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers=headers,
        method='POST'
    )

    try:
        print("\n正在发送测试消息...")
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))

            if result.get('StatusCode') == 0 or result.get('code') == 0:
                print("\n✅ 测试成功！")
                print("\n请检查您的飞书群聊，应该能看到测试消息。")
                print("\n" + "=" * 60)
                print("🎉 配置完成！现在可以运行主程序了：")
                print("   python feishu_notifier.py --days 30")
                print("=" * 60)
                return True
            else:
                print(f"\n❌ 发送失败: {result}")
                return False

    except urllib.error.HTTPError as e:
        error_msg = e.read().decode('utf-8')
        print(f"\n❌ HTTP错误: {e.code}")
        print(f"错误详情: {error_msg}")

        if e.code == 404:
            print("\n可能的原因：")
            print("1. Webhook地址不正确")
            print("2. 机器人已被删除")
        elif e.code == 403:
            print("\n可能的原因：")
            print("1. 机器人已被禁用")
            print("2. Webhook地址已过期")

        print("\n建议：")
        print("1. 重新获取webhook地址")
        print("2. 检查机器人是否仍在群聊中")
        return False

    except urllib.error.URLError as e:
        print(f"\n❌ 网络错误: {e.reason}")
        print("\n可能的原因：")
        print("1. 网络连接问题")
        print("2. Webhook地址格式错误")
        return False

    except Exception as e:
        print(f"\n❌ 发送失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    # 尝试从配置文件读取webhook地址
    try:
        with open('feishu_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            webhook_url = config.get('webhook_url')
    except FileNotFoundError:
        print("❌ 未找到 feishu_config.json 配置文件")
        print("\n请先创建配置文件：")
        print("1. 在飞书群聊中添加自定义机器人")
        print("2. 复制webhook地址")
        print("3. 创建 feishu_config.json 文件：")
        print("""
{
  "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxxxxxxx"
}
        """)
        return 1
    except json.JSONDecodeError:
        print("❌ feishu_config.json 文件格式错误")
        return 1

    if not webhook_url:
        print("❌ 配置文件中未找到webhook_url")
        return 1

    success = test_webhook(webhook_url)
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
