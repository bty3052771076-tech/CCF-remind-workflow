#!/bin/bash
# CCF会议提醒系统 - 快速使用示例脚本
# 演示如何使用新增的数据验证功能

echo "======================================"
echo "CCF会议提醒系统 v2.0 - 使用示例"
echo "======================================"
echo ""

# 1. 查看当前会议数据统计
echo "1️⃣  查看会议数据统计"
echo "   命令: python conference_manager.py --stats"
python conference_manager.py --stats
echo ""

# 2. 创建数据备份
echo "2️⃣  创建数据备份"
echo "   命令: python conference_manager.py --backup"
python conference_manager.py --backup
echo ""

# 3. 查看备份文件
echo "3️⃣  列出备份文件"
echo "   命令: python conference_manager.py --list-backups"
python conference_manager.py --list-backups
echo ""

# 4. 测试数据抓取器（需要网络连接）
echo "4️⃣  测试数据抓取器"
echo "   命令: python data_fetcher.py --help"
python data_fetcher.py --help
echo ""

# 5. 测试数据验证器
echo "5️⃣  测试数据验证器"
echo "   命令: python data_validator.py --help"
python data_validator.py --help
echo ""

echo "======================================"
echo "✅ 示例运行完成！"
echo "======================================"
echo ""
echo "📚 更多功能请查看："
echo "   - DATA_VALIDATION.md（数据验证功能文档）"
echo "   - README.md（总体说明）"
echo ""
