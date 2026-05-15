#!/usr/bin/env python3
"""
项目分配脚本
将项目分配给 3 个 agents
"""

import json
import sys
import argparse


def distribute_projects(projects):
    """将项目分配给 3 个 agents"""
    total = len(projects)
    base = total // 3
    remainder = total % 3

    # 计算每个 agent 的项目数
    agent_a_count = base + (1 if remainder >= 1 else 0)
    agent_b_count = base + (1 if remainder >= 2 else 0)
    agent_c_count = base

    # 分配项目
    distribution = {
        'agent_a': {
            'template': 'pain_driven',
            'count': agent_a_count,
            'projects': projects[:agent_a_count]
        },
        'agent_b': {
            'template': 'scene_based',
            'count': agent_b_count,
            'projects': projects[agent_a_count:agent_a_count + agent_b_count]
        },
        'agent_c': {
            'template': 'github_direct',
            'count': agent_c_count,
            'projects': projects[agent_a_count + agent_b_count:]
        }
    }

    return distribution


def main():
    parser = argparse.ArgumentParser(description='项目分配脚本')
    parser.add_argument('--projects-json', required=True, help='项目信息 JSON 文件')
    parser.add_argument('--output', required=True, help='输出 JSON 文件路径')

    args = parser.parse_args()

    # 读取项目信息
    with open(args.projects_json, 'r', encoding='utf-8') as f:
        projects = json.load(f)

    # 分配项目
    distribution = distribute_projects(projects)

    # 输出报告
    print("=" * 60)
    print("项目分配报告")
    print("=" * 60)
    print(f"\n总项目数：{len(projects)}")
    print(f"\nAgent A (痛点驱动型)：{distribution['agent_a']['count']} 个项目")
    print(f"Agent B (场景描述式)：{distribution['agent_b']['count']} 个项目")
    print(f"Agent C (GitHub 直入式)：{distribution['agent_c']['count']} 个项目")
    print("=" * 60)

    # 保存到文件
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(distribution, f, indent=2, ensure_ascii=False)

    print(f"\n分配结果已保存到：{args.output}")

    # 返回 JSON 到 stdout
    print("\n--- JSON OUTPUT ---")
    print(json.dumps(distribution, ensure_ascii=False))

    return 0


if __name__ == '__main__':
    sys.exit(main())