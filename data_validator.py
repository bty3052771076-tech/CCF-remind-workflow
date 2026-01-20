#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据验证器 - 交叉验证会议数据并检测冲突
支持多数据源验证、冲突检测和置信度计算
"""

import json
import re
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from difflib import SequenceMatcher
from enum import Enum

# Windows控制台编码修复
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)


class ConflictType(Enum):
    """冲突类型枚举"""
    DEADLINE_MISMATCH = "deadline_mismatch"       # 截止日期不一致
    RANK_MISMATCH = "rank_mismatch"               # 等级不一致
    MISSING_FIELD = "missing_field"               # 字段缺失
    DUPLICATE_ENTRY = "duplicate_entry"           # 重复条目
    NAME_MISMATCH = "name_mismatch"               # 名称不匹配


class VerificationStatus(Enum):
    """验证状态枚举"""
    VERIFIED = "verified"                         # 已验证
    CONFLICT = "conflict"                         # 有冲突
    UNVERIFIED = "unverified"                     # 未验证
    OUTDATED = "outdated"                         # 已过期


class ConflictResolver:
    """冲突解决器"""

    @staticmethod
    def by_priority(sources: List[Dict], priority_order: List[str]) -> Dict:
        """按优先级解决冲突

        Args:
            sources: 数据源列表
            priority_order: 优先级顺序（从高到低）

        Returns:
            优先级最高的数据源
        """
        for priority_id in priority_order:
            for source in sources:
                if source.get('source_id') == priority_id:
                    return source
        # 如果没有找到优先级匹配，返回第一个
        return sources[0] if sources else {}

    @staticmethod
    def by_majority(sources: List[Dict], field: str) -> Tuple[any, int]:
        """按多数投票解决冲突

        Args:
            sources: 数据源列表
            field: 要比较的字段名

        Returns:
            (最常见的值, 出现次数)
        """
        values = [s.get('data', {}).get(field) for s in sources if s.get('data', {}).get(field)]

        if not values:
            return None, 0

        # 统计每个值的出现次数
        value_counts = {}
        for value in values:
            value_counts[value] = value_counts.get(value, 0) + 1

        # 找到出现次数最多的值
        most_common = max(value_counts.items(), key=lambda x: x[1])
        return most_common

    @staticmethod
    def by_recency(sources: List[Dict]) -> Dict:
        """按时间戳解决冲突（使用最新的数据）

        Args:
            sources: 数据源列表

        Returns:
            时间戳最新的数据源
        """
        valid_sources = [s for s in sources if s.get('last_checked')]

        if not valid_sources:
            return sources[0] if sources else {}

        # 按时间戳降序排序
        sorted_sources = sorted(
            valid_sources,
            key=lambda x: x['last_checked'],
            reverse=True
        )

        return sorted_sources[0]


class DataValidator:
    """数据验证器 - 交叉验证会议数据"""

    # 验证规则配置
    VALIDATION_RULES = {
        'deadline': {
            'required': True,
            'min_sources': 1,
            'tolerance_days': 3,  # 允许的日期差异天数
        },
        'rank': {
            'required': True,
            'min_sources': 1,
            'valid_values': ['A', 'B', 'C', 'N/A'],
            'authoritative_sources': ['ccf_official', 'manual']
        },
        'name': {
            'required': True,
            'min_sources': 1,
            'similarity_threshold': 0.85  # 名称相似度阈值
        }
    }

    def __init__(self, sources_config: str = 'sources.json'):
        """初始化数据验证器

        Args:
            sources_config: 数据源配置文件路径
        """
        self.sources = self._load_sources(sources_config)
        self.resolver = ConflictResolver()

    def _load_sources(self, sources_file: str) -> List[Dict]:
        """加载数据源配置"""
        try:
            with open(sources_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('sources', [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def validate_all(self, multi_source_data: Dict[str, List[Dict]]) -> Dict:
        """验证所有会议数据

        Args:
            multi_source_data: {source_id: conferences_list} 格式的数据

        Returns:
            验证结果字典
        """
        print(f"🔍 开始验证 {len(multi_source_data)} 个数据源...")

        # 按会议名称分组
        grouped_conferences = self._group_by_name(multi_source_data)

        # 验证每个会议组
        results = {
            'total': len(grouped_conferences),
            'verified': [],
            'conflicts': [],
            'unverified': [],
            'statistics': {}
        }

        for conf_key, conf_group in grouped_conferences.items():
            validation_result = self.validate_conference_group(conf_key, conf_group)

            if validation_result['status'] == VerificationStatus.VERIFIED:
                results['verified'].append(validation_result)
            elif validation_result['status'] == VerificationStatus.CONFLICT:
                results['conflicts'].append(validation_result)
            else:
                results['unverified'].append(validation_result)

        # 计算统计信息
        results['statistics'] = self._calculate_statistics(results)

        # 打印摘要
        self._print_validation_summary(results)

        return results

    def validate_conference_group(self, conf_key: str, conf_group: List[Dict]) -> Dict:
        """验证一组同名会议

        Args:
            conf_key: 会议键（名称）
            conf_group: 同名会议的数据列表

        Returns:
            验证结果
        """
        sources = []
        conflicts = []

        # 收集所有数据源的信息
        for conf in conf_group:
            source_id = conf.get('source_id', 'unknown')
            sources.append({
                'source_id': source_id,
                'data': {
                    'name': conf.get('name'),
                    'deadline': conf.get('deadline'),
                    'rank': conf.get('rank'),
                    'website': conf.get('website'),
                    'conference_date': conf.get('conference_date')
                },
                'last_checked': datetime.now().strftime('%Y-%m-%d'),
                'priority': self._get_source_priority(source_id)
            })

        # 检测冲突
        if len(sources) >= 2:
            # 检查截止日期冲突
            deadline_conflict = self._check_deadline_conflict(sources)
            if deadline_conflict:
                conflicts.append(deadline_conflict)

            # 检查等级冲突
            rank_conflict = self._check_rank_conflict(sources)
            if rank_conflict:
                conflicts.append(rank_conflict)

        # 计算置信度
        confidence = self._calculate_confidence(sources, conflicts)

        # 确定验证状态
        if conflicts:
            status = VerificationStatus.CONFLICT
        elif confidence >= 0.8 and len(sources) >= 2:
            status = VerificationStatus.VERIFIED
        elif len(sources) >= 1:
            status = VerificationStatus.UNVERIFIED
        else:
            status = VerificationStatus.OUTDATED

        return {
            'key': conf_key,
            'name': conf_group[0].get('name', conf_key),
            'status': status.value,
            'sources': sources,
            'conflicts': conflicts,
            'confidence': confidence,
            'recommended_data': self._get_recommended_data(sources, conflicts)
        }

    def _group_by_name(self, multi_source_data: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """按会议名称分组

        Args:
            multi_source_data: 多源会议数据

        Returns:
            {conf_key: [conf_list]} 的字典
        """
        grouped = {}

        for source_id, conferences in multi_source_data.items():
            for conf in conferences:
                # 生成标准化键
                conf_key = self._generate_conf_key(conf.get('name', ''))

                if conf_key not in grouped:
                    grouped[conf_key] = []

                # 添加数据源ID
                conf['source_id'] = source_id
                grouped[conf_key].append(conf)

        return grouped

    def _generate_conf_key(self, name: str) -> str:
        """生成会议键（用于分组）

        Args:
            name: 会议名称

        Returns:
            标准化的会议键
        """
        # 移除年份和特殊字符
        key = re.sub(r'\b20\d{2}\b', '', name)  # 移除年份
        key = re.sub(r'[^a-zA-Z0-9]', '', key)  # 只保留字母数字
        key = key.lower().strip()

        return key

    def _check_deadline_conflict(self, sources: List[Dict]) -> Optional[Dict]:
        """检查截止日期冲突

        Args:
            sources: 数据源列表

        Returns:
            冲突信息（如果没有冲突返回None）
        """
        deadlines = []
        for source in sources:
            deadline = source.get('data', {}).get('deadline')
            if deadline:
                try:
                    deadline_date = datetime.strptime(deadline, '%Y-%m-%d')
                    deadlines.append((deadline, deadline_date, source['source_id']))
                except ValueError:
                    continue

        if len(deadlines) < 2:
            return None

        # 检查日期差异
        deadline_dates = [d[1] for d in deadlines]
        min_date = min(deadline_dates)
        max_date = max(deadline_dates)
        days_diff = (max_date - min_date).days

        tolerance = self.VALIDATION_RULES['deadline']['tolerance_days']

        if days_diff > tolerance:
            return {
                'type': ConflictType.DEADLINE_MISMATCH.value,
                'field': 'deadline',
                'values': [d[0] for d in deadlines],
                'sources': [d[2] for d in deadlines],
                'days_difference': days_diff,
                'severity': 'high' if days_diff > 7 else 'medium'
            }

        return None

    def _check_rank_conflict(self, sources: List[Dict]) -> Optional[Dict]:
        """检查等级冲突

        Args:
            sources: 数据源列表

        Returns:
            冲突信息（如果没有冲突返回None）
        """
        ranks = []
        for source in sources:
            rank = source.get('data', {}).get('rank')
            if rank and rank != 'N/A':
                ranks.append((rank, source['source_id']))

        if len(set(r[0] for r in ranks)) > 1:
            return {
                'type': ConflictType.RANK_MISMATCH.value,
                'field': 'rank',
                'values': [r[0] for r in ranks],
                'sources': [r[1] for r in ranks],
                'severity': 'medium'
            }

        return None

    def _calculate_confidence(self, sources: List[Dict], conflicts: List[Dict]) -> float:
        """计算置信度分数

        Args:
            sources: 数据源列表
            conflicts: 冲突列表

        Returns:
            置信度分数（0.0-1.0）
        """
        if not sources:
            return 0.0

        # 基础分数：数据源数量
        source_score = min(len(sources) * 0.3, 0.6)  # 最多0.6分

        # 权威源加分
        authoritative_count = sum(
            1 for s in sources
            if s['source_id'] in self.VALIDATION_RULES['rank']['authoritative_sources']
        )
        authority_score = min(authoritative_count * 0.2, 0.2)

        # 冲突扣分
        conflict_penalty = min(len(conflicts) * 0.3, 0.6)

        # 优先级分数（优先级高的数据源权重更高）
        priority_score = 0
        if sources:
            avg_priority = sum(s.get('priority', 999) for s in sources) / len(sources)
            priority_score = max(0, (10 - avg_priority) / 50)  # 转换为0-0.2的分数

        confidence = source_score + authority_score + priority_score - conflict_penalty

        return max(0.0, min(1.0, confidence))

    def _get_recommended_data(self, sources: List[Dict], conflicts: List[Dict]) -> Dict:
        """获取推荐的会议数据（解决冲突后）

        Args:
            sources: 数据源列表
            conflicts: 冲突列表

        Returns:
            推荐的会议数据
        """
        if not sources:
            return {}

        # 如果有冲突，使用解决策略
        if conflicts:
            # 按优先级选择
            best_source = self.resolver.by_priority(
                sources,
                self.VALIDATION_RULES['rank']['authoritative_sources']
            )
            return best_source.get('data', {})

        # 如果没有冲突，使用第一个数据源
        return sources[0].get('data', {})

    def _get_source_priority(self, source_id: str) -> int:
        """获取数据源优先级

        Args:
            source_id: 数据源ID

        Returns:
            优先级数值（越小越高）
        """
        for source in self.sources:
            if source['id'] == source_id:
                return source.get('priority', 999)
        return 999

    def _calculate_statistics(self, results: Dict) -> Dict:
        """计算统计信息

        Args:
            results: 验证结果

        Returns:
            统计信息字典
        """
        total = results['total']
        verified = len(results['verified'])
        conflicts = len(results['conflicts'])
        unverified = len(results['unverified'])

        return {
            'total_conferences': total,
            'verified_count': verified,
            'conflict_count': conflicts,
            'unverified_count': unverified,
            'verification_rate': f"{(verified / total * 100):.1f}%" if total > 0 else "0%",
            'conflict_rate': f"{(conflicts / total * 100):.1f}%" if total > 0 else "0%",
            'average_confidence': self._calculate_average_confidence(results)
        }

    def _calculate_average_confidence(self, results: Dict) -> float:
        """计算平均置信度

        Args:
            results: 验证结果

        Returns:
            平均置信度
        """
        all_results = (
            results['verified'] +
            results['conflicts'] +
            results['unverified']
        )

        if not all_results:
            return 0.0

        total_confidence = sum(r.get('confidence', 0) for r in all_results)
        return total_confidence / len(all_results)

    def _print_validation_summary(self, results: Dict):
        """打印验证摘要

        Args:
            results: 验证结果
        """
        stats = results['statistics']

        print(f"\n{'='*60}")
        print("📊 验证结果摘要")
        print(f"{'='*60}")
        print(f"总会议数: {stats['total_conferences']}")
        print(f"✅ 已验证: {stats['verified_count']} ({stats['verification_rate']})")
        print(f"⚠️  有冲突: {stats['conflict_count']} ({stats['conflict_rate']})")
        print(f"❓ 未验证: {stats['unverified_count']}")
        print(f"📈 平均置信度: {stats['average_confidence']:.2f}")
        print(f"{'='*60}")

    def save_report(self, results: Dict, filename: str):
        """保存验证报告

        Args:
            results: 验证结果
            filename: 报告文件名
        """
        report = {
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'statistics': results['statistics'],
            'verified': results['verified'],
            'conflicts': results['conflicts'],
            'unverified': results['unverified']
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"📄 验证报告已保存到: {filename}")

    def auto_fix_conflicts(self, conflicts: List[Dict], conferences: List[Dict]) -> int:
        """自动修复冲突（按优先级）

        Args:
            conflicts: 冲突列表
            conferences: 会议数据列表

        Returns:
            修复的冲突数量
        """
        fixed_count = 0

        for conflict in conflicts:
            if conflict.get('conflicts'):
                # 对于每个冲突，使用优先级最高的数据源
                recommended = conflict.get('recommended_data', {})
                if recommended:
                    # 更新会议数据
                    conf_key = conflict.get('key')
                    for conf in conferences:
                        if self._generate_conf_key(conf.get('name', '')) == conf_key:
                            # 更新字段
                            for field, value in recommended.items():
                                if value:  # 只更新非空值
                                    conf[field] = value
                            fixed_count += 1
                            break

        return fixed_count


def match_conference_name(name1: str, name2: str) -> float:
    """计算两个会议名称的相似度

    Args:
        name1: 第一个会议名称
        name2: 第二个会议名称

    Returns:
        相似度分数（0.0-1.0）
    """
    # 标准化名称
    def normalize(name: str) -> str:
        # 移除年份
        name = re.sub(r'\b20\d{2}\b', '', name)
        # 移除特殊字符，只保留字母数字
        name = re.sub(r'[^a-zA-Z0-9]', '', name)
        # 统一大小写
        name = name.lower().strip()
        return name

    norm1, norm2 = normalize(name1), normalize(name2)

    # 使用SequenceMatcher计算相似度
    return SequenceMatcher(None, norm1, norm2).ratio()


def main():
    """主函数 - 命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description='会议数据验证工具')
    parser.add_argument('--data', type=str, required=True,
                       help='多源数据文件（JSON格式）')
    parser.add_argument('--sources', type=str, default='sources.json',
                       help='数据源配置文件 (默认: sources.json)')
    parser.add_argument('--report', type=str,
                       help='保存验证报告到指定文件')
    parser.add_argument('--verbose', action='store_true',
                       help='显示详细信息')

    args = parser.parse_args()

    print("="*60)
    print("🔍 会议数据验证工具")
    print("="*60)

    # 加载数据
    try:
        with open(args.data, 'r', encoding='utf-8') as f:
            multi_source_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ 数据文件不存在: {args.data}")
        return 1
    except json.JSONDecodeError as e:
        print(f"❌ 数据文件格式错误: {e}")
        return 1

    # 创建验证器
    validator = DataValidator(args.sources)

    # 执行验证
    results = validator.validate_all(multi_source_data)

    # 显示详细冲突信息
    if args.verbose and results['conflicts']:
        print(f"\n⚠️  发现 {len(results['conflicts'])} 个冲突:")
        for i, conflict in enumerate(results['conflicts'][:10], 1):
            print(f"\n{i}. {conflict['name']}")
            for conf in conflict['conflicts']:
                print(f"   - {conf['type']}: {conf.get('values', [])}")

    # 保存报告
    if args.report:
        validator.save_report(results, args.report)

    print("="*60)
    return 0


if __name__ == '__main__':
    sys.exit(main())
