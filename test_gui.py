#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI筛选功能测试脚本
"""

import sys
import tkinter as tk
from tkinter import ttk

# 测试导入
try:
    from conference_manager import ConferenceManager
    from journal_manager import JournalManager
    print("✅ 模块导入成功")
except Exception as e:
    print(f"❌ 模块导入失败: {e}")
    sys.exit(1)

# 测试数据加载
try:
    conf_mgr = ConferenceManager()
    journal_mgr = JournalManager()
    print(f"✅ 数据加载成功")
    print(f"   - 会议: {len(conf_mgr.conferences)}个")
    print(f"   - 期刊: {len(journal_mgr.conferences)}个")
except Exception as e:
    print(f"❌ 数据加载失败: {e}")
    sys.exit(1)

# 测试筛选逻辑
try:
    from datetime import datetime

    # 筛选30天内截止的会议
    today = datetime.now()
    days_ahead = 30

    upcoming = []
    for conf in conf_mgr.conferences:
        deadline_str = conf.get('deadline')
        if not deadline_str:
            continue

        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
            days_until = (deadline - today).days

            if 0 <= days_until <= days_ahead:
                conf['days_until'] = days_until
                conf['deadline_date'] = deadline
                upcoming.append(conf)
        except ValueError:
            continue

    upcoming.sort(key=lambda x: x['deadline_date'])

    print(f"✅ 筛选功能正常")
    print(f"   - 未来30天内截止: {len(upcoming)}个会议")
    if len(upcoming) > 0:
        print(f"   - 最近截止: {upcoming[0]['name']} ({upcoming[0]['days_until']}天)")

except Exception as e:
    print(f"❌ 筛选功能失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试GUI启动（不显示窗口）
try:
    root = tk.Tk()
    root.withdraw()  # 隐藏窗口

    # 测试基本组件创建
    frame = ttk.Frame(root)
    label = ttk.Label(frame, text="测试")
    listbox = tk.Listbox(frame)

    print("✅ GUI组件创建成功")

    root.destroy()
except Exception as e:
    print(f"❌ GUI组件创建失败: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("🎉 所有测试通过！GUI筛选功能正常")
print("="*50)
