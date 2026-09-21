---
name: find-skills
description: 当用户问「怎么做 X」「找一个 X 相关的 skill」「有没有能…的 skill」或想扩展能力时，帮助发现并安装 agent skills。用户寻找可能以可安装 skill 形式存在的功能时应使用本 skill。
---

# Find Skills（发现技能）

本 skill 帮助你在开放 agent skills 生态中发现并安装技能。

## 何时使用本 Skill

当用户出现以下情况时使用本 skill：

- 问「怎么做 X」，且 X 可能是已有 skill 覆盖的常见任务
- 说「找一个 X 的 skill」或「有没有 X 的 skill」
- 问「你能做 X 吗」，且 X 是某种专门能力
- 表示想扩展 agent 的能力
- 想搜索工具、模板或工作流
- 提到希望在某领域（设计、测试、部署等）获得帮助

## 什么是 Skills CLI？

Skills CLI（`npx skills`）是开放 agent skills 生态的包管理器。Skills 是模块化包，用专门知识、工作流和工具扩展 agent 能力。

**常用命令：**

- `npx skills find [query]` - 按关键词交互式搜索技能
- `npx skills add <package>` - 从 GitHub 等来源安装技能
- `npx skills check` - 检查技能更新
- `npx skills update` - 更新所有已安装技能

**浏览技能：** https://skills.sh/

## 如何帮用户找到技能

### 步骤 1：理解需求

当用户寻求帮助时，先明确：

1. 领域（如 React、测试、设计、部署）
2. 具体任务（如写测试、做动画、审 PR）
3. 该任务是否常见到很可能已有对应 skill

### 步骤 2：搜索技能

用相关查询执行 find 命令：

```bash
npx skills find [query]
```

示例：

- 用户问「怎么让我的 React 应用更快？」→ `npx skills find react performance`
- 用户问「能帮我审 PR 吗？」→ `npx skills find pr review`
- 用户说「我需要生成 changelog」→ `npx skills find changelog`

命令会返回类似结果：

```
Install with npx skills add <owner/repo@skill>

vercel-labs/agent-skills@vercel-react-best-practices
└ https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices
```

### 步骤 3：向用户展示选项

找到相关技能后，向用户说明：

1. 技能名称及作用
2. 可执行的安装命令
3. 在 skills.sh 上了解更多信息的链接

示例回复：

```
我找到一个可能对你有用的 skill！"vercel-react-best-practices" 提供
来自 Vercel Engineering 的 React 与 Next.js 性能优化指南。

安装命令：
npx skills add vercel-labs/agent-skills@vercel-react-best-practices

了解更多：https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices
```

### 步骤 4：提供安装

若用户同意，可代为安装：

```bash
npx skills add <owner/repo@skill> -g -y
```

`-g` 表示用户级全局安装，`-y` 跳过确认提示。

## 常见技能分类

搜索时可参考这些分类：

| 分类         | 示例查询                                   |
| ------------ | ------------------------------------------ |
| Web 开发     | react, nextjs, typescript, css, tailwind   |
| 测试         | testing, jest, playwright, e2e             |
| DevOps       | deploy, docker, kubernetes, ci-cd          |
| 文档         | docs, readme, changelog, api-docs          |
| 代码质量     | review, lint, refactor, best-practices     |
| 设计         | ui, ux, design-system, accessibility       |
| 效率         | workflow, automation, git                  |

## 搜索技巧

1. **用具体关键词**：用「react testing」比单用「testing」更好
2. **换说法**：搜「deploy」没结果可试「deployment」或「ci-cd」
3. **关注常见来源**：很多技能来自 `vercel-labs/agent-skills` 或 `ComposioHQ/awesome-claude-skills`

## 未找到相关技能时

若没有匹配技能：

1. 说明未找到现有技能
2. 表示仍可用通用能力直接协助完成该任务
3. 建议用户用 `npx skills init` 创建自己的 skill

示例：

```
我搜索了与「xyz」相关的技能，没有找到匹配结果。
我仍然可以直接帮你完成这个任务！需要我继续吗？

如果这是你常做的事，可以自己创建一个 skill：
npx skills init my-xyz-skill
```
