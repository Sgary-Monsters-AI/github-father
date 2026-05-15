---
name: github-father
description: GitHub 项目推文生产流水线 - 自动爬取 Trending、质量评估、批量生成推文（wsl8297 风格）
version: 2.0.0
author: Gary
triggers:
  - "GitHub Trending"
  - "生成 GitHub 推文"
  - "批量生成 GitHub 推文"
  - "GitHub 项目推荐推文"
  - "爬取 GitHub Trending"
allowed_tools:
  - WebSearch
  - WebFetch
  - Agent
  - Read
  - Write
  - Bash
dependencies:
  - wsl8297-perspective
---

# github-father

> GitHub 项目推文生产流水线

---

## 执行流程

```
启动 → 模式选择 → 项目发现 → 去重验证 → 信息提取 → 质量评估 → 推文生成 → AI 味检查 → 保存发布
```

---

## 阶段 1：启动与模式选择

**输入**：用户调用 `/github-father`

**执行**：
```
询问用户：
1. 自动爬取 GitHub Trending（推荐）
2. 手动提供 GitHub 项目链接

如果选择 1：
  - 询问时间范围：today / this week / this month
  - 询问语言筛选：all / python / javascript / go / rust 等
  - 询问爬取数量：1-25（默认 10）

如果选择 2：
  - 用户粘贴 GitHub 链接（支持多个，换行分隔）
```

**输出**：项目 URL 列表

---

## 阶段 2：项目发现与去重验证

**输入**：项目 URL 列表

**工具**：Bash + Python 脚本

**执行**：
```bash
# 调用去重脚本
python3 .claude/skills/github-father/scripts/deduplicate.py \
  --urls "url1,url2,url3" \
  --history-file ".claude/skills/github-father/history.json"
```

**脚本输出**：
```json
{
  "total": 20,
  "duplicates": 3,
  "new_projects": 17,
  "new_urls": ["url1", "url2", ...]
}
```

**检查点**：
- [ ] 已执行去重脚本
- [ ] 已输出去重报告
- [ ] 只处理 new_urls

---

## 阶段 3：信息提取

**输入**：new_urls 列表

**工具**：WebFetch

**执行**：
对每个 URL 使用 WebFetch 提取：
```
WebFetch(
  url=project_url,
  prompt="提取以下信息：
    1. 仓库名称、Star 数、主要语言、开源协议
    2. 项目一句话描述
    3. 核心功能列表（3-6 条）
    4. 部署方式
    5. 目标受众
    6. README 中的第一张有意义的截图 URL（排除 badge）"
)
```

**输出**：项目信息字典列表

---

## 阶段 4：质量评估

**输入**：项目信息字典列表

**工具**：Bash + Python 脚本

**执行**：
```bash
# 调用评估脚本
python3 .claude/skills/github-father/scripts/evaluate.py \
  --projects-json "projects.json" \
  --threshold 75
```

**评分维度**（总分 100）：
- 实用性 30%
- 开源性 20%
- 易用性 20%
- 创新性 15%
- 活跃度 15%

**脚本输出**：
```json
{
  "qualified_projects": [...],
  "rejected_projects": [...],
  "average_score": 82.3
}
```

**检查点**：
- [ ] 已执行评估脚本
- [ ] 已过滤低质量项目（<75 分）

---

## 阶段 5：推文生成

**输入**：qualified_projects 列表

**模式选择**：
- 1-3 个项目 → 单个推文模式
- 4+ 个项目 → 批量生成模式

---

### 模式 A：单个推文模式

**执行**：
```python
# 1. 加载核心文件
dna = Read(".claude/skills/wsl8297-perspective/SKILL_DNA.md")
rules = Read(".claude/skills/wsl8297-perspective/core/rules.md")

# 2. AI 根据项目特点选择模板
# 可选：pain_driven / scene_based / github_direct / question_based / recommend

template_name = "scene_based"  # AI 自由选择
template = Read(f".claude/skills/wsl8297-perspective/templates/{template_name}.md")

# 3. 生成推文（AI 自由发挥）
```

**必须遵守**：
- ✓ 长度 300-400 字符，3-5 段
- ✓ GitHub 链接在第二段，`**GitHub：**` 加粗
- ✓ 功能列表用 • 符号
- ✓ Emoji <5%，感叹号 ≤1 个
- ✗ 禁止"发现一个 XX 项目"开头
- ✗ 禁止数字编号列表（1. 2. 3.）

---

### 模式 B：批量生成模式

**执行**：
```bash
# 1. 调用分配脚本
python3 .claude/skills/github-father/scripts/distribute.py \
  --projects-json "qualified_projects.json" \
  --output "distribution.json"
```

**分配脚本输出**：
```json
{
  "agent_a": {
    "template": "pain_driven",
    "projects": [...]
  },
  "agent_b": {
    "template": "scene_based",
    "projects": [...]
  },
  "agent_c": {
    "template": "github_direct",
    "projects": [...]
  }
}
```

**2. 并行启动 3 个 agents**：
```python
distribution = read_json("distribution.json")

# Agent A
Agent(
    description=f"Agent A - 痛点驱动型 ({len(distribution['agent_a']['projects'])} 个)",
    prompt=create_agent_prompt(
        agent_name="Agent A",
        template="pain_driven",
        projects=distribution['agent_a']['projects']
    )
)

# Agent B
Agent(
    description=f"Agent B - 场景描述式 ({len(distribution['agent_b']['projects'])} 个)",
    prompt=create_agent_prompt(
        agent_name="Agent B",
        template="scene_based",
        projects=distribution['agent_b']['projects']
    )
)

# Agent C
Agent(
    description=f"Agent C - GitHub 直入式 ({len(distribution['agent_c']['projects'])} 个)",
    prompt=create_agent_prompt(
        agent_name="Agent C",
        template="github_direct",
        projects=distribution['agent_c']['projects']
    )
)
```

**Agent Prompt 函数**：
```python
def create_agent_prompt(agent_name, template, projects):
    dna = Read(".claude/skills/wsl8297-perspective/SKILL_DNA.md")
    rules = Read(".claude/skills/wsl8297-perspective/core/rules.md")
    template_content = Read(f".claude/skills/wsl8297-perspective/templates/{template}.md")
    
    projects_info = "\n\n".join([
        f"### 项目 {i+1}: {p['name']}\n"
        f"- GitHub: {p['url']}\n"
        f"- Star: {p['stars']}\n"
        f"- 简介: {p['description']}\n"
        f"- 核心功能: {', '.join(p['features'])}"
        for i, p in enumerate(projects)
    ])
    
    return f"""
你是 {agent_name}，负责为 {len(projects)} 个 GitHub 项目生成推文。

# 核心风格定义
{dna}

# 表达规则
{rules}

# 模板结构
{template_content}

# 项目列表
{projects_info}

# 必须遵守
1. 长度：300-400 字符，3-5 段
2. 格式：GitHub 链接在第二段，`**GitHub：**` 加粗
3. 功能列表：用 • 符号
4. 语气：Emoji <5%，感叹号 ≤1 个

# 绝对禁止
- ✗ "发现一个 XX 项目"开头
- ✗ 数字编号列表（1. 2. 3.）
- ✗ 固定套路（"XX 来了"）

# 随机性要求
- 每个推文的开场方式必须不同
- 不要连续使用同一种表达方式

开始生成。
"""
```

---

## 阶段 6：AI 味检查

**输入**：生成的推文

**工具**：Bash + Python 脚本

**执行**：
```bash
# 调用 AI 味检查脚本
python3 .claude/skills/github-father/scripts/check_ai_taste.py \
  --tweets-json "generated_tweets.json" \
  --threshold 5
```

**脚本功能**：
- 检查禁用词汇（填充短语、空洞形容词、程度副词）
- 检查禁用句式（二元对比、排比堆砌）
- 检查格式（感叹号、emoji、数字编号）
- 自动修复问题
- 评分 0-10

**脚本输出**：
```json
{
  "tweets": [
    {
      "original": "...",
      "fixed": "...",
      "score": 2,
      "issues": ["删除 1 个感叹号", "替换空洞形容词"]
    }
  ],
  "average_score": 1.8
}
```

**检查点**：
- [ ] AI 味评分 ≤5
- [ ] 已自动修复问题

---

## 阶段 7：保存与发布

**输入**：修复后的推文

**工具**：Write + Bash

**执行**：
```bash
# 1. 创建输出目录
DATE=$(date +%Y-%m-%d)
OUTPUT_DIR="01-内容生产/02-待发布/GitHub推文_${DATE}"
mkdir -p "${OUTPUT_DIR}/images"

# 2. 保存推文
# 使用 Write 工具保存到 ${OUTPUT_DIR}/GitHub推文_${DATE}.md

# 3. 下载截图（如果有）
for project in projects:
    if project['screenshot_url']:
        curl -L -o "${OUTPUT_DIR}/images/${project['owner']}-${project['repo']}.png" \
            "${project['screenshot_url']}"

# 4. 更新历史记录
python3 .claude/skills/github-father/scripts/update_history.py \
  --urls "url1,url2,url3" \
  --history-file ".claude/skills/github-father/history.json"
```

**输出格式**：
```markdown
# GitHub 项目推文 - 2026-05-14

> 生成时间：2026-05-14 14:30
> 项目数量：15
> 平均评分：82.3/100
> 平均 AI 味：1.8/10

---

## 项目 1: owner/repo (评分: 92/100)

![](./images/owner-repo.png)

[推文内容]

**元数据**：
- GitHub：https://github.com/owner/repo
- Star：14.3k
- 语言：Python
- AI 味评分：1/10

---

[以此类推]
```

**检查点**：
- [ ] 推文已保存
- [ ] 截图已下载
- [ ] 历史记录已更新

**必须告知用户**：
```
✓ 已完成！

文件已保存到：{OUTPUT_DIR}/GitHub推文_{DATE}.md
图片已保存到：{OUTPUT_DIR}/images/（X 张）

统计信息：
- 总爬取项目：X
- 通过评估：Y（Z%）
- 平均评分：XX/100
- 平均 AI 味：X.X/10
```

---

## 配置

**状态文件位置**：`.claude/skills/github-father/history.json`

**输出目录**：`01-内容生产/02-待发布/`

**质量阈值**：75 分

**AI 味阈值**：5 分

---

## 脚本清单

| 脚本 | 功能 | 输入 | 输出 |
|------|------|------|------|
| `scripts/deduplicate.py` | 去重验证 | URLs + history.json | new_urls |
| `scripts/evaluate.py` | 质量评估 | projects.json | qualified_projects |
| `scripts/distribute.py` | 项目分配 | qualified_projects | distribution.json |
| `scripts/check_ai_taste.py` | AI 味检查 | tweets.json | fixed_tweets |
| `scripts/update_history.py` | 更新历史 | URLs + history.json | - |

---

**版本**：v2.0.0  
**更新**：2026-05-14