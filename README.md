# Skills 仓库

集中存放所有 Claude Code / OpenCode skills 的汇总仓库。

## 安装原则

**不要将整个仓库的所有 skill 一股脑安装到全局目录或项目目录。** AI 会加载已安装 skill 的全部内容，安装过多无关 skill 会导致：

- Token 消耗大幅增加
- 上下文窗口被无关内容挤占
- AI 理解精度下降，产生幻觉

**正确做法：按需安装，用符号链接。**

### 安装优先级

1. **项目目录优先** — 只在某个项目用到的 skill，安装到该项目的 `.claude/skills/` 下
2. **全局目录其次** — 确定会在多个项目使用的 skill，才安装到全局 `~/.claude/skills/`

### 安装命令

```bash
# 安装到项目目录（推荐）
ln -s ~/.agents/skills/skill-name ~/your-project/.claude/skills/skill-name

# 安装到全局目录（仅限跨项目通用 skill）
ln -s ~/.agents/skills/skill-name ~/.claude/skills/skill-name
```

### 卸载命令

```bash
# 删除符号链接（不会删除源文件）
rm ~/your-project/.claude/skills/skill-name
```

### 验证安装

```bash
ls -la ~/your-project/.claude/skills/ | grep skill-name
```

## 已有 Skills

| Skill | 用途 |
|-------|------|
| agent-development | 创建和调试 Claude agent |
| cua-driver | macOS 原生应用自动化操作 |
| frontend-design | 前端界面设计与开发 |
| hook-development | Claude Code hook 开发 |
| kami | 专业文档排版（简历、白皮书、PPT、落地页） |
| skill-creator | 创建、测试、优化 skill |
| software-development | 通用软件开发 skill 集合 |
| tender-offer-arbitrage | 要约套利分析 |
| transaction-verification | 交易记录核对与验证 |
| 股票智能分析师 | A股/港股/美股分析 |

## 文件结构

每个 Skill 通常包含以下文件：

```
skill-name/
├── SKILL.md          # 必需：skill 定义（含 YAML frontmatter）
├── scripts/          # 可选：可执行脚本
├── examples/         # 可选：使用示例
└── references/       # 可选：参考文档
```

## 创建新 Skill

1. 在本目录创建新文件夹：`mkdir new-skill-name`
2. 创建 `SKILL.md`，必须包含 `name` 和 `description` frontmatter
3. 按需添加 scripts / examples / references
4. 提交并推送到 GitHub

## 参考资源

- [开源 Skill 项目参考](https://github.com/topics/claude-skill)
- [skills.sh - Vercel 官方仓库](https://github.com/vercel/skills.sh)
