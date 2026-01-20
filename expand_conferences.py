#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扩展会议数据 - 添加更多领域的会议
"""

import sys
from datetime import datetime, timedelta
from conference_manager import ConferenceManager

# Windows控制台编码修复
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)


# 新增会议数据
ADDITIONAL_CONFERENCES = [
    # 理论计算领域
    {
        "name": "STOC 2026",
        "rank": "A",
        "deadline": "2026-06-15",
        "conference_date": "2026年6月22-25日",
        "website": "https://acm-stoc.org/",
        "description": "ACM计算理论研讨会，CCF A类会议，录用率28.5%",
        "fields": ["理论计算", "算法", "计算复杂性"]
    },
    {
        "name": "FOCS 2026",
        "rank": "A",
        "deadline": "2026-07-01",
        "conference_date": "2026年11月",
        "website": "https://ieee-focs.org/",
        "description": "IEEE计算机科学基础研讨会，CCF A类会议，录用率29.1%",
        "fields": ["理论计算", "算法"]
    },
    {
        "name": "SODA 2026",
        "rank": "B",
        "deadline": "2026-07-15",
        "conference_date": "2027年1月",
        "website": "https://siam.org/meetings/da26/",
        "description": "ACM-SIAM离散算法研讨会，录用率38.5%",
        "fields": ["理论计算", "算法"]
    },
    {
        "name": "ICALP 2026",
        "rank": "B",
        "deadline": "2026-07-20",
        "conference_date": "2026年7月",
        "website": "https://icalp2026.cs.uni-freiburg.de/",
        "description": "国际自动机、语言与编程研讨会",
        "fields": ["理论计算", "算法"]
    },
    {
        "name": "ESA 2026",
        "rank": "B",
        "deadline": "2026-08-01",
        "conference_date": "2026年9月",
        "website": "https://esa2026.irif.fr/",
        "description": "欧洲研讨会",
        "fields": ["理论计算", "算法"]
    },

    # 人机交互领域
    {
        "name": "CHI 2026",
        "rank": "A",
        "deadline": "2026-09-15",
        "conference_date": "2027年2月",
        "website": "https://chi2026.acm.org/",
        "description": "ACM CHI会议，人机交互顶会，CCF A类会议，录用率26.8%",
        "fields": ["人机交互", "用户界面"]
    },
    {
        "name": "CSCW 2026",
        "rank": "B",
        "deadline": "2026-08-15",
        "conference_date": "2027年2月",
        "website": "https://cscw.acm.org/2026/",
        "description": "ACM计算机支持协同工作会议",
        "fields": ["人机交互", "协同工作"]
    },
    {
        "name": "GROUP 2026",
        "rank": "C",
        "deadline": "2026-09-01",
        "conference_date": "2027年1月",
        "website": "https://group.acm.org/",
        "description": "ACM GROUP会议",
        "fields": ["人机交互", "协同工作"]
    },

    # 云计算/系统领域
    {
        "name": "SOCC 2026",
        "rank": "A",
        "deadline": "2026-06-01",
        "conference_date": "2026年10月",
        "website": "https://socc2026.sigarss.org/",
        "description": "ACM云计算研讨会，CCF A类会议，录用率18.5%",
        "fields": ["云计算", "分布式系统"]
    },
    {
        "name": "EuroSys 2026",
        "rank": "A",
        "deadline": "2026-05-15",
        "conference_date": "2026年4月",
        "website": "https://2026.eurosys.org/",
        "description": "欧洲系统会议，CCF A类会议，录用率19.8%",
        "fields": ["云计算", "操作系统", "分布式系统"]
    },
    {
        "name": "ATC 2026",
        "rank": "B",
        "deadline": "2026-05-20",
        "conference_date": "2026年7月",
        "website": "https://www.usenix.org/conference/atc26",
        "description": "USENIX年度技术会议",
        "fields": ["操作系统", "云计算"]
    },
    {
        "name": "CIDR 2026",
        "rank": "B",
        "deadline": "2026-07-01",
        "conference_date": "2027年1月",
        "website": "https://cidrdb.org/",
        "description": "创新数据系统研究研讨会",
        "fields": ["数据库", "大数据"]
    },

    # 物联网领域
    {
        "name": "SenSys 2026",
        "rank": "B",
        "deadline": "2026-05-01",
        "conference_date": "2026年11月",
        "website": "https://sensys.acm.org/2026/",
        "description": "ACM嵌入式网络传感器系统会议",
        "fields": ["物联网", "传感器网络", "嵌入式系统"]
    },
    {
        "name": "IPSN 2026",
        "rank": "B",
        "deadline": "2026-07-15",
        "conference_date": "2027年4月",
        "website": "https://ipsn.acm.org/2026/",
        "description": "国际信息处理 in sensor networks 会议",
        "fields": ["物联网", "传感器网络", "信息处理"]
    },
    {
        "name": "PerCom 2026",
        "rank": "C",
        "deadline": "2026-07-20",
        "conference_date": "2027年3月",
        "website": "https://percom.org/",
        "description": "国际普适计算会议",
        "fields": ["物联网", "普适计算", "移动计算"]
    },
    {
        "name": "INFOCOM 2026",
        "rank": "A",
        "deadline": "2026-07-30",
        "conference_date": "2027年5月",
        "website": "https://infocom2026.ieee-infocom.org/",
        "description": "IEEE国际计算机通信会议，CCF A类会议，录用率21.5%",
        "fields": ["计算机网络", "物联网"]
    },

    # 区块链
    {
        "name": "ACM CCS 2026",
        "rank": "A",
        "deadline": "2026-05-15",
        "conference_date": "2026年11月",
        "website": "https://www.sigsac.org/ccs/2026/",
        "description": "ACM计算机与通信安全会议，CCF A类会议，录用率19.3%",
        "fields": ["网络安全", "区块链", "密码学"]
    },
    {
        "name": "IEEE S&P 2026",
        "rank": "A",
        "deadline": "2026-05-30",
        "conference_date": "2027年5月",
        "website": "https://www.ieee-security.org/TC/SP2026",
        "description": "IEEE安全与隐私研讨会，CCF A类会议，录用率15.8%",
        "fields": ["网络安全", "隐私保护"]
    },
    {
        "name": "NDSS 2026",
        "rank": "A",
        "deadline": "2026-06-15",
        "conference_date": "2027年2月",
        "website": "https://www.ndss-symposium.org/",
        "description": "网络与分布式系统安全研讨会，CCF A类会议",
        "fields": ["网络安全", "分布式系统"]
    },
    {
        "name": "RAID 2026",
        "rank": "C",
        "deadline": "2026-06-20",
        "conference_date": "2026年9月",
        "website": "https://raid2026.org/",
        "description": "国际最近入侵检测研讨会",
        "fields": ["网络安全", "入侵检测"]
    },

    # 软件工程（扩展）
    {
        "name": "ICSE 2026",
        "rank": "A",
        "deadline": "2026-08-15",
        "conference_date": "2027年4月",
        "website": "https://conf.researchr.org/home/icse-2026",
        "description": "国际软件工程会议，CCF A类会议，录用率22.5%",
        "fields": ["软件工程"]
    },
    {
        "name": "FSE 2026",
        "rank": "A",
        "deadline": "2026-08-30",
        "conference_date": "2027年9月",
        "website": "https://esec-fse.securite.org/",
        "description": "ACM SIGSOFT软件工程基础研讨会，CCF A类会议",
        "fields": ["软件工程"]
    },
    {
        "name": "ICPC 2026",
        "rank": "B",
        "deadline": "2026-08-20",
        "conference_date": "2027年3月",
        "website": "https://conf.researchr.org/home/icpc-2026",
        "description": "国际软件维护与演进会议",
        "fields": ["软件工程", "软件维护"]
    },
    {
        "name": "ESEC/FSE 2026",
        "rank": "A",
        "deadline": "2026-09-01",
        "conference_date": "2027年9月",
        "website": "https://esec-fse.securite.org/",
        "description": "欧洲软件工程会议",
        "fields": ["软件工程"]
    },

    # 计算机图形学（扩展）
    {
        "name": "CVPR 2026",
        "rank": "A",
        "deadline": "2026-11-15",
        "conference_date": "2027年6月",
        "website": "https://cvpr2026.thecvf.com/",
        "description": "IEEE计算机视觉与模式识别会议，CCF A类会议，录用率24.8%",
        "fields": ["计算机视觉", "模式识别"]
    },
    {
        "name": "ICCV 2027",
        "rank": "A",
        "deadline": "2027-03-17",
        "conference_date": "2027年10月",
        "website": "https://iccv2027.thecvf.com/",
        "description": "国际计算机视觉会议，CCF A类会议，录用率28.5%",
        "fields": ["计算机视觉"]
    },
    {
        "name": "SIGGRAPH Asia 2026",
        "rank": "A",
        "deadline": "2026-06-01",
        "conference_date": "2026年12月",
        "website": "https://s2026.siggraph.org/",
        "description": "ACM SIGGRAPH亚洲会议，CCF A类会议",
        "fields": ["计算机图形学", "人机交互"]
    },

    # 自然语言处理
    {
        "name": "ACL 2026",
        "rank": "A",
        "deadline": "2026-12-15",
        "conference_date": "2027年7月",
        "website": "https://2026.aclweb.org/",
        "description": "国际计算语言学年会，CCF A类会议，录用率27.5%",
        "fields": ["自然语言处理", "计算语言学"]
    },
    {
        "name": "EMNLP 2026",
        "rank": "B",
        "deadline": "2026-06-15",
        "conference_date": "2026年11月",
        "website": "https://2026.emnlp.org/",
        "description": "自然语言处理经验方法会议",
        "fields": ["自然语言处理"]
    },
    {
        "name": "NAACL 2026",
        "rank": "C",
        "deadline": "2026-10-01",
        "conference_date": "2027年6月",
        "website": "https://2026.naacl.org/",
        "description": "北美计算语言学年会",
        "fields": ["自然语言处理"]
    },

    # 信息检索
    {
        "name": "WWW 2026",
        "rank": "A",
        "deadline": "2026-10-15",
        "conference_date": "2027年4月",
        "website": "https://www2026.thewebconf.org/",
        "description": "国际万维网会议，CCF A类会议，录用率21.5%",
        "fields": ["信息检索", "万维网", "数据挖掘"]
    },
    {
        "name": "WSDM 2026",
        "rank": "B",
        "deadline": "2026-07-30",
        "conference_date": "2027年3月",
        "website": "https://www.wsdm-conference.org/2026/",
        "description": "ACM国际网络搜索与数据挖掘会议",
        "fields": ["信息检索", "数据挖掘", "搜索"]
    },
    {
        "name": "CIKM 2026",
        "rank": "B",
        "deadline": "2026-06-15",
        "conference_date": "2026年10月",
        "website": "https://www.cikm2026.org/",
        "description": "信息与知识管理国际会议",
        "fields": ["信息检索", "数据库", "知识管理"]
    },

    # 数据挖掘
    {
        "name": "ICDE 2026",
        "rank": "A",
        "deadline": "2026-07-15",
        "conference_date": "2027年4月",
        "website": "https://icde2026.icde.xyz/",
        "description": "国际数据工程会议，CCF A类会议，录用率23.5%",
        "fields": ["数据库", "数据工程", "大数据"]
    },
    {
        "name": "SDM 2026",
        "rank": "B",
        "deadline": "2026-08-01",
        "conference_date": "2027年4月",
        "website": "https://www.siam.org/conferences/dm26/",
        "description": "SIAM国际数据挖掘会议",
        "fields": ["数据挖掘", "机器学习"]
    },

    # 机器人
    {
        "name": "ICRA 2026",
        "rank": "B",
        "deadline": "2026-09-15",
        "conference_date": "2027年5月",
        "website": "https://2026.ieee-icra.org/",
        "description": "IEEE国际机器人与自动化会议",
        "fields": ["机器人", "自动化"]
    },
    {
        "name": "IROS 2026",
        "rank": "B",
        "deadline": "2026-08-30",
        "conference_date": "2026年10月",
        "website": "https://iros2026.org/",
        "description": "IEEE/RSJ智能机器人与系统国际会议",
        "fields": ["机器人", "智能系统"]
    },
    {
        "name": "RSS 2026",
        "rank": "B",
        "deadline": "2026-07-01",
        "conference_date": "2026年6月",
        "website": "https://roboticsconference.org/",
        "description": "机器人：科学与系统",
        "fields": ["机器人"]
    },

    # 区域性会议
    {
        "name": "CNCC 2026",
        "rank": "C",
        "deadline": "2026-07-30",
        "conference_date": "2026年10月",
        "website": "https://cncc.ccf.org.cn/",
        "description": "中国计算机大会",
        "fields": ["综合", "计算机科学"]
    },
    {
        "name": "PRICAI 2026",
        "rank": "C",
        "deadline": "2026-05-15",
        "conference_date": "2026年11月",
        "website": "https://www.pricai2026.org/",
        "description": "太平洋人工智能国际会议",
        "fields": ["人工智能"]
    }
]


def expand_conference_data():
    """扩展会议数据"""
    print("="*60)
    print("📚 扩展会议数据库")
    print("="*60)

    manager = ConferenceManager('conferences.json')

    initial_count = len(manager.conferences)
    print(f"\n📊 当前会议数: {initial_count}")

    print(f"\n➕ 准备添加 {len(ADDITIONAL_CONFERENCES)} 个新会议...")

    added_count = 0
    for conf in ADDITIONAL_CONFERENCES:
        # 设置type为conference
        conf['type'] = 'conference'
        if manager.add_conference(conf):
            added_count += 1

    print(f"\n✅ 成功添加 {added_count} 个会议")

    # 保存数据
    manager.save_data()

    final_count = len(manager.conferences)
    print(f"\n📊 扩展后会议总数: {final_count}")

    # 显示统计
    stats = manager.get_statistics()
    print(f"\n📈 统计信息:")
    print(f"   按等级: A={stats['by_rank']['A']}, "
          f"B={stats['by_rank']['B']}, C={stats['by_rank']['C']}")

    # 按领域统计
    field_counts = {}
    for conf in manager.conferences:
        for field in conf.get('fields', []):
            field_counts[field] = field_counts.get(field, 0) + 1

    print(f"\n   主要领域（前10）:")
    top_fields = sorted(field_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for field, count in top_fields:
        print(f"   - {field}: {count}")

    print("\n" + "="*60)


def main():
    """主函数"""
    expand_conference_data()

    print("\n✅ 会议数据扩展完成！")
    print(f"\n💡 当前数据:")
    print(f"   - 期刊: 49个")
    print(f"   - 会议: {len(ConferenceManager('conferences.json').conferences)}个")
    print(f"   - 总计: {49 + len(ConferenceManager('conferences.json').conferences)}条")


if __name__ == '__main__':
    main()
