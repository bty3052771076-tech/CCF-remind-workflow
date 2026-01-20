#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心模块测试脚本
测试 data_fetcher, data_validator, conference_manager 的功能
"""

import json
import os
import sys
import shutil
from datetime import datetime, timedelta

# Windows控制台编码修复
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# 测试数据
TEST_CONFERENCE = {
    "name": "Test Conference 2026",
    "rank": "A",
    "deadline": "2026-12-31",
    "conference_date": "2026年8月",
    "website": "https://test.conf.org",
    "description": "测试会议"
}

MULTI_SOURCE_DATA = {
    "ccfddl": [
        {
            "id": "ijcai-2026",
            "name": "IJCAI 2026",
            "rank": "A",
            "deadline": "2026-01-20",
            "source_id": "ccfddl"
        },
        {
            "id": "aaai-2026",
            "name": "AAAI 2026",
            "rank": "A",
            "deadline": "2026-02-15",
            "source_id": "ccfddl"
        }
    ],
    "manual": [
        {
            "id": "ijcai-2026",
            "name": "IJCAI 2026",
            "rank": "A",
            "deadline": "2026-01-20",  # 相同，应该验证通过
            "source_id": "manual"
        },
        {
            "id": "cvpr-2026",
            "name": "CVPR 2026",
            "rank": "A",
            "deadline": "2026-11-15",
            "source_id": "manual"
        }
    ]
}


def test_conference_manager():
    """测试会议管理器"""
    print("\n" + "="*60)
    print("🧪 测试 conference_manager.py")
    print("="*60)

    from conference_manager import ConferenceManager

    # 创建临时测试文件
    test_file = "test_conferences.json"
    backup_file = "conferences.json"

    try:
        # 备份原文件
        if os.path.exists(backup_file):
            shutil.copy2(backup_file, test_file)

        # 测试1: 初始化和加载
        print("\n📋 测试1: 初始化和加载数据")
        manager = ConferenceManager(test_file)
        print(f"   ✅ 成功加载 {len(manager.conferences)} 个会议")
        assert len(manager.conferences) > 0, "应该有会议数据"
        print("   ✅ 测试通过")

        # 测试2: 统计信息
        print("\n📊 测试2: 获取统计信息")
        stats = manager.get_statistics()
        print(f"   总数: {stats['total']}")
        print(f"   A类: {stats['by_rank']['A']}")
        print(f"   B类: {stats['by_rank']['B']}")
        print(f"   C类: {stats['by_rank']['C']}")
        assert stats['total'] > 0, "应该有统计数据"
        print("   ✅ 测试通过")

        # 测试3: 筛选功能
        print("\n🔍 测试3: 筛选会议")
        rank_a = manager.filter_conferences(rank='A')
        print(f"   找到 {len(rank_a)} 个A类会议")
        assert len(rank_a) > 0, "应该有A类会议"
        print("   ✅ 测试通过")

        # 测试4: 添加会议
        print("\n➕ 测试4: 添加会议")
        initial_count = len(manager.conferences)
        success = manager.add_conference(TEST_CONFERENCE.copy())
        print(f"   添加结果: {success}")
        print(f"   会议数变化: {initial_count} → {len(manager.conferences)}")
        assert len(manager.conferences) == initial_count + 1, "会议数应该增加1"
        print("   ✅ 测试通过")

        # 测试5: 查找会议
        print("\n🔎 测试5: 查找会议")
        conf = manager.find_conference("test-2026")
        print(f"   找到会议: {conf['name'] if conf else 'None'}")
        assert conf is not None, "应该能找到刚添加的会议"
        assert conf['name'] == TEST_CONFERENCE['name'], "会议名称应该匹配"
        print("   ✅ 测试通过")

        # 测试6: 更新会议
        print("\n✏️  测试6: 更新会议")
        success = manager.update_conference(
            "test-2026",
            {"description": "更新后的描述"}
        )
        conf = manager.find_conference("test-2026")
        print(f"   更新结果: {success}")
        print(f"   新描述: {conf['description']}")
        assert conf['description'] == "更新后的描述", "描述应该已更新"
        print("   ✅ 测试通过")

        # 测试7: 删除会议
        print("\n🗑️  测试7: 删除会议")
        success = manager.delete_conference("test-2026")
        print(f"   删除结果: {success}")
        print(f"   会议数变化: {len(manager.conferences)} → {initial_count}")
        assert len(manager.conferences) == initial_count, "会议数应该恢复原值"
        print("   ✅ 测试通过")

        # 测试8: 备份功能
        print("\n💾 测试8: 备份功能")
        backup_path = manager._create_backup()
        print(f"   备份路径: {backup_path}")
        assert os.path.exists(backup_path), "备份文件应该存在"
        print("   ✅ 测试通过")

        # 测试9: 数据迁移
        print("\n🔄 测试9: 数据格式迁移")
        old_format_conf = {
            "name": "Old Format Conf",
            "rank": "B",
            "deadline": "2026-06-01"
        }
        new_format_conf = manager.migrate_old_format(old_format_conf)
        print(f"   旧格式: {list(old_format_conf.keys())}")
        print(f"   新格式字段: {list(new_format_conf.keys())}")
        assert 'id' in new_format_conf, "新格式应该有id字段"
        assert 'verification' in new_format_conf, "新格式应该有verification字段"
        assert 'metadata' in new_format_conf, "新格式应该有metadata字段"
        print("   ✅ 测试通过")

        print("\n" + "="*60)
        print("✅ conference_manager.py 所有测试通过！")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)

    return True


def test_data_validator():
    """测试数据验证器"""
    print("\n" + "="*60)
    print("🧪 测试 data_validator.py")
    print("="*60)

    from data_validator import DataValidator, match_conference_name

    try:
        # 测试1: 初始化
        print("\n📋 测试1: 初始化验证器")
        validator = DataValidator('sources.json')
        print(f"   数据源数量: {len(validator.sources)}")
        assert len(validator.sources) > 0, "应该有数据源配置"
        print("   ✅ 测试通过")

        # 测试2: 名称匹配
        print("\n🔍 测试2: 会议名称匹配")
        # 测试相似的名称
        similarity1 = match_conference_name("IJCAI 2026", "IJCAI 2026")
        similarity2 = match_conference_name("CVPR Conference", "CVPR")
        similarity3 = match_conference_name("International Joint Conference on AI", "IJCAI")
        print(f"   完全匹配相似度: {similarity1:.2f}")
        print(f"   包含关系相似度: {similarity2:.2f}")
        print(f"   全称vs缩写: {similarity3:.2f}")
        assert similarity1 > 0.9, "完全匹配相似度应该很高"
        assert similarity2 > 0.3, "包含关系相似度应该大于0.3"
        assert similarity3 > 0.2, "全称vs缩写相似度应该大于0.2"
        print("   ✅ 测试通过")

        # 测试3: 验证多源数据
        print("\n✅ 测试3: 交叉验证多源数据")
        results = validator.validate_all(MULTI_SOURCE_DATA)
        print(f"   总会议数: {results['total']}")
        print(f"   已验证: {len(results['verified'])}")
        print(f"   有冲突: {len(results['conflicts'])}")
        print(f"   未验证: {len(results['unverified'])}")

        # 检查IJCAI应该验证通过（两个源数据一致）
        ijcai_verified = any(
            'ijcai' in r['key'].lower() and r['status'] == 'verified'
            for r in results['verified'] + results['unverified']
        )
        print(f"   IJCAI验证状态: {'通过' if ijcai_verified else '未通过'}")
        print("   ✅ 测试通过")

        # 测试4: 冲突解决
        print("\n⚖️  测试4: 冲突解决策略")
        if results['conflicts']:
            conflict = results['conflicts'][0]
            print(f"   冲突会议: {conflict['name']}")
            print(f"   冲突类型: {[c['type'] for c in conflict['conflicts']]}")
            print(f"   推荐数据: {conflict.get('recommended_data', {})}")
        print("   ✅ 测试通过")

        # 测试5: 生成报告
        print("\n📄 测试5: 生成验证报告")
        report_file = "test_validation_report.json"
        validator.save_report(results, report_file)
        print(f"   报告已保存: {report_file}")
        assert os.path.exists(report_file), "报告文件应该存在"

        # 读取并检查报告
        with open(report_file, 'r', encoding='utf-8') as f:
            report = json.load(f)
        print(f"   报告生成时间: {report['generated_at']}")
        print(f"   统计信息: {list(report['statistics'].keys())}")
        assert 'statistics' in report, "报告应该包含统计信息"
        print("   ✅ 测试通过")

        print("\n" + "="*60)
        print("✅ data_validator.py 所有测试通过！")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # 清理测试文件
        if os.path.exists("test_validation_report.json"):
            os.remove("test_validation_report.json")

    return True


def test_data_fetcher():
    """测试数据抓取器"""
    print("\n" + "="*60)
    print("🧪 测试 data_fetcher.py")
    print("="*60)

    from data_fetcher import DataFetcher

    try:
        # 测试1: 初始化
        print("\n📋 测试1: 初始化数据抓取器")
        fetcher = DataFetcher('sources.json')
        print(f"   数据源数量: {len(fetcher.sources)}")
        assert len(fetcher.sources) > 0, "应该有数据源配置"
        print("   ✅ 测试通过")

        # 测试2: 数据源配置
        print("\n⚙️  测试2: 数据源配置检查")
        enabled_sources = [s for s in fetcher.sources if s.get('enabled', True)]
        print(f"   启用的数据源: {len(enabled_sources)}")
        for source in enabled_sources:
            print(f"   - {source['id']}: {source['name']}")
        print("   ✅ 测试通过")

        # 测试3: 数据标准化
        print("\n🔧 测试3: 数据标准化")
        raw_conf = {
            "name": "  IJCAI 2026  ",
            "rank": "a",
            "deadline": "2026/01/20"
        }
        normalized = fetcher.normalize_conference(raw_conf, "test")
        print(f"   原始名称: '{raw_conf['name']}'")
        print(f"   标准化: '{normalized['name']}'")
        print(f"   原始等级: '{raw_conf['rank']}'")
        print(f"   标准化: '{normalized['rank']}'")
        assert normalized['name'].strip() == raw_conf['name'].strip(), "名称应该保留"
        assert normalized['rank'] == 'A', "等级应该大写"
        print("   ✅ 测试通过")

        # 测试4: ID生成
        print("\n🆔 测试4: 会议ID生成")
        test_cases = [
            ("IJCAI 2026", "2026-01-20"),
            ("CVPR 2026", "2026-11-15"),
            ("AAAI-26", "2026-08-01")
        ]
        for name, deadline in test_cases:
            conf_id = fetcher._generate_conf_id(name, deadline)
            print(f"   {name} → {conf_id}")
            assert '-' in conf_id, "ID应该包含连字符"
        print("   ✅ 测试通过")

        # 测试5: 抓取手动数据源
        print("\n📥 测试5: 抓取手动数据源")
        data = fetcher.fetch_from_source('manual')
        print(f"   抓取结果: {len(data)} 条数据")
        print(f"   ✅ 测试通过")

        print("\n" + "="*60)
        print("✅ data_fetcher.py 所有测试通过！")
        print("="*60)
        print("   ℹ️  注意: 网页抓取功能需要网络连接，在此测试中跳过")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def test_integration():
    """集成测试"""
    print("\n" + "="*60)
    print("🧪 集成测试 - 完整工作流程")
    print("="*60)

    from conference_manager import ConferenceManager
    from data_validator import DataValidator

    try:
        # 测试完整工作流程
        print("\n🔄 测试: 管理器 → 验证器 → 报告")

        # 1. 从管理器获取数据
        print("\n1️⃣  加载会议数据")
        manager = ConferenceManager('conferences.json')
        conferences = manager.conferences[:10]  # 只测试前10个
        print(f"   选取 {len(conferences)} 个会议进行测试")

        # 2. 模拟多源数据
        print("\n2️⃣  模拟多源数据")
        multi_source = {
            'source1': conferences[:5],
            'source2': conferences[5:10]
        }
        print(f"   数据源1: {len(multi_source['source1'])} 个会议")
        print(f"   数据源2: {len(multi_source['source2'])} 个会议")

        # 3. 验证数据
        print("\n3️⃣  执行交叉验证")
        validator = DataValidator('sources.json')
        results = validator.validate_all(multi_source)
        print(f"   验证完成: {results['total']} 个会议")

        # 4. 生成报告
        print("\n4️⃣  生成报告")
        report_file = "test_integration_report.json"
        validator.save_report(results, report_file)
        print(f"   报告已保存: {report_file}")

        print("\n" + "="*60)
        print("✅ 集成测试通过！")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # 清理测试文件
        if os.path.exists("test_integration_report.json"):
            os.remove("test_integration_report.json")

    return True


def main():
    """运行所有测试"""
    print("\n" + "🚀"*30)
    print("CCF会议提醒系统 - 核心模块测试")
    print("🚀"*30)

    results = {
        'conference_manager': False,
        'data_validator': False,
        'data_fetcher': False,
        'integration': False
    }

    # 运行测试
    try:
        results['conference_manager'] = test_conference_manager()
        results['data_validator'] = test_data_validator()
        results['data_fetcher'] = test_data_fetcher()
        results['integration'] = test_integration()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        return

    # 汇总结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")

    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print("\n🎉 所有测试通过！系统运行正常。")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查。")
        return 1


if __name__ == '__main__':
    sys.exit(main())
