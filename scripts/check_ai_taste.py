#!/usr/bin/env python3
"""
AI 味检查脚本
检查并修复推文中的 AI 味问题
"""

import json
import sys
import argparse
import re


# 禁用词汇
FORBIDDEN_WORDS = {
    '填充短语': ['此外', '值得注意的是', '不可否认', '毋庸置疑'],
    '空洞形容词': ['充满活力', '持久的', '关键性的', '不断演变', '格局'],
    '程度副词': ['非常', '十分', '极其', '完全', '真正'],
    '营销话术': ['不容错过', '必备神器', '强烈推荐']
}

# 禁用句式模式
FORBIDDEN_PATTERNS = [
    (r'不仅.*?而且', '二元对比'),
    (r'从.*?到', '虚假范围'),
    (r'这就是', '升华结尾'),
    (r'这才是', '升华结尾'),
]


def check_forbidden_words(text):
    """检查禁用词汇"""
    issues = []
    for category, words in FORBIDDEN_WORDS.items():
        for word in words:
            if word in text:
                issues.append({
                    'type': '禁用词汇',
                    'category': category,
                    'word': word,
                    'fix': f'删除"{word}"'
                })
    return issues


def check_forbidden_patterns(text):
    """检查禁用句式"""
    issues = []
    for pattern, name in FORBIDDEN_PATTERNS:
        if re.search(pattern, text):
            issues.append({
                'type': '禁用句式',
                'pattern': name,
                'fix': f'重写{name}句式'
            })
    return issues


def check_format(text):
    """检查格式问题"""
    issues = []

    # 检查感叹号
    exclamation_count = text.count('！')
    if exclamation_count > 1:
        issues.append({
            'type': '格式问题',
            'issue': f'感叹号使用 {exclamation_count} 次',
            'fix': f'删除 {exclamation_count - 1} 个感叹号'
        })

    # 检查数字编号
    if re.search(r'[1-9]\.\s', text):
        issues.append({
            'type': '格式问题',
            'issue': '使用数字编号列表',
            'fix': '改用 • 符号'
        })

    # 检查禁止开头
    if text.startswith('发现一个'):
        issues.append({
            'type': '格式问题',
            'issue': '"发现一个"开头',
            'fix': '更换开场方式'
        })

    return issues


def auto_fix(text, issues):
    """自动修复问题"""
    fixed_text = text

    for issue in issues:
        if issue['type'] == '禁用词汇':
            fixed_text = fixed_text.replace(issue['word'], '')
        elif issue['type'] == '格式问题':
            if '感叹号' in issue['issue']:
                # 只保留第一个感叹号
                parts = fixed_text.split('！')
                fixed_text = parts[0] + '！' + ''.join(parts[1:]).replace('！', '。')
            elif '数字编号' in issue['issue']:
                # 替换数字编号为 •
                fixed_text = re.sub(r'([1-9])\.\s', r'• ', fixed_text)

    return fixed_text


def calculate_score(issues):
    """计算 AI 味评分"""
    score = 0
    for issue in issues:
        if issue['type'] == '禁用词汇':
            score += 0.5
        elif issue['type'] == '禁用句式':
            score += 1
        elif issue['type'] == '格式问题':
            score += 1
    return min(score, 10)


def check_tweet(tweet):
    """检查单条推文"""
    issues = []
    issues.extend(check_forbidden_words(tweet))
    issues.extend(check_forbidden_patterns(tweet))
    issues.extend(check_format(tweet))

    score = calculate_score(issues)
    fixed = auto_fix(tweet, issues) if issues else tweet

    return {
        'original': tweet,
        'fixed': fixed,
        'score': score,
        'issues': [f"{i['type']}: {i.get('word', i.get('pattern', i.get('issue')))}" for i in issues]
    }


def main():
    parser = argparse.ArgumentParser(description='AI 味检查脚本')
    parser.add_argument('--tweets-json', required=True, help='推文 JSON 文件')
    parser.add_argument('--threshold', type=int, default=5, help='AI 味阈值（默认 5）')
    parser.add_argument('--output', help='输出 JSON 文件路径（可选）')

    args = parser.parse_args()

    # 读取推文
    with open(args.tweets_json, 'r', encoding='utf-8') as f:
        tweets = json.load(f)

    # 检查所有推文
    results = []
    for tweet in tweets:
        # 如果是字典，提取 content 字段
        if isinstance(tweet, dict):
            tweet_content = tweet.get('content', '')
            tweet_project = tweet.get('project', '')
            tweet_url = tweet.get('url', '')
        else:
            tweet_content = tweet
            tweet_project = ''
            tweet_url = ''

        result = check_tweet(tweet_content)
        result['project'] = tweet_project
        result['url'] = tweet_url
        results.append(result)

    # 输出报告
    print("=" * 60)
    print("AI 味检查报告")
    print("=" * 60)

    for i, result in enumerate(results, 1):
        print(f"\n推文 {i}:")
        print(f"AI 味评分：{result['score']}/10")
        if result['issues']:
            print("检测到的问题：")
            for issue in result['issues']:
                print(f"  ✗ {issue}")
            print(f"已自动修复")
        else:
            print("  ✓ 无问题")

    avg_score = sum(r['score'] for r in results) / len(results)
    print("\n" + "=" * 60)
    print(f"平均 AI 味评分：{avg_score:.1f}/10")
    if avg_score <= args.threshold:
        print("✓ 通过检查")
    else:
        print("✗ 需要人工审核")
    print("=" * 60)

    # 输出结果
    output_data = {
        'tweets': results,
        'average_score': avg_score,
        'passed': avg_score <= args.threshold
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