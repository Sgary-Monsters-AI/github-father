#!/usr/bin/env python3
"""
去重验证脚本
检查项目 URL 是否已在历史记录中
"""

import json
import sys
import argparse
from pathlib import Path


def load_history(history_file):
    """加载历史记录"""
    if not Path(history_file).exists():
        return {"crawled_urls": [], "last_updated": None}

    with open(history_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def deduplicate(urls, history_file):
    """去重验证"""
    history = load_history(history_file)
    history_urls = set(history.get('crawled_urls', []))

    new_urls = []
    duplicates = []

    for url in urls:
        if url in history_urls:
            duplicates.append(url)
        else:
            new_urls.append(url)

    return {
        "total": len(urls),
        "duplicates": len(duplicates),
        "new_projects": len(new_urls),
        "new_urls": new_urls,
        "duplicate_urls": duplicates
    }


def main():
    parser = argparse.ArgumentParser(description='去重验证脚本')
    parser.add_argument('--urls', required=True, help='项目 URL 列表（逗号分隔）')
    parser.add_argument('--history-file', required=True, help='历史记录文件路径')
    parser.add_argument('--output', help='输出 JSON 文件路径（可选）')

    args = parser.parse_args()

    # 解析 URL 列表
    urls = [url.strip() for url in args.urls.split(',') if url.strip()]

    # 去重验证
    result = deduplicate(urls, args.history_file)

    # 输出结果
    print("=" * 60)
    print(f"爬取总数：{result['total']} 个")
    print(f"重复（跳过）：{result['duplicates']} 个")
    print(f"新增（待处理）：{result['new_projects']} 个")
    print("=" * 60)

    if result['duplicate_urls']:
        print("\n✗ 重复项目（已在历史记录中）：")
        for url in result['duplicate_urls']:
            print(f"  {url}")

    if result['new_urls']:
        print("\n✓ 新项目（继续处理）：")
        for url in result['new_urls']:
            print(f"  {url}")

    # 保存到文件（如果指定）
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n结果已保存到：{args.output}")

    # 返回 JSON 到 stdout（供 Claude 读取）
    print("\n--- JSON OUTPUT ---")
    print(json.dumps(result, ensure_ascii=False))

    return 0


if __name__ == '__main__':
    sys.exit(main())