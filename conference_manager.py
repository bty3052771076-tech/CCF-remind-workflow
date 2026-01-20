#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会议数据管理器 - 管理会议数据的加载、保存、合并和迁移
支持向后兼容和数据版本控制
"""

import json
import os
import re
import sys
import shutil
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Windows控制台编码修复
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)


class ConferenceManager:
    """会议数据管理器"""

    def __init__(self, data_file: str = 'conferences.json'):
        """初始化会议管理器

        Args:
            data_file: 会议数据文件路径
        """
        self.data_file = data_file
        self.backup_dir = 'backups'
        self.conferences = []
        self.metadata = {
            'version': '2.0',
            'last_updated': None,
            'total_count': 0
        }

        # 确保备份目录存在
        os.makedirs(self.backup_dir, exist_ok=True)

        # 加载数据
        self.load_data()

    def load_data(self) -> List[Dict]:
        """加载会议数据（兼容旧格式）

        Returns:
            会议数据列表
        """
        if not os.path.exists(self.data_file):
            print(f"⚠️  数据文件不存在: {self.data_file}")
            self.conferences = []
            return self.conferences

        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 检查是否为新格式
            if isinstance(data, dict) and 'conferences' in data:
                # 新格式：包含 metadata
                self.conferences = data['conferences']
                self.metadata = data.get('metadata', {})
            elif isinstance(data, list):
                # 旧格式：直接是会议列表
                self.conferences = data
                # 迁移到新格式
                self.conferences = [self.migrate_old_format(conf) for conf in self.conferences]
            else:
                print(f"❌ 未知的数据格式")
                self.conferences = []

            print(f"✅ 成功加载 {len(self.conferences)} 个会议")
            return self.conferences

        except json.JSONDecodeError as e:
            print(f"❌ 数据文件格式错误: {e}")
            self.conferences = []
            return self.conferences

    def save_data(self, create_backup: bool = True) -> bool:
        """保存会议数据

        Args:
            create_backup: 是否创建备份

        Returns:
            保存是否成功
        """
        try:
            # 创建备份
            if create_backup and os.path.exists(self.data_file):
                self._create_backup()

            # 更新元数据
            self.metadata['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.metadata['total_count'] = len(self.conferences)

            # 保存数据（新格式）
            data = {
                'conferences': self.conferences,
                'metadata': self.metadata
            }

            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"💾 数据已保存到: {self.data_file}")
            print(f"   总计: {len(self.conferences)} 个会议")
            return True

        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return False

    def add_conference(self, conference: Dict, source_id: str = 'manual') -> bool:
        """添加单个会议

        Args:
            conference: 会议数据
            source_id: 数据源ID

        Returns:
            是否添加成功
        """
        try:
            # 生成ID（如果没有）
            if 'id' not in conference:
                conference['id'] = self._generate_conf_id(conference)

            # 添加验证信息
            if 'verification' not in conference:
                conference['verification'] = {
                    'status': 'unverified',
                    'sources': [{
                        'source_id': source_id,
                        'last_checked': datetime.now().strftime('%Y-%m-%d'),
                        'data': {k: v for k, v in conference.items()
                                if k not in ['verification', 'metadata']}
                    }],
                    'conflicts': [],
                    'confidence': 0.5
                }

            # 添加元数据
            if 'metadata' not in conference:
                conference['metadata'] = {
                    'created_at': datetime.now().strftime('%Y-%m-%d'),
                    'updated_at': datetime.now().strftime('%Y-%m-%d'),
                    'updated_by': source_id
                }

            # 检查是否已存在
            existing = self.find_conference(conference['id'])
            if existing:
                print(f"⚠️  会议已存在: {conference['name']}")
                return False

            self.conferences.append(conference)
            print(f"✅ 已添加会议: {conference['name']}")
            return True

        except Exception as e:
            print(f"❌ 添加会议失败: {e}")
            return False

    def update_conference(self, conf_id: str, update_data: Dict,
                         source_id: str = 'manual') -> bool:
        """更新会议信息

        Args:
            conf_id: 会议ID
            update_data: 要更新的数据
            source_id: 数据源ID

        Returns:
            是否更新成功
        """
        try:
            conf = self.find_conference(conf_id)
            if not conf:
                print(f"❌ 未找到会议: {conf_id}")
                return False

            # 更新字段
            for key, value in update_data.items():
                if value is not None:  # 只更新非空值
                    conf[key] = value

            # 更新元数据
            if 'metadata' in conf:
                conf['metadata']['updated_at'] = datetime.now().strftime('%Y-%m-%d')
                conf['metadata']['updated_by'] = source_id

            print(f"✅ 已更新会议: {conf.get('name', conf_id)}")
            return True

        except Exception as e:
            print(f"❌ 更新会议失败: {e}")
            return False

    def delete_conference(self, conf_id: str) -> bool:
        """删除会议

        Args:
            conf_id: 会议ID

        Returns:
            是否删除成功
        """
        try:
            conf = self.find_conference(conf_id)
            if not conf:
                print(f"❌ 未找到会议: {conf_id}")
                return False

            self.conferences.remove(conf)
            print(f"✅ 已删除会议: {conf.get('name', conf_id)}")
            return True

        except Exception as e:
            print(f"❌ 删除会议失败: {e}")
            return False

    def find_conference(self, conf_id: str) -> Optional[Dict]:
        """查找会议

        Args:
            conf_id: 会议ID

        Returns:
            会议数据（未找到返回None）
        """
        for conf in self.conferences:
            if conf.get('id') == conf_id:
                return conf
        return None

    def merge_data(self, new_data: List[Dict], source_id: str = 'merged',
                   update_existing: bool = True) -> Dict:
        """合并新数据

        Args:
            new_data: 新会议数据列表
            source_id: 数据源ID
            update_existing: 是否更新已存在的会议

        Returns:
            合并统计信息
        """
        stats = {
            'added': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }

        for new_conf in new_data:
            try:
                # 生成ID
                conf_id = new_conf.get('id') or self._generate_conf_id(new_conf)

                # 检查是否已存在
                existing = self.find_conference(conf_id)

                if existing:
                    if update_existing:
                        # 更新已存在的会议
                        self.update_conference(conf_id, new_conf, source_id)
                        stats['updated'] += 1
                    else:
                        stats['skipped'] += 1
                else:
                    # 添加新会议
                    self.add_conference(new_conf, source_id)
                    stats['added'] += 1

            except Exception as e:
                print(f"❌ 合并会议失败: {e}")
                stats['errors'] += 1

        return stats

    def migrate_old_format(self, old_conf: Dict) -> Dict:
        """迁移旧格式数据到新格式

        Args:
            old_conf: 旧格式会议数据

        Returns:
            新格式会议数据
        """
        # 如果已经是新格式，直接返回
        if 'verification' in old_conf and 'metadata' in old_conf:
            return old_conf

        # 生成ID
        conf_id = self._generate_conf_id(old_conf)

        # 迁移到新格式
        new_conf = {
            'id': conf_id,
            'name': old_conf.get('name', ''),
            'rank': old_conf.get('rank', 'N/A'),
            'deadline': old_conf.get('deadline', ''),
            'conference_date': old_conf.get('conference_date', ''),
            'website': old_conf.get('website', ''),
            'description': old_conf.get('description', ''),
            'type': old_conf.get('type', 'conference'),
            'fields': old_conf.get('fields', []),
            'verification': {
                'status': 'unverified',
                'sources': [{
                    'source_id': 'legacy',
                    'last_checked': datetime.now().strftime('%Y-%m-%d'),
                    'data': {
                        'name': old_conf.get('name'),
                        'deadline': old_conf.get('deadline'),
                        'rank': old_conf.get('rank')
                    }
                }],
                'conflicts': [],
                'confidence': 0.5
            },
            'metadata': {
                'created_at': old_conf.get('created_at', datetime.now().strftime('%Y-%m-%d')),
                'updated_at': datetime.now().strftime('%Y-%m-%d'),
                'updated_by': 'migration'
            }
        }

        return new_conf

    def filter_conferences(self, **filters) -> List[Dict]:
        """筛选会议

        Args:
            **filters: 筛选条件
                - rank: CCF等级（A/B/C）
                - field: 研究领域
                - type: 类型（conference/journal）
                - days_after: 截止日期在多少天后
                - days_before: 截止日期在多少天前

        Returns:
            筛选后的会议列表
        """
        filtered = self.conferences

        # 按等级筛选
        if 'rank' in filters:
            rank = filters['rank'].upper()
            if rank in ['A', 'B', 'C']:
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

        # 按截止日期筛选
        if 'days_after' in filters or 'days_before' in filters:
            from datetime import datetime, timedelta

            today = datetime.now()
            filtered = [
                c for c in filtered
                if c.get('deadline')
            ]

            if 'days_after' in filters:
                days = filters['days_after']
                deadline_date = today + timedelta(days=days)
                filtered = [
                    c for c in filtered
                    if datetime.strptime(c['deadline'], '%Y-%m-%d') <= deadline_date
                ]

            if 'days_before' in filters:
                days = filters['days_before']
                deadline_date = today + timedelta(days=days)
                filtered = [
                    c for c in filtered
                    if datetime.strptime(c['deadline'], '%Y-%m-%d') >= deadline_date
                ]

        return filtered

    def get_statistics(self) -> Dict:
        """获取统计信息

        Returns:
            统计信息字典
        """
        from datetime import datetime

        total = len(self.conferences)

        # 按等级统计
        rank_stats = {'A': 0, 'B': 0, 'C': 0, 'N/A': 0}
        for conf in self.conferences:
            rank = conf.get('rank', 'N/A')
            if rank in rank_stats:
                rank_stats[rank] += 1

        # 按类型统计
        type_stats = {'conference': 0, 'journal': 0, 'workshop': 0}
        for conf in self.conferences:
            conf_type = conf.get('type', 'conference')
            type_stats[conf_type] = type_stats.get(conf_type, 0) + 1

        # 按验证状态统计
        verification_stats = {
            'verified': 0,
            'conflict': 0,
            'unverified': 0,
            'outdated': 0
        }
        for conf in self.conferences:
            status = conf.get('verification', {}).get('status', 'unverified')
            verification_stats[status] = verification_stats.get(status, 0) + 1

        # 即将截止的会议（30天内）
        upcoming_count = 0
        today = datetime.now()
        thirty_days_later = today + timedelta(days=30)

        for conf in self.conferences:
            if conf.get('deadline'):
                try:
                    deadline = datetime.strptime(conf['deadline'], '%Y-%m-%d')
                    if today <= deadline <= thirty_days_later:
                        upcoming_count += 1
                except ValueError:
                    continue

        return {
            'total': total,
            'by_rank': rank_stats,
            'by_type': type_stats,
            'by_verification': verification_stats,
            'upcoming_30days': upcoming_count,
            'last_updated': self.metadata.get('last_updated', 'Unknown')
        }

    def _generate_conf_id(self, conf: Dict) -> str:
        """生成会议唯一ID

        Args:
            conf: 会议数据

        Returns:
            唯一ID
        """
        name = conf.get('name', '')
        deadline = conf.get('deadline', '')

        # 提取缩写
        abbrev_match = re.search(r'\b([A-Z]{2,})\b', name)
        if abbrev_match:
            abbrev = abbrev_match.group(1).lower()
        else:
            first_word = name.split()[0].lower() if name else 'conf'
            abbrev = re.sub(r'[^a-z0-9]', '', first_word)[:10]

        # 提取年份
        year_match = re.search(r'\b(20\d{2})\b', name + ' ' + deadline)
        year = year_match.group(1) if year_match else '0000'

        return f"{abbrev}-{year}"

    def _create_backup(self) -> str:
        """创建备份文件

        Returns:
            备份文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"conferences_backup_{timestamp}.json"
        backup_path = os.path.join(self.backup_dir, backup_filename)

        shutil.copy2(self.data_file, backup_path)
        print(f"💾 备份已创建: {backup_path}")

        return backup_path

    def list_backups(self, limit: int = 10) -> List[str]:
        """列出备份文件

        Args:
            limit: 最多返回多少个备份

        Returns:
            备份文件路径列表
        """
        if not os.path.exists(self.backup_dir):
            return []

        backups = [
            os.path.join(self.backup_dir, f)
            for f in os.listdir(self.backup_dir)
            if f.startswith('conferences_backup_') and f.endswith('.json')
        ]

        # 按修改时间降序排序
        backups.sort(key=lambda x: os.path.getmtime(x), reverse=True)

        return backups[:limit]

    def restore_backup(self, backup_path: str) -> bool:
        """从备份恢复

        Args:
            backup_path: 备份文件路径

        Returns:
            是否恢复成功
        """
        try:
            if not os.path.exists(backup_path):
                print(f"❌ 备份文件不存在: {backup_path}")
                return False

            # 先备份当前数据
            self._create_backup()

            # 恢复数据
            shutil.copy2(backup_path, self.data_file)

            # 重新加载数据
            self.load_data()

            print(f"✅ 已从备份恢复: {backup_path}")
            return True

        except Exception as e:
            print(f"❌ 恢复备份失败: {e}")
            return False


def main():
    """主函数 - 命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description='会议数据管理工具')
    parser.add_argument('--file', type=str, default='conferences.json',
                       help='会议数据文件 (默认: conferences.json)')
    parser.add_argument('--stats', action='store_true',
                       help='显示统计信息')
    parser.add_argument('--migrate', action='store_true',
                       help='迁移旧格式数据到新格式')
    parser.add_argument('--backup', action='store_true',
                       help='创建备份')
    parser.add_argument('--list-backups', action='store_true',
                       help='列出备份文件')
    parser.add_argument('--restore', type=str,
                       help='从指定备份恢复')

    args = parser.parse_args()

    print("="*60)
    print("🗂️  会议数据管理工具")
    print("="*60)

    # 创建管理器
    manager = ConferenceManager(args.file)

    # 显示统计信息
    if args.stats:
        stats = manager.get_statistics()
        print(f"\n📊 数据统计:")
        print(f"   总数: {stats['total']}")
        print(f"   按等级: A={stats['by_rank']['A']}, "
              f"B={stats['by_rank']['B']}, C={stats['by_rank']['C']}")
        print(f"   按类型: 会议={stats['by_type']['conference']}, "
              f"期刊={stats['by_type']['journal']}")
        print(f"   验证状态: 已验证={stats['by_verification']['verified']}, "
              f"有冲突={stats['by_verification']['conflict']}")
        print(f"   即将截止(30天): {stats['upcoming_30days']}")
        print(f"   最后更新: {stats['last_updated']}")

    # 迁移数据
    if args.migrate:
        print("\n🔄 正在迁移数据...")
        manager.save_data(create_backup=True)
        print("✅ 数据迁移完成")

    # 创建备份
    if args.backup:
        print("\n💾 正在创建备份...")
        backup_path = manager._create_backup()
        print(f"✅ 备份已创建: {backup_path}")

    # 列出备份
    if args.list_backups:
        print("\n📋 备份文件列表:")
        backups = manager.list_backups()
        if backups:
            for i, backup in enumerate(backups, 1):
                mtime = datetime.fromtimestamp(os.path.getmtime(backup))
                size = os.path.getsize(backup) / 1024  # KB
                print(f"   {i}. {os.path.basename(backup)}")
                print(f"      时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')}, "
                      f"大小: {size:.1f} KB")
        else:
            print("   (无备份文件)")

    # 恢复备份
    if args.restore:
        print(f"\n🔄 正在从备份恢复: {args.restore}")
        manager.restore_backup(args.restore)

    print("="*60)


if __name__ == '__main__':
    main()
