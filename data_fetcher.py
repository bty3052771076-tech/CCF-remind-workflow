#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据抓取器 - 使用Python标准库抓取会议信息
支持从多个数据源获取会议数据并进行标准化处理
"""

import urllib.request
import urllib.error
import json
import re
import sys
from datetime import datetime
from html.parser import HTMLParser
from typing import List, Dict, Optional
import time

# Windows控制台编码修复
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)


class DataFetcher:
    """数据抓取器 - 使用标准库urllib抓取网页数据"""

    def __init__(self, sources_file: str = 'sources.json'):
        """初始化数据抓取器

        Args:
            sources_file: 数据源配置文件路径
        """
        self.sources = self._load_sources(sources_file)
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        self.timeout = 30

    def _load_sources(self, sources_file: str) -> List[Dict]:
        """加载数据源配置"""
        try:
            with open(sources_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('sources', [])
        except FileNotFoundError:
            print(f"⚠️  数据源配置文件不存在: {sources_file}")
            print("   请先创建 sources.json 配置文件")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ 配置文件格式错误: {e}")
            return []

    def fetch_page(self, url: str, retries: int = 3) -> Optional[str]:
        """抓取网页内容（带重试机制）

        Args:
            url: 目标URL
            retries: 重试次数

        Returns:
            网页HTML内容（失败返回None）
        """
        for attempt in range(retries):
            try:
                req = urllib.request.Request(
                    url,
                    headers={
                        'User-Agent': self.user_agent,
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
                    }
                )

                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    # 尝试自动检测编码
                    content = response.read()

                    # 优先从HTTP头获取编码
                    charset = None
                    content_type = response.getheader('Content-Type', '')
                    if 'charset=' in content_type:
                        charset = content_type.split('charset=')[-1].strip()

                    # 如果没有找到编码，尝试从meta标签获取
                    if not charset:
                        try:
                            html = content.decode('utf-8', errors='ignore')
                            match = re.search(r'<meta[^>]+charset=["\']?([^"\'>\s]+)', html, re.I)
                            if match:
                                charset = match.group(1)
                        except:
                            pass

                    # 默认使用utf-8
                    if not charset:
                        charset = 'utf-8'

                    try:
                        return content.decode(charset)
                    except (UnicodeDecodeError, LookupError):
                        # 如果指定编码失败，尝试常见编码
                        for fallback_encoding in ['utf-8', 'gbk', 'gb2312', 'iso-8859-1']:
                            try:
                                return content.decode(fallback_encoding)
                            except:
                                continue

                        # 如果所有编码都失败，使用utf-8并忽略错误
                        return content.decode('utf-8', errors='ignore')

            except urllib.error.HTTPError as e:
                print(f"❌ HTTP错误 (尝试 {attempt + 1}/{retries}): {e.code} - {url}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                    continue
                return None

            except urllib.error.URLError as e:
                print(f"❌ 网络错误 (尝试 {attempt + 1}/{retries}): {e.reason} - {url}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None

            except Exception as e:
                print(f"❌ 未知错误 (尝试 {attempt + 1}/{retries}): {e} - {url}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None

        return None

    def fetch_from_source(self, source_id: str) -> List[Dict]:
        """从指定数据源获取数据

        Args:
            source_id: 数据源ID

        Returns:
            标准化后的会议数据列表
        """
        source = next((s for s in self.sources if s['id'] == source_id), None)
        if not source:
            print(f"❌ 未找到数据源: {source_id}")
            return []

        if not source.get('enabled', True):
            print(f"⏭️  数据源已禁用: {source_id}")
            return []

        print(f"📡 正在从 {source['name']} 抓取数据...")

        # 根据数据源类型选择解析器
        parser_type = source.get('parser', source_id)

        try:
            if parser_type == 'ccfddl':
                data = self._parse_ccfddl(source['url'])
            elif parser_type == 'ccf_official':
                data = self._parse_ccf_official(source['url'])
            elif parser_type == 'manual':
                # 手动数据源，直接返回预定义数据
                data = source.get('data', [])
            else:
                print(f"⚠️  不支持的解析器类型: {parser_type}")
                return []

            # 标准化数据
            normalized_data = [
                self.normalize_conference(conf, source_id)
                for conf in data
            ]

            print(f"✅ 成功抓取 {len(normalized_data)} 条数据")
            return normalized_data

        except Exception as e:
            print(f"❌ 抓取失败: {e}")
            import traceback
            traceback.print_exc()
            return []

    def fetch_all_enabled_sources(self) -> Dict[str, List[Dict]]:
        """从所有启用的数据源获取数据

        Returns:
            {source_id: conferences_list} 的字典
        """
        all_data = {}

        enabled_sources = [s for s in self.sources if s.get('enabled', True)]

        if not enabled_sources:
            print("⚠️  没有启用的数据源")
            return all_data

        print(f"📊 共有 {len(enabled_sources)} 个启用的数据源")

        for source in enabled_sources:
            print(f"\n{'='*60}")
            data = self.fetch_from_source(source['id'])
            all_data[source['id']] = data

        return all_data

    def _parse_ccfddl(self, url: str) -> List[Dict]:
        """解析ccfddl.top网站

        这是一个示例解析器，实际实现需要根据网站结构调整
        """
        print(f"🔍 正在解析 {url}...")

        html = self.fetch_page(url)
        if not html:
            return []

        # 使用正则表达式提取会议信息
        # 注意：这里是一个简化的示例，实际需要根据网站HTML结构调整
        conferences = []

        # 示例：提取包含会议信息的div
        # 实际实现时需要使用浏览器开发者工具查看网站结构
        pattern = re.compile(
            r'<div[^>]*class="[^"]*conf[^"]*"[^>]*>.*?'
            r'<h3[^>]*>(.*?)</h3>.*?'
            r'(?:deadline|截止)[^>]*>([^<]+)</span>.*?'
            r'(?:rank|等级)[^>]*>([ABC])</span>',
            re.DOTALL | re.IGNORECASE
        )

        matches = pattern.findall(html)

        for name, deadline, rank in matches:
            # 清理HTML标签
            name = re.sub(r'<[^>]+>', '', name).strip()
            deadline = re.sub(r'[^\d-]', '', deadline).strip()

            if name and deadline:
                conferences.append({
                    'name': name,
                    'deadline': deadline,
                    'rank': rank,
                    'conference_date': '',
                    'website': '',
                    'description': ''
                })

        return conferences

    def _parse_ccf_official(self, url: str) -> List[Dict]:
        """解析CCF官方网站

        这是一个示例解析器，实际实现需要根据网站结构调整
        """
        print(f"🔍 正在解析 {url}...")

        html = self.fetch_page(url)
        if not html:
            return []

        # CCF官网主要用于验证会议等级
        # 这里返回空列表，实际使用时需要根据官网结构实现解析
        print("⚠️  CCF官网解析器待实现")
        return []

    def normalize_conference(self, raw_conf: Dict, source_id: str) -> Dict:
        """标准化会议数据格式

        Args:
            raw_conf: 原始会议数据
            source_id: 数据源ID

        Returns:
            标准化后的会议数据
        """
        # 提取并清理截止日期
        deadline = raw_conf.get('deadline', '')
        if deadline:
            # 尝试多种日期格式
            date_patterns = [
                r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
                r'(\d{4})/(\d{1,2})/(\d{1,2})',  # YYYY/MM/DD
                r'(\d{1,2})-(\d{1,2})-(\d{4})',  # DD-MM-YYYY
            ]

            for pattern in date_patterns:
                match = re.search(pattern, deadline)
                if match:
                    groups = match.groups()
                    # 标准化为 YYYY-MM-DD 格式
                    if len(groups[0]) == 4:  # 年在前
                        deadline = f"{groups[0]}-{groups[1].zfill(2)}-{groups[2].zfill(2)}"
                    else:  # 年在后
                        deadline = f"{groups[2]}-{groups[1].zfill(2)}-{groups[0].zfill(2)}"
                    break

        # 清理会议名称
        name = raw_conf.get('name', '').strip()
        name = re.sub(r'\s+', ' ', name)  # 合并多个空格

        # 标准化等级
        rank = raw_conf.get('rank', '').upper().strip()
        if rank not in ['A', 'B', 'C']:
            rank = 'N/A'

        # 生成唯一ID
        conf_id = self._generate_conf_id(name, raw_conf.get('deadline', ''))

        normalized = {
            'id': conf_id,
            'name': name,
            'rank': rank,
            'deadline': deadline,
            'conference_date': raw_conf.get('conference_date', ''),
            'website': raw_conf.get('website', ''),
            'description': raw_conf.get('description', ''),
            'type': raw_conf.get('type', 'conference'),
            'fields': raw_conf.get('fields', []),
            'source_id': source_id,
            'raw_data': raw_conf  # 保留原始数据以便调试
        }

        return normalized

    def _generate_conf_id(self, name: str, deadline: str) -> str:
        """生成会议唯一ID

        Args:
            name: 会议名称
            deadline: 截止日期

        Returns:
            唯一ID字符串
        """
        # 提取会议缩写（通常是第一个词或连续大写字母）
        abbrev_match = re.search(r'\b([A-Z]{2,})\b', name)
        if abbrev_match:
            abbrev = abbrev_match.group(1).lower()
        else:
            # 如果没有找到缩写，使用第一个单词
            first_word = name.split()[0].lower()
            abbrev = re.sub(r'[^a-z0-9]', '', first_word)[:10]

        # 提取年份
        year_match = re.search(r'\b(20\d{2})\b', name + ' ' + deadline)
        year = year_match.group(1) if year_match else '0000'

        return f"{abbrev}-{year}"

    def save_to_file(self, data: List[Dict], filename: str):
        """保存数据到文件

        Args:
            data: 会议数据列表
            filename: 输出文件名
        """
        # 移除raw_data字段（仅用于调试）
        clean_data = [
            {k: v for k, v in conf.items() if k != 'raw_data'}
            for conf in data
        ]

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(clean_data, f, ensure_ascii=False, indent=2)

        print(f"💾 数据已保存到: {filename}")


class ConferenceHTMLParser(HTMLParser):
    """HTML解析器基类，用于解析会议网站"""

    def __init__(self):
        super().__init__()
        self.conferences = []
        self.current_conf = {}
        self.in_conference = False
        self.current_tag = None
        self.current_data = []

    def handle_starttag(self, tag, attrs):
        """处理开始标签"""
        attrs_dict = dict(attrs)

        # 检测是否进入会议项
        if tag in ['div', 'li', 'article']:
            classes = attrs_dict.get('class', '').split()
            if any(cls in ['conf', 'conference', 'item'] for cls in classes):
                self.in_conference = True
                self.current_conf = {}

        # 记录当前标签
        if self.in_conference:
            self.current_tag = tag

    def handle_endtag(self, tag):
        """处理结束标签"""
        # 检测是否离开会议项
        if tag in ['div', 'li', 'article'] and self.in_conference:
            self._save_current_conference()

        self.current_tag = None

    def handle_data(self, data):
        """处理文本数据"""
        if self.in_conference and self.current_tag:
            self.current_data.append(data.strip())

    def _save_current_conference(self):
        """保存当前会议"""
        if self.current_conf:
            self.conferences.append(self.current_conf)
            self.current_conf = {}
            self.in_conference = False


def main():
    """主函数 - 命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description='会议数据抓取工具')
    parser.add_argument('--sources', type=str, default='sources.json',
                       help='数据源配置文件 (默认: sources.json)')
    parser.add_argument('--source', type=str,
                       help='只抓取指定的数据源ID')
    parser.add_argument('--output', type=str,
                       help='输出文件名（JSON格式）')
    parser.add_argument('--verbose', action='store_true',
                       help='显示详细信息')

    args = parser.parse_args()

    print("="*60)
    print("📊 会议数据抓取工具")
    print("="*60)

    # 创建抓取器
    fetcher = DataFetcher(args.sources)

    # 抓取数据
    if args.source:
        # 抓取单个数据源
        data = fetcher.fetch_from_source(args.source)
        all_data = {args.source: data}
    else:
        # 抓取所有启用的数据源
        all_data = fetcher.fetch_all_enabled_sources()

    # 统计
    total_conferences = sum(len(confs) for confs in all_data.values())
    print(f"\n{'='*60}")
    print(f"📊 抓取完成！")
    print(f"   数据源数量: {len(all_data)}")
    print(f"   会议总数: {total_conferences}")

    for source_id, confs in all_data.items():
        print(f"   - {source_id}: {len(confs)} 条")

    # 保存到文件
    if args.output:
        # 合并所有数据源
        merged_data = []
        for source_id, confs in all_data.items():
            merged_data.extend(confs)

        fetcher.save_to_file(merged_data, args.output)

    print("="*60)


if __name__ == '__main__':
    main()
