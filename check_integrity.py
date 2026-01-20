#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据完整性检查脚本
验证所有数据文件的完整性和一致性
"""

import json
import os
import sys
from datetime import datetime

# Windows控制台编码修复
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)


def check_json_file(filepath, name):
    """检查JSON文件完整性

    Args:
        filepath: 文件路径
        name: 文件名称

    Returns:
        (is_valid, error_message, stats)
    """
    if not os.path.exists(filepath):
        return False, f"文件不存在: {filepath}", None

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 基本结构检查
        if isinstance(data, list):
            item_count = len(data)
            has_metadata = False
            items = data
        elif isinstance(data, dict):
            if 'conferences' in data:
                items = data['conferences']
                item_count = len(items)
                has_metadata = 'metadata' in data
            else:
                return False, "JSON格式不正确（缺少conferences字段）", None
        else:
            return False, "JSON根节点类型不正确", None

        # 检查必需字段
        missing_fields = []
        for i, item in enumerate(items[:5]):  # 检查前5个
            if not item.get('name'):
                missing_fields.append(f"item[{i}]: name")
            if not item.get('rank'):
                missing_fields.append(f"item[{i}]: rank")
            if not item.get('deadline'):
                missing_fields.append(f"item[{i}]: deadline")

        # 统计信息
        stats = {
            'total_items': item_count,
            'has_metadata': has_metadata,
            'missing_fields_sample': missing_fields[:5] if missing_fields else []
        }

        # 等级统计
        rank_counts = {'A': 0, 'B': 0, 'C': 0, 'N/A': 0}
        for item in items:
            rank = item.get('rank', 'N/A')
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
        stats['rank_counts'] = rank_counts

        return True, "OK", stats

    except json.JSONDecodeError as e:
        return False, f"JSON格式错误: {e}", None
    except Exception as e:
        return False, f"读取错误: {e}", None


def main():
    print("="*60)
    print("🔍 数据完整性检查")
    print("="*60)

    files_to_check = [
        ('conferences.json', '会议数据'),
        ('journals.json', '期刊数据'),
        ('sources.json', '数据源配置'),
        ('config.example.json', '邮件配置示例'),
        ('feishu_config.example.json', '飞书配置示例'),
    ]

    all_valid = True
    results = []

    for filepath, name in files_to_check:
        print(f"\n📄 检查 {name} ({filepath})...")
        is_valid, msg, stats = check_json_file(filepath, name)

        if is_valid:
            print(f"   ✅ {msg}")
            if stats:
                print(f"   📊 总数: {stats['total_items']}")
                if 'rank_counts' in stats:
                    rc = stats['rank_counts']
                    print(f"   📈 等级分布: A={rc['A']}, B={rc['B']}, C={rc['C']}")
                if stats.get('has_metadata'):
                    print(f"   ✨ 包含元数据")
            results.append((name, True, stats))
        else:
            print(f"   ❌ {msg}")
            results.append((name, False, None))
            all_valid = False

    # 备份文件检查
    print(f"\n💾 检查备份文件...")
    backup_dir = 'backups'
    if os.path.exists(backup_dir):
        backups = [f for f in os.listdir(backup_dir)
                  if f.startswith('conferences_backup_')]
        print(f"   ✅ 找到 {len(backups)} 个备份文件")
        if backups:
            # 显示最新的3个备份
            backups_sorted = sorted(backups, reverse=True)[:3]
            for backup in backups_sorted:
                fpath = os.path.join(backup_dir, backup)
                mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
                size = os.path.getsize(fpath) / 1024
                print(f"      - {backup}")
                print(f"        时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')}, "
                      f"大小: {size:.1f}KB")
    else:
        print(f"   ⚠️  备份目录不存在")

    # Python模块检查
    print(f"\n🐍 检查Python模块...")
    modules = [
        'data_fetcher.py',
        'data_validator.py',
        'conference_manager.py',
        'journal_manager.py',
        'email_sender.py',
        'feishu_notifier.py',
        'manage_customers.py'
    ]

    for module in modules:
        if os.path.exists(module):
            print(f"   ✅ {module}")
        else:
            print(f"   ❌ {module} 缺失")
            all_valid = False

    # 文档文件检查
    print(f"\n📚 检查文档文件...")
    docs = [
        'README.md',
        'CLAUDE.md',
        'DATA_VALIDATION.md',
        'TEST_REPORT.md',
        'STAGE2_SUMMARY.md',
        'FINAL_SUMMARY.md'
    ]

    for doc in docs:
        if os.path.exists(doc):
            print(f"   ✅ {doc}")
        else:
            print(f"   ⚠️  {doc} 不存在（可选）")

    # 总体统计
    print("\n" + "="*60)
    print("📊 检查结果汇总")
    print("="*60)

    total_conferences = 0
    total_journals = 0

    for name, valid, stats in results:
        if valid and stats:
            if '会议' in name:
                total_conferences = stats['total_items']
            elif '期刊' in name:
                total_journals = stats['total_items']

    print(f"会议总数: {total_conferences}")
    print(f"期刊总数: {total_journals}")
    print(f"数据总计: {total_conferences + total_journals}")

    if all_valid:
        print("\n✅ 所有数据文件完整性检查通过！")
        return 0
    else:
        print("\n⚠️  发现问题，请检查上述错误")
        return 1


if __name__ == '__main__':
    sys.exit(main())
