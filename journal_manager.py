#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
期刊数据管理器 - 管理期刊数据
继承ConferenceManager，添加期刊特有功能
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# 导入会议管理器
from conference_manager import ConferenceManager

# Windows控制台编码修复
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)


class JournalManager(ConferenceManager):
    """期刊数据管理器 - 继承会议管理器"""

    # 期刊出版周期类型
    PUBLICATION_TYPES = {
        'weekly': '周刊',
        'monthly': '月刊',
        'bimonthly': '双月刊',
        'quarterly': '季刊',
        'annual': '年刊',
        'irregular': '不定期'
    }

    def __init__(self, data_file: str = 'journals.json'):
        """初始化期刊管理器

        Args:
            data_file: 期刊数据文件路径
        """
        # 调用父类初始化
        super().__init__(data_file)
        self.data_file = data_file

    def add_journal(self, journal: Dict, source_id: str = 'manual') -> bool:
        """添加期刊

        Args:
            journal: 期刊数据
            source_id: 数据源ID

        Returns:
            是否添加成功
        """
        try:
            # 确保type字段为journal
            journal['type'] = 'journal'

            # 生成ID（如果没有）
            if 'id' not in journal:
                journal['id'] = self._generate_journal_id(journal)

            # 添加验证信息
            if 'verification' not in journal:
                journal['verification'] = {
                    'status': 'unverified',
                    'sources': [{
                        'source_id': source_id,
                        'last_checked': datetime.now().strftime('%Y-%m-%d'),
                        'data': {k: v for k, v in journal.items()
                                if k not in ['verification', 'metadata']}
                    }],
                    'conflicts': [],
                    'confidence': 0.5
                }

            # 添加元数据
            if 'metadata' not in journal:
                journal['metadata'] = {
                    'created_at': datetime.now().strftime('%Y-%m-%d'),
                    'updated_at': datetime.now().strftime('%Y-%m-%d'),
                    'updated_by': source_id
                }

            # 检查是否已存在
            existing = self.find_conference(journal['id'])
            if existing:
                print(f"⚠️  期刊已存在: {journal['name']}")
                return False

            self.conferences.append(journal)
            print(f"✅ 已添加期刊: {journal['name']}")
            return True

        except Exception as e:
            print(f"❌ 添加期刊失败: {e}")
            return False

    def _generate_journal_id(self, journal: Dict) -> str:
        """生成期刊唯一ID

        Args:
            journal: 期刊数据

        Returns:
            唯一ID
        """
        # 优先使用缩写
        abbrev = journal.get('abbrev', '')
        if not abbrev:
            # 如果没有缩写，从名称提取
            name = journal.get('name', '')
            # 提取首字母缩写（通常是大写）
            words = name.split()
            if len(words) >= 2:
                # 取每个单词的首字母
                abbrev = ''.join([w[0].upper() for w in words[:4] if w])
            else:
                abbrev = name[:10].upper()

        # 清理缩写
        abbrev = re.sub(r'[^A-Z]', '', abbrev).lower()

        return f"{abbrev}"

    def get_upcoming_deadlines(self, days_ahead: int = 30) -> List[Dict]:
        """获取即将截稿的期刊

        对于期刊，由于通常是rolling submission，我们根据出版周期估算提醒时间

        Args:
            days_ahead: 查询未来多少天内的截止日期

        Returns:
            即将截稿的期刊列表
        """
        upcoming = []
        today = datetime.now()

        for journal in self.conferences:
            deadline_str = journal.get('deadline')
            if not deadline_str:
                continue

            try:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
                days_until = (deadline - today).days

                if 0 <= days_until <= days_ahead:
                    journal['days_until'] = days_until
                    journal['deadline_date'] = deadline
                    upcoming.append(journal)
            except ValueError:
                continue

        # 按截止日期排序
        upcoming.sort(key=lambda x: x['deadline_date'])
        return upcoming

    def get_statistics(self) -> Dict:
        """获取统计信息（扩展父类方法）

        Returns:
            统计信息字典
        """
        stats = super().get_statistics()

        # 添加期刊特有统计
        stats['by_publication_type'] = {}
        for journal in self.conferences:
            pub_type = journal.get('publication_frequency', 'unknown')
            stats['by_publication_type'][pub_type] = \
                stats['by_publication_type'].get(pub_type, 0) + 1

        # 影响因子统计
        impact_factors = [
            j.get('impact_factor', 0)
            for j in self.conferences
            if j.get('impact_factor')
        ]

        if impact_factors:
            stats['impact_factor_stats'] = {
                'max': max(impact_factors),
                'min': min(impact_factors),
                'avg': sum(impact_factors) / len(impact_factors),
                'count': len(impact_factors)
            }

        return stats

    def filter_by_impact_factor(self, min_if: float = 0.0,
                                max_if: float = 100.0) -> List[Dict]:
        """按影响因子筛选期刊

        Args:
            min_if: 最低影响因子
            max_if: 最高影响因子

        Returns:
            符合条件的期刊列表
        """
        filtered = []
        for journal in self.conferences:
            if_factor = journal.get('impact_factor', 0)
            if min_if <= if_factor <= max_if:
                filtered.append(journal)

        return filtered

    def get_top_journals(self, n: int = 10, by: str = 'impact_factor') -> List[Dict]:
        """获取Top期刊

        Args:
            n: 返回数量
            by: 排序依据（impact_factor/citations/h_index）

        Returns:
            Top期刊列表
        """
        if by == 'impact_factor':
            key_func = lambda x: x.get('impact_factor', 0)
        elif by == 'citations':
            key_func = lambda x: x.get('citations', 0)
        elif by == 'h_index':
            key_func = lambda x: x.get('h_index', 0)
        else:
            key_func = lambda x: x.get('impact_factor', 0)

        # 过滤有该指标的期刊并排序
        filtered = [
            j for j in self.conferences
            if j.get(by) is not None
        ]

        sorted_journals = sorted(
            filtered,
            key=key_func,
            reverse=True
        )

        return sorted_journals[:n]


def create_sample_journals() -> List[Dict]:
    """创建示例期刊数据

    Returns:
        期刊数据列表
    """
    journals = [
        # AI/ML 期刊
        {
            "name": "IEEE Transactions on Pattern Analysis and Machine Intelligence",
            "abbrev": "TPAMI",
            "rank": "A",
            "publisher": "IEEE",
            "issn": "0162-8828",
            "deadline": "2026-02-15",
            "publication_frequency": "monthly",
            "website": "https://www.computer.org/csdl/journal/tp",
            "description": "模式分析与机器智能汇刊，CCF A类",
            "fields": ["计算机视觉", "机器学习", "人工智能"],
            "impact_factor": 24.3,
            "h_index": 280,
            "submission_types": ["regular_paper"]
        },
        {
            "name": "Journal of Machine Learning Research",
            "abbrev": "JMLR",
            "rank": "A",
            "publisher": "MIT Press",
            "issn": "1532-4435",
            "deadline": "2026-03-01",
            "publication_frequency": "monthly",
            "website": "https://www.jmlr.org/",
            "description": "机器学习研究期刊，CCF A类",
            "fields": ["机器学习", "人工智能", "理论计算机"],
            "impact_factor": 6.0,
            "h_index": 195,
            "submission_types": ["regular_paper"]
        },
        {
            "name": "IEEE Transactions on Neural Networks and Learning Systems",
            "abbrev": "TNNLS",
            "rank": "A",
            "publisher": "IEEE",
            "issn": "2162-237X",
            "deadline": "2026-02-20",
            "publication_frequency": "monthly",
            "website": "https://www.ieee.org/",
            "description": "神经网络与学习系统汇刊，CCF A类",
            "fields": ["神经网络", "深度学习", "人工智能"],
            "impact_factor": 14.3,
            "h_index": 210,
            "submission_types": ["regular_paper", "letter"]
        },
        # 数据库期刊
        {
            "name": "ACM Transactions on Database Systems",
            "abbrev": "TODS",
            "rank": "A",
            "publisher": "ACM",
            "issn": "0362-5915",
            "deadline": "2026-03-15",
            "publication_frequency": "quarterly",
            "website": "https://dl.acm.org/journal/tods",
            "description": "数据库系统汇刊，CCF A类",
            "fields": ["数据库", "数据管理", "信息系统"],
            "impact_factor": 3.5,
            "h_index": 120,
            "submission_types": ["regular_paper"]
        },
        {
            "name": "IEEE Transactions on Knowledge and Data Engineering",
            "abbrev": "TKDE",
            "rank": "A",
            "publisher": "IEEE",
            "issn": "1041-4347",
            "deadline": "2026-03-01",
            "publication_frequency": "monthly",
            "website": "https://www.computer.org/csdl/journal/tkde",
            "description": "知识与数据工程汇刊，CCF A类",
            "fields": ["数据库", "数据挖掘", "机器学习"],
            "impact_factor": 8.9,
            "h_index": 185,
            "submission_types": ["regular_paper"]
        },
        {
            "name": "VLDB Journal",
            "abbrev": "VLDB J.",
            "rank": "A",
            "publisher": "Springer",
            "issn": "1066-8888",
            "deadline": "2026-04-01",
            "publication_frequency": "bimonthly",
            "website": "https://link.springer.com/journal/10678",
            "description": "超大型数据库期刊，CCF A类",
            "fields": ["数据库", "大数据", "数据管理"],
            "impact_factor": 4.5,
            "h_index": 130,
            "submission_types": ["regular_paper"]
        },
        # 网络期刊
        {
            "name": "IEEE/ACM Transactions on Networking",
            "abbrev": "TON",
            "rank": "A",
            "publisher": "IEEE/ACM",
            "issn": "1063-6692",
            "deadline": "2026-02-28",
            "publication_frequency": "bimonthly",
            "website": "https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=71",
            "description": "网络汇刊，CCF A类",
            "fields": ["计算机网络", "通信", "网络协议"],
            "impact_factor": 5.8,
            "h_index": 165,
            "submission_types": ["regular_paper"]
        },
        # 安全期刊
        {
            "name": "IEEE Transactions on Information Forensics and Security",
            "abbrev": "TIFS",
            "rank": "A",
            "publisher": "IEEE",
            "issn": "1556-6013",
            "deadline": "2026-03-10",
            "publication_frequency": "monthly",
            "website": "https://www.ieee.org/",
            "description": "信息取证与安全汇刊，CCF A类",
            "fields": ["信息安全", "密码学", "数字取证"],
            "impact_factor": 7.2,
            "h_index": 140,
            "submission_types": ["regular_paper"]
        },
        {
            "name": "ACM Transactions on Privacy and Security",
            "abbrev": "TAPS",
            "rank": "A",
            "publisher": "ACM",
            "issn": "2471-2566",
            "deadline": "2026-03-20",
            "publication_frequency": "quarterly",
            "website": "https://dl.acm.org/journal/taps",
            "description": "隐私与安全汇刊，CCF A类",
            "fields": ["网络安全", "隐私保护", "系统安全"],
            "impact_factor": 3.5,
            "h_index": 85,
            "submission_types": ["regular_paper"]
        },
        {
            "name": "Journal of Cryptology",
            "abbrev": "J. Cryptol.",
            "rank": "A",
            "publisher": "Springer",
            "issn": "0933-2790",
            "deadline": "2026-04-15",
            "publication_frequency": "bimonthly",
            "website": "https://link.springer.com/journal/145",
            "description": "密码学期刊，CCF A类",
            "fields": ["密码学", "理论计算机", "网络安全"],
            "impact_factor": 2.8,
            "h_index": 75,
            "submission_types": ["regular_paper"]
        },
        # 软件工程期刊
        {
            "name": "IEEE Transactions on Software Engineering",
            "abbrev": "TSE",
            "rank": "A",
            "publisher": "IEEE",
            "issn": "0098-5589",
            "deadline": "2026-03-05",
            "publication_frequency": "monthly",
            "website": "https://www.computer.org/csdl/journal/tse",
            "description": "软件工程汇刊，CCF A类",
            "fields": ["软件工程", "编程语言", "软件测试"],
            "impact_factor": 6.2,
            "h_index": 155,
            "submission_types": ["regular_paper"]
        },
        {
            "name": "ACM Transactions on Software Engineering and Methodology",
            "abbrev": "TOSEM",
            "rank": "B",
            "publisher": "ACM",
            "issn": "1049-331X",
            "deadline": "2026-03-25",
            "publication_frequency": "quarterly",
            "website": "https://dl.acm.org/journal/tosem",
            "description": "软件工程与方法论汇刊，CCF B类",
            "fields": ["软件工程", "软件方法论", "软件开发"],
            "impact_factor": 3.5,
            "h_index": 95,
            "submission_types": ["regular_paper"]
        },
        # 理论计算机期刊
        {
            "name": "Journal of the ACM",
            "abbrev": "JACM",
            "rank": "A",
            "publisher": "ACM",
            "issn": "0004-5411",
            "deadline": "2026-04-01",
            "publication_frequency": "bimonthly",
            "website": "https://dl.acm.org/journal/jacm",
            "description": "ACM期刊，理论计算机顶刊，CCF A类",
            "fields": ["理论计算机", "算法", "计算复杂性"],
            "impact_factor": 3.5,
            "h_index": 130,
            "submission_types": ["regular_paper"]
        },
        {
            "name": "SIAM Journal on Computing",
            "abbrev": "SICOMP",
            "rank": "A",
            "publisher": "SIAM",
            "issn": "0097-5397",
            "deadline": "2026-03-30",
            "publication_frequency": "bimonthly",
            "website": "https://epubs.siam.org/journal/sjcomp",
            "description": "SIAM计算期刊，CCF A类",
            "fields": ["理论计算机", "算法", "数学"],
            "impact_factor": 2.5,
            "h_index": 110,
            "submission_types": ["regular_paper"]
        },
        # HCI期刊
        {
            "name": "ACM Transactions on Computer-Human Interaction",
            "abbrev": "TOCHI",
            "rank": "A",
            "publisher": "ACM",
            "issn": "1073-0516",
            "deadline": "2026-04-10",
            "publication_frequency": "quarterly",
            "website": "https://dl.acm.org/journal/tochi",
            "description": "人机交互汇刊，CCF A类",
            "fields": ["人机交互", "用户界面", "用户体验"],
            "impact_factor": 4.8,
            "h_index": 125,
            "submission_types": ["regular_paper"]
        },
        # 系统期刊
        {
            "name": "ACM Transactions on Computer Systems",
            "abbrev": "TOCS",
            "rank": "A",
            "publisher": "ACM",
            "issn": "0734-2071",
            "deadline": "2026-03-15",
            "publication_frequency": "quarterly",
            "website": "https://dl.acm.org/journal/tocs",
            "description": "计算机系统汇刊，CCF A类",
            "fields": ["操作系统", "分布式系统", "计算机架构"],
            "impact_factor": 3.2,
            "h_index": 105,
            "submission_types": ["regular_paper"]
        },
        # 计算机视觉
        {
            "name": "International Journal of Computer Vision",
            "abbrev": "IJCV",
            "rank": "A",
            "publisher": "Springer",
            "issn": "0920-5691",
            "deadline": "2026-03-20",
            "publication_frequency": "monthly",
            "website": "https://link.springer.com/journal/11263",
            "description": "国际计算机视觉期刊，CCF A类",
            "fields": ["计算机视觉", "图像处理", "模式识别"],
            "impact_factor": 19.5,
            "h_index": 220,
            "submission_types": ["regular_paper"]
        }
    ]

    return journals


def main():
    """主函数 - 命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description='期刊数据管理工具')
    parser.add_argument('--file', type=str, default='journals.json',
                       help='期刊数据文件 (默认: journals.json)')
    parser.add_argument('--stats', action='store_true',
                       help='显示统计信息')
    parser.add_argument('--top', type=int, default=10,
                       help='显示TopN期刊 (默认: 10)')
    parser.add_argument('--by', choices=['impact_factor', 'citations', 'h_index'],
                       default='impact_factor',
                       help='排序依据 (默认: impact_factor)')
    parser.add_argument('--init', action='store_true',
                       help='初始化期刊数据库（创建示例数据）')
    parser.add_argument('--filter-if', type=float, nargs=2, metavar=('MIN', 'MAX'),
                       help='按影响因子筛选')

    args = parser.parse_args()

    print("="*60)
    print("📚 期刊数据管理工具")
    print("="*60)

    # 初始化数据
    if args.init:
        print("\n📝 正在初始化期刊数据库...")
        manager = JournalManager(args.file)

        sample_journals = create_sample_journals()
        print(f"   准备添加 {len(sample_journals)} 个期刊...")

        for journal in sample_journals:
            manager.add_journal(journal)

        manager.save_data()
        print("\n✅ 期刊数据库初始化完成！")
        return 0

    # 创建管理器
    manager = JournalManager(args.file)

    # 如果文件不存在且未初始化
    if not os.path.exists(args.file):
        print(f"\n⚠️  期刊数据文件不存在: {args.file}")
        print("   请先运行: python journal_manager.py --init")
        return 1

    # 显示统计信息
    if args.stats:
        stats = manager.get_statistics()
        print(f"\n📊 数据统计:")
        print(f"   总数: {stats['total']}")
        print(f"   按等级: A={stats['by_rank']['A']}, "
              f"B={stats['by_rank']['B']}, C={stats['by_rank']['C']}")
        print(f"   按出版周期: {stats['by_publication_type']}")

        if 'impact_factor_stats' in stats:
            if_stats = stats['impact_factor_stats']
            print(f"   影响因子: 最高={if_stats['max']:.1f}, "
                  f"最低={if_stats['min']:.1f}, 平均={if_stats['avg']:.1f}")

        print(f"   即将截止(30天): {stats['upcoming_30days']}")
        print(f"   最后更新: {stats['last_updated']}")

    # 显示Top期刊
    if args.top:
        print(f"\n🏆 Top {args.top} 期刊（按{args.by}）:")
        top_journals = manager.get_top_journals(args.top, args.by)

        for i, journal in enumerate(top_journals, 1):
            name = journal.get('abbrev', journal.get('name', 'Unknown'))
            value = journal.get(args.by, 0)
            print(f"   {i:2d}. {name:15s} - {value:.1f}")

    # 按影响因子筛选
    if args.filter_if:
        min_if, max_if = args.filter_if
        print(f"\n🔍 影响因子在 {min_if}-{max_if} 之间的期刊:")
        filtered = manager.filter_by_impact_factor(min_if, max_if)

        for journal in filtered[:10]:  # 只显示前10个
            name = journal.get('abbrev', journal.get('name', 'Unknown'))
            if_factor = journal.get('impact_factor', 0)
            print(f"   - {name:15s}: {if_factor:.1f}")

        print(f"   总计: {len(filtered)} 个期刊")

    print("="*60)
    return 0


if __name__ == '__main__':
    sys.exit(main())
