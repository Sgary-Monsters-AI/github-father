# github-father

> GitHub 项目推文生产流水线 - 自动化生成高质量 GitHub 项目推荐推文

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/yourusername/github-father)

## 功能特性

- 🔍 **自动爬取**：支持 GitHub Trending 自动爬取或手动输入项目链接
- 🔄 **智能去重**：自动检测历史记录，避免重复推荐
- ⭐ **质量评估**：100 分制评分系统（实用性、开源性、易用性、创新性、活跃度）
- ✍️ **批量生成**：并行 3 个 agents 生成推文，支持多种模板风格
- 🎨 **AI 味检查**：自动检测并修复 AI 生成痕迹
- 📦 **一键保存**：自动下载截图，保存到待发布目录

## 快速开始

### 安装

```bash
# 使用 npx（推荐）
npx skills add yourusername/github-father

# 或手动安装
git clone https://github.com/yourusername/github-father.git
cd github-father
# 将目录复制到 .claude/skills/ 下
```

### 使用

```bash
# 在 Claude Code 中调用
/github-father
```

## 工作流程

```
启动 → 模式选择 → 项目发现 → 去重验证 → 信息提取 → 质量评估 → 推文生成 → AI 味检查 → 保存发布
```

### 阶段说明

1. **模式选择**：自动爬取 GitHub Trending 或手动提供链接
2. **去重验证**：检查 `history.json`，过滤已推荐项目
3. **信息提取**：使用 WebFetch 提取项目详细信息
4. **质量评估**：5 维度评分（阈值 75 分）
5. **推文生成**：3 个 agents 并行生成（痛点驱动型、场景描述式、GitHub 直入式）
6. **AI 味检查**：检测并修复 AI 生成痕迹（阈值 5 分）
7. **保存发布**：保存推文 + 下载截图 + 更新历史

## 文件结构

```
github-father/
├── SKILL.md              # AI 执行剧本
├── README.md             # 本文件
├── config.json           # 配置文件
├── history.json          # 历史记录（自动生成）
└── scripts/              # Python 脚本
    ├── deduplicate.py    # 去重验证
    ├── evaluate.py       # 质量评估
    ├── distribute.py     # 项目分配
    ├── check_ai_taste.py # AI 味检查
    └── update_history.py # 更新历史记录
```

## 配置

### 质量评估维度

| 维度 | 权重 | 说明 |
|------|------|------|
| 实用性 | 30% | 描述、功能、目标受众 |
| 开源性 | 20% | 开源协议（MIT/Apache/BSD/GPL） |
| 易用性 | 20% | 部署方式、文档完善度 |
| 创新性 | 15% | 差异化、功能特性 |
| 活跃度 | 15% | Star 数量 |

### AI 味检查规则

- **禁用词汇**：填充短语、空洞形容词、程度副词、营销话术
- **禁用句式**：二元对比、虚假范围、升华结尾
- **格式检查**：感叹号数量、emoji 比例、数字编号

## 推文风格

基于 [wsl8297](https://x.com/wsl8297) 的 GitHub 项目推荐风格：

- **长度**：300-400 字符，3-5 段
- **语气**：克制专业（emoji <5%，感叹号 ≤1 个）
- **结构**：开场 → 项目引入 → **GitHub：** 链接 → 功能列表 → 结尾
- **列表**：用 • 符号，不用数字编号

### 模板类型

1. **痛点驱动型**（6.1%）：用户行为 + 痛点 → 解决方案
2. **场景描述式**（56.1%）：场景/需求描述 → 项目介绍
3. **GitHub 直入式**（28.5%）：直接引入 → 功能密集描述

## 输出示例

```markdown
# GitHub 项目推文 - 2026-05-15

## 项目 1: telegraf (评分: 83/100)

监控系统搭建时，最头疼的是数据采集：不同来源需要不同工具，配置复杂，依赖一堆。

Telegraf 是 InfluxData 开源的指标采集引擎，单个静态二进制文件，无外部依赖。

**GitHub：** https://github.com/influxdata/telegraf

主要功能：
• 300+ 插件覆盖系统监控、云服务、消息队列
• TOML 配置文件，人类可读
• Windows 专用输入（事件日志、性能计数器）
• 通用输入支持 Exec、HTTP、SNMP、SQL

适合需要统一采集层的运维团队和 SRE。

**元数据**：
- Star：17.2k
- 语言：Go
- AI 味评分：0/10
```

## 依赖

- **Claude Code**：AI 编程助手
- **wsl8297-perspective**：推文风格定义（可选，如果需要完整风格）
- **Python 3.x**：运行脚本

## 常见问题

### Q: 如何修改质量评估阈值？

编辑 `scripts/evaluate.py`，修改 `--threshold` 默认值（默认 75）。

### Q: 如何自定义推文风格？

修改 `SKILL.md` 中的风格定义部分，或创建自己的模板文件。

### Q: 历史记录文件在哪里？

`history.json` 会自动生成在 skill 目录下，记录所有已推荐的项目 URL。

### Q: 如何清空历史记录？

删除或清空 `history.json` 文件即可。

## 开发

### 运行测试

```bash
# 测试去重脚本
python3 scripts/deduplicate.py --urls "url1,url2" --history-file history.json

# 测试质量评估
python3 scripts/evaluate.py --projects-json projects.json --threshold 75

# 测试 AI 味检查
python3 scripts/check_ai_taste.py --tweets-json tweets.json --threshold 5
```

### 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 版本历史

- **v2.0.0** (2026-05-14)
  - 重构为完整流水线
  - 新增并行 agents 生成
  - 新增 AI 味检查
  - 新增质量评估系统

- **v1.0.0** (2026-05-11)
  - 初始版本

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 致谢

- 推文风格灵感来自 [@wsl8297](https://x.com/wsl8297)
- 基于 [Claude Code](https://claude.ai/code) 构建

## 联系方式

- GitHub: [@yourusername](https://github.com/yourusername)
- X/Twitter: [@yourhandle](https://x.com/yourhandle)

---

**Star ⭐ 本项目，如果它对你有帮助！**
