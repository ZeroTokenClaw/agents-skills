# 项目Skill目录标准

## 位置规则

```
❌ 错误: ~/.config/opencode/my-project-skill/
✅ 正确: project-root/.{agent}/skills/
```

## Agent目录映射

| Agent工具 | 目录名 |
|-----------|--------|
| Claude Code | `.claude` |
| OpenCode | `.opencode` |
| Codex | `.codex` |
| Cursor | `.cursor` |
| 通用 | `.ai` |

## 标准结构

```
project-root/
  .{agent}/              # 根据当前agent确定
    skills/
      PROJECT.md         # 必需：主约束文档
      STYLE-GUIDE.md     # 可选：详细风格
      ARCHITECTURE.md    # 可选：架构决策
```

## 文件说明

| 文件 | 必需 | 内容 | 行数 |
|------|-----|------|-----|
| PROJECT.md | ✅ | 主约束 | 100-200 |
| STYLE-GUIDE.md | ⚪ | 风格细节 | 50-100 |
| ARCHITECTURE.md | ⚪ | 架构决策 | 50-100 |

## 完整性检查

- [ ] PROJECT.md存在
- [ ] 版本号从配置复制
- [ ] 命令可执行
- [ ] 目录结构真实
- [ ] 示例来自真实代码
- [ ] 已提交Git
