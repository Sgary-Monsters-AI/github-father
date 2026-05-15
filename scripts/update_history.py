#!/usr/bin/env python3
"""
更新历史记录脚本
将新的 URL 追加到历史记录
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime


def update_history(urls, history_file):
    """更新历史记录"""
    # 读取或初始化历史记录
    if Path(history_file).exists():
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
    else:
        history = {'crawled_urls': []}

    # 确保 crawled_urls 存在
    if 'crawled_urls' not in history:
        history['crawled_urls'] = []

    # 追加新 URL（去重）
    existing_urls = set(history['crawled_urls'])
    new_urls = []

    for url in urls:
        if url not in existing_urls:
            history['crawled_urls'].append(url)
            new_urls.append(url)
            existing_urls.add(url)

    # 更新时间戳
    history['last_updated'] = datetime.now().isoformat()

    # 保存
    Path(history_file).parent.mkdir(parents=True, exist_ok=True)
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    return {
        'total_urls': len(history['crawled_urls']),
        'new_urls': len(new_urls),
        'updated': history['last_updated']
    }


def main():
    parser = argparse.ArgumentParser(description='更新历史记录脚本')
    parser.add_argument('--urls', required=True, help='URL 列表（逗号分隔）')
    parser.add_argument('--history-file', required=True, help='历史记录文件路径')

    args = parser.parse_args()

    # 解析 URL 列表
    urls = [url.strip() for url in args.urls.split(',') if url.strip()]

    # 更新历史记录
    result = update_history(urls, args.history_file)

    # 输出报告
    print("=" * 60)
    print("历史记录更新完成")
    print("=" * 60)
    print(f"新增 URL：{result['new_urls']} 个")
    print(f"历史总数：{result['total_urls']} 个")
    print(f"更新时间：{result['updated']}")
    print("=" * 60)

    # 返回 JSON 到 stdout
    print("\n--- JSON OUTPUT ---")
    print(json.dumps(result, ensure_ascii=False))

    return 0


if __name__ == '__main__':
    sys.exit(main())