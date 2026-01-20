#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据更新工具
自动从多个数据源获取会议数据并更新到本地数据库
"""

import json
import sys
import argparse
from datetime import datetime
from typing import List, Dict

# 导入核心模块
from data_fetcher import DataFetcher
from data_validator import DataValidator
from conference_manager import ConferenceManager

# Windows控制台编码修复
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)


class DataUpdater:
    """数据更新器"""

    def __init__(self, sources_file: str = 'sources.json'):
        """初始化数据更新器

        Args:
            sources_file: 数据源配置文件路径
        """
        self.fetcher = DataFetcher(sources_file)
        self.validator = DataValidator(sources_file)
        self.manager = ConferenceManager()

    def fetch_all_sources(self, source_ids: List[str] = None) -> Dict[str, List[Dict]]:
        """从所有数据源抓取数据

        Args:
            source_ids: 指定要抓取的数据源ID列表（None表示全部）

        Returns:
            按数据源ID分组的会议数据字典
        """
        print("🌐 开始抓取数据...")

        if source_ids:
            print(f"📌 指定数据源: {', '.join(source_ids)}")
            sources = [s for s in self.fetcher.sources if s['id'] in source_ids]
        else:
            print("📌 使用所有已启用的数据源")
            sources = [s for s in self.fetcher.sources if s.get('enabled', True)]

        if not sources:
            print("❌ 没有可用的数据源")
            return {}

        all_data = {}
        for source in sources:
            source_id = source['id']
            source_name = source['name']

            print(f"\n📥 正在抓取: {source_name} ({source_id})...")
            try:
                data = self.fetcher.fetch_from_source(source_id)
                all_data[source_id] = data
                print(f"   ✅ 成功获取 {len(data)} 个会议/期刊")
            except Exception as e:
                print(f"   ❌ 抓取失败: {e}")
                all_data[source_id] = []

        return all_data

    def validate_data(self, all_data: Dict[str, List[Dict]]) -> Dict:
        """验证抓取的数据

        Args:
            all_data: 按数据源分组的会议数据

        Returns:
            验证报告
        """
        print("\n🔍 开始数据验证...")

        # 合并所有数据源
        all_conferences = []
        for source_id, data in all_data.items():
            all_conferences.extend(data)

        print(f"📊 总共 {len(all_conferences)} 条数据待验证")

        # 分组验证（按会议名称相似度分组）
        validation_results = {}
        processed = set()

        for conf in all_conferences:
            conf_key = conf.get('name', '')
            if not conf_key or conf_key in processed:
                continue

            # 查找相似会议
            similar_confs = [c for c in all_conferences
                           if self.validator._name_similarity(conf_key, c.get('name', '')) > 0.85]

            if similar_confs:
                result = self.validator.validate_conference_group(conf_key, similar_confs)
                validation_results[conf_key] = result
                processed.add(conf_key)

        print(f"✅ 验证完成，共 {len(validation_results)} 个会议组")

        # 统计
        verified = sum(1 for r in validation_results.values() if r['status'] == 'verified')
        conflicts = sum(1 for r in validation_results.values() if r['conflicts'])
        print(f"   - 已验证: {verified}")
        print(f"   - 有冲突: {conflicts}")
        print(f"   - 需人工审核: {len(validation_results) - verified}")

        return validation_results

    def merge_with_existing(self, all_data: Dict[str, List[Dict]],
                           validation_results: Dict = None,
                           auto_fix: bool = False) -> List[Dict]:
        """合并抓取的数据到现有数据库

        Args:
            all_data: 抓取的数据
            validation_results: 验证结果（可选）
            auto_fix: 是否自动修复冲突

        Returns:
            合并后的会议列表
        """
        print("\n🔧 开始合并数据...")

        # 加载现有数据
        existing_confs = self.manager.conferences
        print(f"📚 现有会议数: {len(existing_confs)}")

        # 合并所有新数据
        new_confs = []
        for source_id, data in all_data.items():
            new_confs.extend(data)

        new_confs = self.fetcher.deduplicate_conferences(new_confs)
        print(f"📝 新会议数: {len(new_confs)}")

        # 检查已存在的会议
        existing_names = {c.get('name', ''): c for c in existing_confs}
        merged = existing_confs.copy()
        added_count = 0
        updated_count = 0

        for new_conf in new_confs:
            name = new_conf.get('name', '')
            if not name:
                continue

            if name in existing_names:
                # 更新现有会议
                existing = existing_names[name]
                changed = False

                # 更新截止日期（如果验证结果存在且有推荐值）
                if validation_results and name in validation_results:
                    result = validation_results[name]
                    if result.get('recommended_data'):
                        rec = result['recommended_data']
                        if 'deadline' in rec and rec['deadline'] != existing.get('deadline'):
                            existing['deadline'] = rec['deadline']
                            changed = True

                # 更新其他字段
                for key in ['deadline', 'conference_date', 'website', 'description']:
                    if new_conf.get(key) and new_conf[key] != existing.get(key):
                        existing[key] = new_conf[key]
                        changed = True

                if changed:
                    updated_count += 1
            else:
                # 添加新会议
                merged.append(new_conf)
                added_count += 1

        print(f"   ✅ 添加 {added_count} 个新会议")
        print(f"   🔄 更新 {updated_count} 个现有会议")
        print(f"   📊 总计 {len(merged)} 个会议")

        return merged

    def save_report(self, report: Dict, filename: str = None):
        """保存报告到文件

        Args:
            report: 报告数据
            filename: 文件名（默认自动生成）
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'validation_report_{timestamp}.json'

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"📄 报告已保存: {filename}")

    def run(self, source_ids: List[str] = None,
            validate_only: bool = False,
            auto_fix: bool = False,
            save_report: bool = False,
            apply_changes: bool = False) -> bool:
        """运行完整更新流程

        Args:
            source_ids: 指定数据源
            validate_only: 仅验证不应用更改
            auto_fix: 自动修复冲突
            save_report: 保存验证报告
            apply_changes: 应用更改到数据文件

        Returns:
            是否成功
        """
        try:
            # 1. 抓取数据
            all_data = self.fetch_all_sources(source_ids)
            if not all_data:
                return False

            total_fetched = sum(len(data) for data in all_data.values())
            if total_fetched == 0:
                print("⚠️  没有抓取到任何数据")
                return False

            # 2. 验证数据
            validation_results = self.validate_data(all_data)

            # 3. 保存报告
            if save_report:
                report = {
                    'timestamp': datetime.now().isoformat(),
                    'sources': list(all_data.keys()),
                    'total_fetched': total_fetched,
                    'validation_results': validation_results
                }
                self.save_report(report)

            # 4. 如果只是验证，到此结束
            if validate_only:
                print("\n✅ 验证完成（未应用更改）")
                return True

            # 5. 合并数据
            merged = self.merge_with_existing(all_data, validation_results, auto_fix)

            # 6. 应用更改
            if apply_changes:
                print("\n💾 正在保存更改...")
                self.manager.conferences = merged
                self.manager.save_data()
                print("✅ 数据已更新到 conferences.json")
            else:
                print("\n⚠️  未应用更改（使用 --apply 保存到文件）")

            return True

        except Exception as e:
            print(f"❌ 更新失败: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='CCF会议数据更新工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 从所有数据源抓取并验证
  python update_data.py

  # 只验证不应用更改
  python update_data.py --validate-only

  # 从特定数据源抓取
  python update_data.py --sources ccfddl

  # 自动修复并应用更改
  python update_data.py --auto-fix --apply

  # 保存验证报告
  python update_data.py --save-report
                                    """
    )
    parser.add_argument('-s', '--sources', type=str, nargs='+',
                        help='指定数据源（如：ccfddl manual）')
    parser.add_argument('--validate-only', action='store_true',
                        help='仅验证数据，不应用更改')
    parser.add_argument('--auto-fix', action='store_true',
                        help='自动修复冲突')
    parser.add_argument('--save-report', action='store_true',
                        help='保存验证报告到文件')
    parser.add_argument('--apply', action='store_true',
                        help='应用更改到conferences.json')

    args = parser.parse_args()

    try:
        updater = DataUpdater()
        success = updater.run(
            source_ids=args.sources,
            validate_only=args.validate_only,
            auto_fix=args.auto_fix,
            save_report=args.save_report,
            apply_changes=args.apply
        )
        return 0 if success else 1
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
