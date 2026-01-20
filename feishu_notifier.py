#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CCF论文投稿截止日期飞书机器人提醒程序
通过飞书自定义机器人webhook发送会议截止日期提醒
"""

import json
import sys
import argparse
from datetime import datetime
from typing import List, Dict
import urllib.request
import urllib.error

# Windows控制台编码修复
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)


class FeishuCCFNotifier:
    """飞书CCF会议截止日期通知器"""

    def __init__(self, webhook_url: str = None, data_file: str = None):
        """初始化通知器

        Args:
            webhook_url: 飞书机器人webhook地址
            data_file: 数据文件路径（默认为conferences.json）
        """
        if webhook_url is None:
            # 从配置文件读取
            with open('feishu_config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                webhook_url = config.get('webhook_url')

        if not webhook_url:
            raise ValueError("未配置飞书机器人webhook地址")

        self.webhook_url = webhook_url
        self.load_conferences(data_file)

    def load_conferences(self, data_file: str = None):
        """加载会议信息

        Args:
            data_file: 数据文件路径（默认为conferences.json）
        """
        if data_file is None:
            data_file = 'conferences.json'

        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.conferences = data.get('conferences', [])
            self.data_type = '会议' if 'conference' in data_file else '期刊'

    def filter_conferences(self, filters: Dict) -> List[Dict]:
        """筛选会议

        Args:
            filters: 筛选条件字典
                - rank: CCF等级（A/B/C）
                - field: 研究领域
                - type: 类型（conference/journal）
                - min_confidence: 最低置信度

        Returns:
            筛选后的会议列表
        """
        filtered = self.conferences

        # 按等级筛选
        if 'rank' in filters:
            rank = filters['rank'].upper()
            if ',' in rank:
                ranks = rank.split(',')
                filtered = [c for c in filtered if c.get('rank') in ranks]
            else:
                filtered = [c for c in filtered if c.get('rank') == rank]

        # 按领域筛选
        if 'field' in filters:
            field = filters['field'].lower()
            filtered = [
                c for c in filtered
                if any(field in f.lower() for f in c.get('fields', []))
            ]

        # 按类型筛选
        if 'type' in filters:
            conf_type = filters['type']
            filtered = [c for c in filtered if c.get('type', 'conference') == conf_type]

        # 按置信度筛选
        if 'min_confidence' in filters:
            min_conf = filters['min_confidence']
            filtered = [
                c for c in filtered
                if c.get('verification', {}).get('confidence', 0) >= min_conf
            ]

        return filtered

    def get_upcoming_deadlines(self, days_ahead: int = 30, filters: Dict = None) -> List[Dict]:
        """获取即将到来的截止日期

        Args:
            days_ahead: 查询未来多少天内的截止日期
            filters: 筛选条件（可选）

        Returns:
            即将截止的会议列表
        """
        # 先应用筛选
        if filters:
            conferences = self.filter_conferences(filters)
        else:
            conferences = self.conferences

        today = datetime.now()
        upcoming = []

        for conf in conferences:
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

    def generate_card_content(self, upcoming: List[Dict]) -> dict:
        """生成飞书卡片消息内容

        Args:
            upcoming: 即将截止的会议列表

        Returns:
            飞书卡片消息字典
        """
        today = datetime.now().strftime('%Y年%m月%d日')

        if not upcoming:
            # 没有即将截止的会议
            card = {
                "msg_type": "interactive",
                "card": {
                    "header": {
                        "title": {
                            "tag": "plain_text",
                            "content": "📚 CCF会议截止提醒"
                        },
                        "template": "green"
                    },
                    "elements": [
                        {
                            "tag": "div",
                            "text": {
                                "tag": "lark_md",
                                "content": f"**查询日期：** {today}\n\n"
                                          f"✅ 未来30天没有即将截止的CCF会议\n\n"
                                          f"您可以安心休息，或开始准备下一个季度的投稿！"
                            }
                        },
                        {
                            "tag": "action",
                            "actions": [
                                {
                                    "tag": "button",
                                    "text": {
                                        "tag": "plain_text",
                                        "content": "查看更多会议"
                                    },
                                    "type": "default",
                                    "url": "https://ccfddl.top/"
                                }
                            ]
                        }
                    ]
                }
            }
            return card

        # 有即将截止的会议，按紧急程度分组
        urgent = [c for c in upcoming if c['days_until'] <= 7]
        moderate = [c for c in upcoming if 7 < c['days_until'] <= 15]
        normal = [c for c in upcoming if c['days_until'] > 15]

        # 构建卡片元素
        elements = []

        # 添加统计信息
        total_text = f"**查询日期：** {today}\n\n"
        total_text += f"📊 找到 **{len(upcoming)}** 个即将截止的会议\n\n"
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": total_text
            }
        })

        # 添加会议列表
        for conf in upcoming:
            urgency_emoji = "🔥" if conf['days_until'] <= 7 else "⚠️" if conf['days_until'] <= 15 else "📅"
            rank_color = self._get_rank_color(conf.get('rank', 'C'))
            days_text = f"还剩 {conf['days_until']} 天" if conf['days_until'] > 0 else "今天截止"

            conf_text = f"\n---\n{urgency_emoji} **{conf['name']}**\n\n"
            conf_text += f"**CCF等级：** <font color='{rank_color}'>{conf.get('rank', 'C')}</font>\n"
            conf_text += f"**截止日期：** {conf['deadline_date'].strftime('%Y年%m月%d日')}\n"
            conf_text += f"**剩余时间：** {days_text}\n"

            if conf.get('conference_date'):
                conf_text += f"**会议日期：** {conf['conference_date']}\n"

            if conf.get('website'):
                conf_text += f"**官网：** [{conf['website']}]({conf['website']})\n"

            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": conf_text
                }
            })

        # 添加操作按钮
        elements.append({
            "tag": "hr"
        })
        elements.append({
            "tag": "action",
            "actions": [
                {
                    "tag": "button",
                    "text": {
                        "tag": "plain_text",
                        "content": "📚 查看更多会议"
                    },
                    "type": "primary",
                    "url": "https://ccfddl.top/"
                },
                {
                    "tag": "button",
                    "text": {
                        "tag": "plain_text",
                        "content": "🔍 CCF官网"
                    },
                    "type": "default",
                    "url": "https://www.ccf.org.cn/"
                }
            ]
        })

        # 确定卡片主题颜色
        if urgent:
            template = "red"
        elif moderate:
            template = "orange"
        else:
            template = "blue"

        card = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "📚 CCF会议截止提醒"
                    },
                    "template": template
                },
                "elements": elements
            }
        }

        return card

    def _get_rank_color(self, rank: str) -> str:
        """获取CCF等级对应的颜色

        Args:
            rank: CCF等级（A/B/C）

        Returns:
            颜色代码
        """
        colors = {
            'A': '#FF0000',
            'B': '#FF9900',
            'C': '#00CC00'
        }
        return colors.get(rank.upper(), '#999999')

    def send_message(self, content: dict):
        """发送消息到飞书

        Args:
            content: 消息内容字典
        """
        headers = {
            'Content-Type': 'application/json'
        }

        data = json.dumps(content).encode('utf-8')

        req = urllib.request.Request(
            self.webhook_url,
            data=data,
            headers=headers,
            method='POST'
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))

                if result.get('StatusCode') == 0 or result.get('code') == 0:
                    print("✅ 消息发送成功！")
                    return True
                else:
                    print(f"❌ 发送失败: {result}")
                    return False

        except urllib.error.HTTPError as e:
            error_msg = e.read().decode('utf-8')
            print(f"❌ HTTP错误: {e.code} - {error_msg}")
            return False
        except urllib.error.URLError as e:
            print(f"❌ 网络错误: {e.reason}")
            return False
        except Exception as e:
            print(f"❌ 发送失败: {e}")
            return False

    def run(self, days_ahead: int = 30, filters: Dict = None):
        """运行通知流程

        Args:
            days_ahead: 查询未来多少天内的截止日期
            filters: 筛选条件（可选）
        """
        print(f"🔍 正在查找未来 {days_ahead} 天内的{self.data_type}截止日期...")

        upcoming = self.get_upcoming_deadlines(days_ahead, filters)

        if upcoming:
            print(f"📊 找到 {len(upcoming)} 个即将截止的会议")
            for conf in upcoming:
                print(f"   - {conf['name']} (CCF-{conf.get('rank', 'C')}): {conf['days_until']} 天后截止")
        else:
            print("📭 未来30天没有即将截止的会议")

        print("\n📤 正在发送飞书消息...")
        content = self.generate_card_content(upcoming)
        success = self.send_message(content)

        if success:
            print("✅ 飞书通知发送成功！")
        else:
            print("❌ 飞书通知发送失败！")

        return success


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='CCF会议/期刊截止日期飞书提醒',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 查看未来30天的会议
  python feishu_notifier.py --days 30

  # 只查看A类会议
  python feishu_notifier.py --days 30 --rank A

  # 查看人工智能领域的会议
  python feishu_notifier.py --days 30 --field "人工智能"

  # 查看期刊（而非会议）
  python feishu_notifier.py --days 30 --type journal

  # 组合筛选：A类人工智能会议
  python feishu_notifier.py --days 30 --rank A --field "人工智能"

  # 使用期刊数据文件
  python feishu_notifier.py --days 30 --type journal --data journals.json
                                    """
    )
    parser.add_argument('-d', '--days', type=int, default=30,
                        help='查询未来多少天内的截止日期 (默认: 30)')
    parser.add_argument('-w', '--webhook', type=str, default=None,
                        help='飞书机器人webhook地址')
    parser.add_argument('--rank', type=str, choices=['A', 'B', 'C'],
                        help='筛选CCF等级 (A/B/C)')
    parser.add_argument('--field', type=str,
                        help='筛选研究领域（如：人工智能、数据库等）')
    parser.add_argument('--type', choices=['conference', 'journal', 'all'],
                        default='all',
                        help='筛选类型：conference=会议, journal=期刊, all=全部 (默认: all)')
    parser.add_argument('--data', type=str,
                        help='数据文件路径 (默认: conferences.json)')
    parser.add_argument('--min-confidence', type=float,
                        help='最低置信度 (0.0-1.0，默认不限制)')

    args = parser.parse_args()

    try:
        # 确定数据文件
        data_file = args.data if args.data else 'conferences.json'

        notifier = FeishuCCFNotifier(args.webhook, data_file)

        # 构建筛选条件
        filters = {}
        if args.rank:
            filters['rank'] = args.rank
        if args.field:
            filters['field'] = args.field
        if args.type != 'all':
            filters['type'] = args.type
        if args.min_confidence is not None:
            filters['min_confidence'] = args.min_confidence

        # 显示筛选条件
        if filters:
            print("🔍 筛选条件:")
            if 'rank' in filters:
                print(f"   等级: {filters['rank']}")
            if 'field' in filters:
                print(f"   领域: {filters['field']}")
            if 'type' in filters:
                type_name = {'conference': '会议', 'journal': '期刊'}[filters['type']]
                print(f"   类型: {type_name}")
            if 'min_confidence' in filters:
                print(f"   最低置信度: {filters['min_confidence']}")
            print()

        success = notifier.run(days_ahead=args.days, filters=filters)
        return 0 if success else 1
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
