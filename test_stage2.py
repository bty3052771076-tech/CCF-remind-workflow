#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阶段2验证脚本 - 测试期刊和会议整合
"""

import sys
from conference_manager import ConferenceManager
from journal_manager import JournalManager

# Windows控制台编码修复
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)


def main():
    print("="*60)
    print("🎯 阶段2功能验证")
    print("="*60)

    # 1. 测试会议管理器
    print("\n📚 会议数据验证")
    print("-" * 60)
    conf_manager = ConferenceManager('conferences.json')
    conf_stats = conf_manager.get_statistics()

    print(f"✅ 会议总数: {conf_stats['total']}")
    print(f"   等级分布: A={conf_stats['by_rank']['A']}, "
          f"B={conf_stats['by_rank']['B']}, C={conf_stats['by_rank']['C']}")
    print(f"   即将截止(30天): {conf_stats['upcoming_30days']}")

    # 2. 测试期刊管理器
    print("\n📖 期刊数据验证")
    print("-" * 60)
    journal_manager = JournalManager('journals.json')
    journal_stats = journal_manager.get_statistics()

    print(f"✅ 期刊总数: {journal_stats['total']}")
    print(f"   等级分布: A={journal_stats['by_rank']['A']}, "
          f"B={journal_stats['by_rank']['B']}, C={journal_stats['by_rank']['C']}")
    print(f"   出版周期: {journal_stats['by_publication_type']}")

    if 'impact_factor_stats' in journal_stats:
        if_stats = journal_stats['impact_factor_stats']
        print(f"   影响因子:")
        print(f"     - 最高: {if_stats['max']:.1f}")
        print(f"     - 最低: {if_stats['min']:.1f}")
        print(f"     - 平均: {if_stats['avg']:.1f}")

    # 3. 测试Top期刊
    print("\n🏆 Top 10期刊（按影响因子）")
    print("-" * 60)
    top_journals = journal_manager.get_top_journals(10, 'impact_factor')
    for i, j in enumerate(top_journals, 1):
        name = j.get('abbrev', j.get('name', 'Unknown'))
        if_factor = j.get('impact_factor', 0)
        rank = j.get('rank', 'N/A')
        print(f"   {i:2d}. {name:15s}  IF={if_factor:5.1f}  CCF-{rank}")

    # 4. 测试筛选功能
    print("\n🔍 筛选功能测试")
    print("-" * 60)

    # 筛选A类会议
    rank_a = conf_manager.filter_conferences(rank='A')
    print(f"✅ A类会议: {len(rank_a)} 个")

    # 筛选高影响因子期刊
    high_impact = journal_manager.filter_by_impact_factor(5.0, 100.0)
    print(f"✅ 高影响因子期刊(>5.0): {len(high_impact)} 个")

    # 5. 领域统计
    print("\n📊 领域分布")
    print("-" * 60)

    # 会议领域
    conf_fields = {}
    for conf in conf_manager.conferences:
        for field in conf.get('fields', []):
            conf_fields[field] = conf_fields.get(field, 0) + 1

    top_conf_fields = sorted(conf_fields.items(), key=lambda x: x[1], reverse=True)[:10]
    print(f"会议领域 Top 10:")
    for field, count in top_conf_fields:
        print(f"   - {field}: {count}")

    # 期刊领域
    journal_fields = {}
    for journal in journal_manager.conferences:
        for field in journal.get('fields', []):
            journal_fields[field] = journal_fields.get(field, 0) + 1

    top_journal_fields = sorted(journal_fields.items(), key=lambda x: x[1], reverse=True)[:10]
    print(f"\n期刊领域 Top 10:")
    for field, count in top_journal_fields:
        print(f"   - {field}: {count}")

    # 6. 总结
    print("\n" + "="*60)
    print("📈 阶段2数据汇总")
    print("="*60)
    print(f"会议: {conf_stats['total']} 个")
    print(f"期刊: {journal_stats['total']} 个")
    print(f"总计: {conf_stats['total'] + journal_stats['total']} 条")
    print(f"\nA类会议: {conf_stats['by_rank']['A']} ({conf_stats['by_rank']['A']/conf_stats['total']*100:.1f}%)")
    print(f"A类期刊: {journal_stats['by_rank']['A']} ({journal_stats['by_rank']['A']/journal_stats['total']*100:.1f}%)")

    print("\n✅ 阶段2验证完成！")
    print("\n💡 下一步：阶段3 - 集成与工具")
    print("   - 修改email_sender.py集成验证功能")
    print("   - 添加筛选参数（--field, --rank, --type）")
    print("   - 创建数据更新工具")
    print("="*60)


if __name__ == '__main__':
    main()
