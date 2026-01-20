#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据扩展脚本 - 扩展期刊和会议数据
添加更多领域的期刊和会议
"""

import json
import sys
from journal_manager import JournalManager, create_sample_journals
from conference_manager import ConferenceManager

# Windows控制台编码修复
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)


# 扩展期刊数据
EXTENDED_JOURNALS = [
    # 网络领域
    {
        "name": "ACM SIGCOMM Computer Communication Review",
        "abbrev": "CCR",
        "rank": "B",
        "publisher": "ACM",
        "deadline": "2026-04-01",
        "publication_frequency": "quarterly",
        "website": "https://dl.acm.org/journal/ccr",
        "description": "SIGCOMM计算机通信评论",
        "fields": ["计算机网络"],
        "impact_factor": 3.2
    },
    {
        "name": "Computer Networks",
        "abbrev": "Comput. Netw.",
        "rank": "B",
        "publisher": "Elsevier",
        "deadline": "2026-03-15",
        "publication_frequency": "monthly",
        "website": "https://www.journals.elsevier.com/computer-networks",
        "description": "计算机网络期刊",
        "fields": ["计算机网络", "通信"],
        "impact_factor": 5.5
    },

    # 软件工程
    {
        "name": "Automated Software Engineering",
        "abbrev": "ASE",
        "rank": "B",
        "publisher": "Springer",
        "deadline": "2026-04-10",
        "publication_frequency": "bimonthly",
        "website": "https://link.springer.com/journal/10515",
        "description": "自动化软件工程",
        "fields": ["软件工程", "自动化"],
        "impact_factor": 3.8
    },
    {
        "name": "Empirical Software Engineering",
        "abbrev": "Empir. Softw. Eng.",
        "rank": "B",
        "publisher": "Springer",
        "deadline": "2026-04-15",
        "publication_frequency": "monthly",
        "website": "https://link.springer.com/journal/10664",
        "description": "实证软件工程",
        "fields": ["软件工程"],
        "impact_factor": 3.5
    },
    {
        "name": "Software: Practice and Experience",
        "abbrev": "Softw. Pract. Exp.",
        "rank": "C",
        "publisher": "Wiley",
        "deadline": "2026-04-20",
        "publication_frequency": "monthly",
        "website": "https://onlinelibrary.wiley.com/journal/1097024X",
        "description": "软件：实践与经验",
        "fields": ["软件工程"],
        "impact_factor": 2.1
    },

    # 理论计算机
    {
        "name": "Theoretical Computer Science",
        "abbrev": "Theor. Comput. Sci.",
        "rank": "B",
        "publisher": "Elsevier",
        "deadline": "2026-05-01",
        "publication_frequency": "semimonthly",
        "website": "https://www.journals.elsevier.com/theoretical-computer-science",
        "description": "理论计算机科学",
        "fields": ["理论计算机", "算法"],
        "impact_factor": 1.3
    },
    {
        "name": "Algorithmica",
        "abbrev": "Algorithmica",
        "rank": "B",
        "publisher": "Springer",
        "deadline": "2026-04-25",
        "publication_frequency": "monthly",
        "website": "https://link.springer.com/journal/453",
        "description": "算法期刊",
        "fields": ["算法", "理论计算机"],
        "impact_factor": 1.5
    },
    {
        "name": "Information and Computation",
        "abbrev": "I&C",
        "rank": "B",
        "publisher": "Elsevier",
        "deadline": "2026-05-05",
        "publication_frequency": "bimonthly",
        "website": "https://www.journals.elsevier.com/information-and-computation",
        "description": "信息与计算",
        "fields": ["理论计算机"],
        "impact_factor": 1.8
    },

    # HCI
    {
        "name": "International Journal of Human-Computer Studies",
        "abbrev": "IJHCS",
        "rank": "B",
        "publisher": "Elsevier",
        "deadline": "2026-04-05",
        "publication_frequency": "monthly",
        "website": "https://www.journals.elsevier.com/international-journal-of-human-computer-studies",
        "description": "国际人机交互研究期刊",
        "fields": ["人机交互"],
        "impact_factor": 3.8
    },
    {
        "name": "Human-Computer Interaction",
        "abbrev": "HCI",
        "rank": "B",
        "publisher": "Taylor & Francis",
        "deadline": "2026-04-15",
        "publication_frequency": "bimonthly",
        "website": "https://www.tandfonline.com/toc/hhci20/current",
        "description": "人机交互期刊",
        "fields": ["人机交互"],
        "impact_factor": 3.5
    },

    # 系统架构
    {
        "name": "IEEE Computer Architecture Letters",
        "abbrev": "CAL",
        "rank": "C",
        "publisher": "IEEE",
        "deadline": "2026-05-10",
        "publication_frequency": "quarterly",
        "website": "https://www.computer.org/csdl/journal/cal",
        "description": "IEEE计算机架构通讯",
        "fields": ["计算机架构"],
        "impact_factor": 1.8
    },

    # 物联网
    {
        "name": "ACM Transactions on Sensor Networks",
        "abbrev": "TOSN",
        "rank": "B",
        "publisher": "ACM",
        "deadline": "2026-04-20",
        "publication_frequency": "quarterly",
        "website": "https://dl.acm.org/journal/tosn",
        "description": "传感器网络汇刊",
        "fields": ["物联网", "传感器网络"],
        "impact_factor": 2.8
    },
    {
        "name": "IEEE Internet of Things Journal",
        "abbrev": "IOT-J",
        "rank": "B",
        "publisher": "IEEE",
        "deadline": "2026-04-25",
        "publication_frequency": "monthly",
        "website": "https://www.ieee.org/",
        "description": "IEEE物联网期刊",
        "fields": ["物联网", "嵌入式系统"],
        "impact_factor": 9.5
    },

    # 信息系统
    {
        "name": "ACM Transactions on Information Systems",
        "abbrev": "TOIS",
        "rank": "A",
        "publisher": "ACM",
        "deadline": "2026-04-10",
        "publication_frequency": "quarterly",
        "website": "https://dl.acm.org/journal/tois",
        "description": "信息系统汇刊，CCF A类",
        "fields": ["信息系统", "信息检索"],
        "impact_factor": 5.5
    },
    {
        "name": "Information Systems Research",
        "abbrev": "ISR",
        "rank": "A",
        "publisher": "INFORMS",
        "deadline": "2026-04-15",
        "publication_frequency": "quarterly",
        "website": "https://pubsonline.informs.org/journal/isre",
        "description": "信息系统研究，CCF A类",
        "fields": ["信息系统", "管理信息系统"],
        "impact_factor": 4.8
    },
    {
        "name": "MIS Quarterly",
        "abbrev": "MIS Q.",
        "rank": "A",
        "publisher": "University of Minnesota",
        "deadline": "2026-05-01",
        "publication_frequency": "quarterly",
        "website": "https://misq.umn.edu/",
        "description": "MIS季刊，信息系统顶刊，CCF A类",
        "fields": ["管理信息系统", "信息系统"],
        "impact_factor": 8.5
    },

    # 多媒体
    {
        "name": "ACM Transactions on Multimedia Computing, Communications and Applications",
        "abbrev": "TOMM",
        "rank": "B",
        "publisher": "ACM",
        "deadline": "2026-04-12",
        "publication_frequency": "quarterly",
        "website": "https://dl.acm.org/journal/tomm",
        "description": "多媒体计算、通信与应用汇刊",
        "fields": ["多媒体", "计算机视觉"],
        "impact_factor": 3.2
    },
    {
        "name": "IEEE Transactions on Multimedia",
        "abbrev": "TMM",
        "rank": "B",
        "publisher": "IEEE",
        "deadline": "2026-04-18",
        "publication_frequency": "bimonthly",
        "website": "https://www.ieee.org/",
        "description": "多媒体汇刊",
        "fields": ["多媒体", "图像处理"],
        "impact_factor": 7.5
    },

    # 自然语言处理
    {
        "name": "Computational Linguistics",
        "abbrev": "CL",
        "rank": "A",
        "publisher": "MIT Press",
        "deadline": "2026-05-05",
        "publication_frequency": "quarterly",
        "website": "https://direct.mit.edu/coli/",
        "description": "计算语言学，CCF A类",
        "fields": ["自然语言处理", "计算语言学"],
        "impact_factor": 4.5
    },
    {
        "name": "ACM Transactions on Speech and Language Processing",
        "abbrev": "TSLP",
        "rank": "C",
        "publisher": "ACM",
        "deadline": "2026-05-10",
        "publication_frequency": "quarterly",
        "website": "https://dl.acm.org/journal/tslp",
        "description": "语音与语言处理汇刊",
        "fields": ["自然语言处理", "语音识别"],
        "impact_factor": 2.1
    },

    # 人工智能（扩展）
    {
        "name": "Artificial Intelligence",
        "abbrev": "AI",
        "rank": "A",
        "publisher": "Elsevier",
        "deadline": "2026-05-15",
        "publication_frequency": "monthly",
        "website": "https://www.journals.elsevier.com/artificial-intelligence",
        "description": "人工智能，CCF A类",
        "fields": ["人工智能", "机器学习"],
        "impact_factor": 14.5
    },
    {
        "name": "Machine Learning",
        "abbrev": "ML",
        "rank": "A",
        "publisher": "Springer",
        "deadline": "2026-05-20",
        "publication_frequency": "monthly",
        "website": "https://link.springer.com/journal/10994",
        "description": "机器学习，CCF A类",
        "fields": ["机器学习"],
        "impact_factor": 8.5
    },
    {
        "name": "Neural Computation",
        "abbrev": "Neural Comput.",
        "rank": "B",
        "publisher": "MIT Press",
        "deadline": "2026-05-25",
        "publication_frequency": "monthly",
        "website": "https://direct.mit.edu/neco/",
        "description": "神经计算",
        "fields": ["神经网络", "计算神经科学"],
        "impact_factor": 3.5
    },
    {
        "name": "Neural Networks",
        "abbrev": "Neural Netw.",
        "rank": "B",
        "publisher": "Elsevier",
        "deadline": "2026-06-01",
        "publication_frequency": "monthly",
        "website": "https://www.journals.elsevier.com/neural-networks",
        "description": "神经网络",
        "fields": ["神经网络", "人工智能"],
        "impact_factor": 7.8
    },

    # 性能评估
    {
        "name": "Performance Evaluation",
        "abbrev": "Perform. Eval.",
        "rank": "C",
        "publisher": "Elsevier",
        "deadline": "2026-06-05",
        "publication_frequency": "monthly",
        "website": "https://www.journals.elsevier.com/performance-evaluation",
        "description": "性能评估",
        "fields": ["性能评估", "计算机网络"],
        "impact_factor": 2.5
    },

    # 并行计算
    {
        "name": "IEEE Transactions on Parallel and Distributed Systems",
        "abbrev": "TPDS",
        "rank": "A",
        "publisher": "IEEE",
        "deadline": "2026-05-30",
        "publication_frequency": "monthly",
        "website": "https://www.computer.org/csdl/journal/tpds",
        "description": "并行与分布式系统汇刊，CCF A类",
        "fields": ["并行计算", "分布式系统"],
        "impact_factor": 5.5
    },
    {
        "name": "Journal of Parallel and Distributed Computing",
        "abbrev": "JPDC",
        "rank": "B",
        "publisher": "Elsevier",
        "deadline": "2026-06-10",
        "publication_frequency": "monthly",
        "website": "https://www.journals.elsevier.com/journal-of-parallel-and-distributed-computing",
        "description": "并行与分布式计算",
        "fields": ["并行计算", "分布式系统"],
        "impact_factor": 2.8
    },

    # 图形学
    {
        "name": "IEEE Transactions on Visualization and Computer Graphics",
        "abbrev": "TVCG",
        "rank": "A",
        "publisher": "IEEE",
        "deadline": "2026-06-15",
        "publication_frequency": "monthly",
        "website": "https://www.computer.org/csdl/journal/tvcg",
        "description": "可视化与计算机图形学汇刊，CCF A类",
        "fields": ["计算机图形学", "可视化"],
        "impact_factor": 5.5
    },
    {
        "name": "Computer Graphics Forum",
        "abbrev": "CGF",
        "rank": "B",
        "publisher": "Wiley",
        "deadline": "2026-06-20",
        "publication_frequency": "bimonthly",
        "website": "https://onlinelibrary.wiley.com/journal/14678659",
        "description": "计算机图形学论坛",
        "fields": ["计算机图形学"],
        "impact_factor": 2.8
    },

    # 可信计算
    {
        "name": "IEEE Transactions on Dependable and Secure Computing",
        "abbrev": "TDSC",
        "rank": "A",
        "publisher": "IEEE",
        "deadline": "2026-06-25",
        "publication_frequency": "bimonthly",
        "website": "https://www.computer.org/csdl/journal/tdsc",
        "description": "可信与安全计算汇刊，CCF A类",
        "fields": ["网络安全", "可信计算"],
        "impact_factor": 5.8
    },

    # 生物信息学
    {
        "name": "Bioinformatics",
        "abbrev": "Bioinformatics",
        "rank": "B",
        "publisher": "Oxford",
        "deadline": "2026-07-01",
        "publication_frequency": "semimonthly",
        "website": "https://academic.oup.com/bioinformatics",
        "description": "生物信息学",
        "fields": ["生物信息学", "计算生物学"],
        "impact_factor": 5.5
    },
    {
        "name": "IEEE/ACM Transactions on Computational Biology and Bioinformatics",
        "abbrev": "TCBB",
        "rank": "B",
        "publisher": "IEEE/ACM",
        "deadline": "2026-07-05",
        "publication_frequency": "bimonthly",
        "website": "https://www.computer.org/csdl/journal/tcbb",
        "description": "计算生物学与生物信息学汇刊",
        "fields": ["生物信息学", "计算生物学"],
        "impact_factor": 3.5
    }
]


def expand_journal_data():
    """扩展期刊数据"""
    print("="*60)
    print("📚 扩展期刊数据库")
    print("="*60)

    manager = JournalManager('journals.json')

    initial_count = len(manager.conferences)
    print(f"\n📊 当前期刊数: {initial_count}")

    print(f"\n➕ 准备添加 {len(EXTENDED_JOURNALS)} 个新期刊...")

    added_count = 0
    for journal in EXTENDED_JOURNALS:
        if manager.add_journal(journal):
            added_count += 1

    print(f"\n✅ 成功添加 {added_count} 个期刊")

    # 保存数据
    manager.save_data()

    final_count = len(manager.conferences)
    print(f"\n📊 扩展后期刊总数: {final_count}")

    # 显示统计
    stats = manager.get_statistics()
    print(f"\n📈 统计信息:")
    print(f"   按等级: A={stats['by_rank']['A']}, "
          f"B={stats['by_rank']['B']}, C={stats['by_rank']['C']}")
    if 'impact_factor_stats' in stats:
        if_stats = stats['impact_factor_stats']
        print(f"   影响因子: 最高={if_stats['max']:.1f}, "
              f"平均={if_stats['avg']:.1f}")

    print("\n" + "="*60)


def main():
    """主函数"""
    expand_journal_data()

    print("\n✅ 期刊数据扩展完成！")
    print("\n💡 接下来可以扩展会议数据（conferences.json）")


if __name__ == '__main__':
    main()
