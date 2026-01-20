#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据验证工具
独立的数据验证工具，用于检查会议数据的完整性和准确性
"""

import json
import sys
import argparse
from datetime import datetime
from typing import List, Dict, Tuple

# 导入核心模块
from data_validator import DataValidator, ConflictType, ConflictResolver, match_conference_name
from conference_manager import ConferenceManager

# Windows控制台编码修复
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)


class DataValidatorTool:
    """数据验证工具"""

    def __init__(self, data_file: str = 'conferences.json',
                 sources_file: str = 'sources.json'):
        """初始化验证工具

        Args:
            data_file: 数据文件路径
            sources_file: 数据源配置文件路径
        """
        self.data_file = data_file
        self.manager = ConferenceManager(data_file)
        self.validator = DataValidator(sources_file)

    def validate_completeness(self) -> Dict:
        """验证数据完整性

        Returns:
            验证结果
        """
        print("🔍 验证数据完整性...")

        conferences = self.manager.conferences
        issues = []

        required_fields = ['name', 'rank', 'deadline']
        optional_fields = ['website', 'description', 'conference_date']

        for i, conf in enumerate(conferences):
            # 检查必需字段
            for field in required_fields:
                if not conf.get(field):
                    issues.append({
                        'type': 'missing_required',
                        'index': i,
                        'name': conf.get('name', 'Unknown'),
                        'field': field,
                        'severity': 'error'
                    })

            # 检查可选字段
            for field in optional_fields:
                if not conf.get(field):
                    issues.append({
                        'type': 'missing_optional',
                        'index': i,
                        'name': conf.get('name', 'Unknown'),
                        'field': field,
                        'severity': 'warning'
                    })

        # 按严重程度分类
        errors = [i for i in issues if i['severity'] == 'error']
        warnings = [i for i in issues if i['severity'] == 'warning']

        print(f"   ✅ 检查了 {len(conferences)} 个会议")
        print(f"   ❌ 错误: {len(errors)}")
        print(f"   ⚠️  警告: {len(warnings)}")

        return {
            'total': len(conferences),
            'errors': errors,
            'warnings': warnings,
            'error_count': len(errors),
            'warning_count': len(warnings)
        }

    def validate_deadlines(self) -> Dict:
        """验证截止日期

        Returns:
            验证结果
        """
        print("\n🔍 验证截止日期...")

        conferences = self.manager.conferences
        issues = []
        today = datetime.now()

        for conf in conferences:
            deadline_str = conf.get('deadline')
            if not deadline_str:
                continue

            try:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
                days_diff = (deadline - today).days

                # 检查过期会议
                if days_diff < -365:  # 超过1年
                    issues.append({
                        'type': 'expired',
                        'name': conf['name'],
                        'deadline': deadline_str,
                        'days_expired': abs(days_diff),
                        'severity': 'warning'
                    })

                # 检查格式
                if deadline_str != deadline.strftime('%Y-%m-%d'):
                    issues.append({
                        'type': 'format_error',
                        'name': conf['name'],
                        'deadline': deadline_str,
                        'severity': 'error'
                    })

            except ValueError as e:
                issues.append({
                    'type': 'invalid_date',
                    'name': conf.get('name', 'Unknown'),
                    'deadline': deadline_str,
                    'error': str(e),
                    'severity': 'error'
                })

        print(f"   ✅ 检查了 {len(conferences)} 个截止日期")
        print(f"   ❌ 错误: {len([i for i in issues if i['severity'] == 'error'])}")
        print(f"   ⚠️  警告: {len([i for i in issues if i['severity'] == 'warning'])}")

        return {
            'total_checked': len(conferences),
            'issues': issues,
            'error_count': len([i for i in issues if i['severity'] == 'error']),
            'warning_count': len([i for i in issues if i['severity'] == 'warning'])
        }

    def validate_duplicates(self) -> Dict:
        """验证重复数据

        Returns:
            验证结果
        """
        print("\n🔍 验证重复数据...")

        conferences = self.manager.conferences
        duplicates = []
        seen = {}

        for conf in conferences:
            name = conf.get('name', '')
            if not name:
                continue

            # 检查完全重复
            if name in seen:
                duplicates.append({
                    'name': name,
                    'index1': seen[name],
                    'severity': 'error'
                })
            else:
                seen[name] = conferences.index(conf)

        # 检查相似度高的会议
        similar_pairs = []
        names = list(seen.keys())
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                name1, name2 = names[i], names[j]
                similarity = match_conference_name(name1, name2)
                if 0.85 < similarity < 1.0:  # 相似但不完全相同
                    similar_pairs.append({
                        'name1': name1,
                        'name2': name2,
                        'similarity': round(similarity, 2),
                        'severity': 'warning'
                    })

        print(f"   ✅ 检查了 {len(conferences)} 个会议")
        print(f"   ❌ 完全重复: {len(duplicates)}")
        print(f"   ⚠️  高度相似: {len(similar_pairs)}")

        return {
            'total_checked': len(conferences),
            'duplicates': duplicates,
            'similar_pairs': similar_pairs,
            'duplicate_count': len(duplicates),
            'similar_count': len(similar_pairs)
        }

    def validate_ranks(self) -> Dict:
        """验证CCF等级

        Returns:
            验证结果
        """
        print("\n🔍 验证CCF等级...")

        conferences = self.manager.conferences
        issues = []
        valid_ranks = ['A', 'B', 'C']

        rank_counts = {'A': 0, 'B': 0, 'C': 0, 'Unknown': 0}

        for conf in conferences:
            rank = conf.get('rank', '').upper()
            if not rank:
                rank_counts['Unknown'] += 1
                issues.append({
                    'type': 'missing_rank',
                    'name': conf['name'],
                    'severity': 'error'
                })
            elif rank not in valid_ranks:
                issues.append({
                    'type': 'invalid_rank',
                    'name': conf['name'],
                    'rank': rank,
                    'severity': 'error'
                })
            else:
                rank_counts[rank] += 1

        print(f"   ✅ 等级分布:")
        for rank in ['A', 'B', 'C', 'Unknown']:
            print(f"      - {rank}: {rank_counts[rank]}")
        print(f"   ❌ 无效等级: {len([i for i in issues if i['type'] == 'invalid_rank'])}")
        print(f"   ❌ 缺失等级: {len([i for i in issues if i['type'] == 'missing_rank'])}")

        return {
            'total_checked': len(conferences),
            'rank_distribution': rank_counts,
            'issues': issues,
            'error_count': len(issues)
        }

    def validate_websites(self) -> Dict:
        """验证网站链接

        Returns:
            验证结果
        """
        print("\n🔍 验证网站链接...")

        conferences = self.manager.conferences
        issues = []

        for conf in conferences:
            website = conf.get('website')
            if not website:
                continue

            # 检查URL格式
            if not (website.startswith('http://') or website.startswith('https://')):
                issues.append({
                    'type': 'invalid_url',
                    'name': conf['name'],
                    'website': website,
                    'severity': 'warning'
                })

        print(f"   ✅ 检查了 {len(conferences)} 个会议")
        print(f"   ⚠️  URL格式问题: {len(issues)}")

        return {
            'total_checked': len(conferences),
            'issues': issues,
            'warning_count': len(issues)
        }

    def generate_report(self) -> Dict:
        """生成完整验证报告

        Returns:
            完整验证报告
        """
        print("="*60)
        print("📊 开始生成验证报告")
        print("="*60)

        report = {
            'timestamp': datetime.now().isoformat(),
            'data_file': self.data_file,
            'validation_results': {}
        }

        # 运行各项验证
        report['validation_results']['completeness'] = self.validate_completeness()
        report['validation_results']['deadlines'] = self.validate_deadlines()
        report['validation_results']['duplicates'] = self.validate_duplicates()
        report['validation_results']['ranks'] = self.validate_ranks()
        report['validation_results']['websites'] = self.validate_websites()

        # 汇总统计
        total_errors = (report['validation_results']['completeness']['error_count'] +
                       report['validation_results']['deadlines']['error_count'] +
                       report['validation_results']['duplicates']['duplicate_count'] +
                       report['validation_results']['ranks']['error_count'])

        total_warnings = (report['validation_results']['completeness']['warning_count'] +
                         report['validation_results']['deadlines']['warning_count'] +
                         report['validation_results']['duplicates']['similar_count'] +
                         report['validation_results']['websites']['warning_count'])

        report['summary'] = {
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'status': 'passed' if total_errors == 0 else 'failed'
        }

        # 显示汇总
        print("\n" + "="*60)
        print("📋 验证汇总")
        print("="*60)
        print(f"   ❌ 总错误数: {total_errors}")
        print(f"   ⚠️  总警告数: {total_warnings}")
        print(f"   {'✅ 验证通过' if total_errors == 0 else '❌ 验证失败'}")
        print("="*60)

        return report

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

        print(f"\n📄 报告已保存: {filename}")

    def auto_fix(self, report: Dict, apply: bool = False) -> Tuple[int, int]:
        """自动修复可修复的问题

        Args:
            report: 验证报告
            apply: 是否应用修复

        Returns:
            (修复数量, 跳过数量)
        """
        print("\n🔧 自动修复...")

        fixed = 0
        skipped = 0

        if not apply:
            print("⚠️  预览模式（使用 --apply 应用修复）")
            return fixed, skipped

        # TODO: 实现自动修复逻辑
        # 1. 删除完全重复的会议
        # 2. 标准化日期格式
        # 3. 标准化等级大小写
        # 4. 修复URL格式

        print("⚠️  自动修复功能尚未实现")
        return fixed, skipped


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='CCF会议数据验证工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 验证数据
  python validate_data.py

  # 验证并保存报告
  python validate_data.py --save-report

  # 验证期刊数据
  python validate_data.py --data journals.json

  # 详细输出
  python validate_data.py --verbose
                                    """
    )
    parser.add_argument('-d', '--data', type=str, default='conferences.json',
                        help='数据文件路径 (默认: conferences.json)')
    parser.add_argument('-s', '--sources', type=str, default='sources.json',
                        help='数据源配置文件路径')
    parser.add_argument('--save-report', action='store_true',
                        help='保存验证报告到文件')
    parser.add_argument('--report-file', type=str,
                        help='指定报告文件名')
    parser.add_argument('--apply', action='store_true',
                        help='应用自动修复')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='详细输出')

    args = parser.parse_args()

    try:
        validator = DataValidatorTool(args.data, args.sources)

        # 生成报告
        report = validator.generate_report()

        # 保存报告
        if args.save_report:
            validator.save_report(report, args.report_file)

        # 自动修复
        if args.apply:
            fixed, skipped = validator.auto_fix(report, apply=True)
            print(f"\n✅ 修复了 {fixed} 个问题，跳过 {skipped} 个")

        # 返回状态
        return 0 if report['summary']['total_errors'] == 0 else 1

    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
