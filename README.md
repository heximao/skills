# Skills 目录

本目录用于存放和管理 Claude 代理的 Skills（技能扩展）。

## 目录说明

- **全局用户 Skills**：通过 npm 全局安装的 Skills 存放在此目录
- **符号链接**：可以通过符号链接将 Skills 指向 Claude Code、OpenCode 等代理目录

## 文件结构

每个 Skill 通常包含以下文件：

```
skill-name/
├── SKILL.md          # Skill 的详细描述和使用说明
├── prompt.md         # 提示词文件（可选）
├── examples/         # 使用示例（可选）
└── utils/            # 工具函数（可选）
```

## 创建新 Skill

1. 在本目录创建新文件夹：`skill-name/`
2. 创建 `SKILL.md` 文件，描述 Skill 的功能和使用方式
3. 添加必要的实现文件
4. 配置符号链接（如需要）

## 符号链接配置

将 Skill 链接到 Claude 代理目录：

```bash
# 创建符号链接：将源 Skill 链接到目标代理目录
# -s 表示创建软链接（symbolic link）
# 第一个参数是源路径（全局 Skills 目录），第二个是目标路径（代理 Skills 目录）
ln -s /Users/user-name/.agents/skills/skill-name \
      /Users/user-name/.claude/skills/skill-name

# 验证符号链接创建是否成功
# 列出目标目录中的所有文件（包括隐藏文件），并过滤出特定的 skill 名称
ls -la /Users/user-name/.claude/skills/ | grep skill-name

# 删除符号链接（如需要）
# 使用 rm 命令删除链接本身，不会删除源文件
rm /Users/user-name/.claude/skills/skill-name
```

**说明：**
- 替换 `skill-name` 为实际的 Skill 目录名称
- 源路径：全局 Skills 存放目录（本目录）
- 目标路径：Claude 代理的 Skills 目录

## 参考资源

- [开源 Skill 项目参考](https://github.com/topics/claude-skill)
- [skills.sh - Vercel 官方仓库](https://github.com/vercel/skills.sh)

## 已有 Skills

查看本目录的子文件夹列表可查看已安装的全部 Skills。