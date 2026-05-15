#!/usr/bin/env python3
"""
质量评估脚本
对项目进行 100 分制评分
"""

import json
import sys
import argparse


def evaluate_project(project):
    """评估单个项目"""
    score = 0
    details = {}

    # 1. 实用性 (30%)
    utility_score = 0
    if project.get('description'):
        utility_score += 10
    if project.get('features') and len(project['features']) >= 3:
        utility_score += 10
    if project.get('target_audience'):
        utility_score += 10
    details['实用性'] = f"{utility_score}/30"
    score += utility_score

    # 2. 开源性 (20%)
    opensource_score = 0
    license = project.get('license', '').lower()
    if license in ['mit', 'apache-2.0', 'apache 2.0', 'bsd', 'gpl']:
        opensource_score = 20
    elif license:
        opensource_score = 10
    details['开源性'] = f"{opensource_score}/20"
    score += opensource_score

    # 3. 易用性 (20%)
    usability_score = 0
    if project.get('deployment'):
        if 'docker' in project['deployment'].lower() or '一键' in project['deployment']:
            usability_score += 10
        else:
            usability_score += 5
    if project.get('documentation'):
        usability_score += 10
    details['易用性'] = f"{usability_score}/20"
    score += usability_score

    # 4. 创新性 (15%)
    innovation_score = 0
    if project.get('differentiation'):
        innovation_score = 15
    elif project.get('features'):
        innovation_score = 8
    details['创新性'] = f"{innovation_score}/15"
    score += innovation_score

    # 5. 活跃度 (15%)
    activity_score = 0
    stars = project.get('stars', 0)
    if isinstance(stars, str):
        stars = stars.replace(',', '').strip()
        if 'k' in stars.lower():
            stars = float(stars.lower().replace('k', '')) * 1000
        stars = int(stars)

    if stars >= 10000:
        activity_score = 15
    elif stars >= 5000:
        activity_score = 12
    elif stars >= 1000:
        activity_score = 9
    elif stars >= 500:
        activity_score = 6
    else:
        activity_score = 3
    details['活跃度'] = f"{activity_score}/15"
    score += activity_score

    return {
        'url': project['url'],
        'name': project.get('name', ''),
        'score': score,
        'details': details
    }


def main():
    parser = argparse.ArgumentParser(description='质量评估脚本')
    parser.add_argument('--projects-json', required=True, help='项目信息 JSON 文件')
    parser.add_argument('--threshold', type=int, default=75, help='通过阈值（默认 75）')
    parser.add_argument('--output', help='输出 JSON 文件路径（可选）')

    args = parser.parse_args()

    # 读取项目信息
    with open(args.projects_json, 'r', encoding='utf-8') as f:
        projects = json.load(f)

    # 评估所有项目
    results = []
    for project in projects:
        result = evaluate_project(project)
        results.append(result)

    # 过滤
    qualified = [r for r in results if r['score'] >= args.threshold]
    rejected = [r for r in results if r['score'] < args.threshold]

    # 输出报告
    print("=" * 60)
    print("质量评估报告")
    print("=" * 60)

    for result in results:
        print(f"\n项目：{result['name']}")
        print(f"评分：{result['score']}/100")
        for dim, score in result['details'].items():
            print(f"  {dim}：{score}")
        if result['score'] >= args.threshold:
            print("  结论：✓ 通过")
        else:
            print("  结论：✗ 未通过")

    print("\n" + "=" * 60)
    print(f"总项目数：{len(results)}")
    print(f"通过评估：{len(qualified)} ({len(qualified)/len(results)*100:.1f}%)")
    print(f"未通过：{len(rejected)} ({len(rejected)/len(results)*100:.1f}%)")
    print(f"平均评分：{sum(r['score'] for r in results)/len(results):.1f}/100")
    print("=" * 60)

    # 输出结果
    output_data = {
        'qualified_projects': [projects[i] for i, r in enumerate(results) if r['score'] >= args.threshold],
        'rejected_projects': [projects[i] for i, r in enumerate(results) if r['score'] < args.threshold],
        'scores': results,
        'average_score': sum(r['score'] for r in results) / len(results)
    }

    # 保存到文件（如果指定）
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"\n结果已保存到：{args.output}")

    # 返回 JSON 到 stdout
    print("\n--- JSON OUTPUT ---")
    print(json.dumps(output_data, ensure_ascii=False))

    return 0


if __name__ == '__main__':
    sys.exit(main())