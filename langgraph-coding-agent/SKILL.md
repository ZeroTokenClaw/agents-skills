---
name: langgraph-coding-agent
description: >-
  Use when building LangGraph / multi-agent coding systems inspired by Claude
  Code-style tool loops: plan mode, Explore/Plan subagents, Task fan-out, agent
  JSON specs, CLAUDE.md context. Trigger on LangGraph、编码Agent、计划模式、
  子代理、Explore、Plan、EnterPlanMode、创建agent。
---

# LangGraph 编码 Agent 架构

模式提炼自开源结构研究仓：[DarkNoah/langgraph-claude-code@7e1e4fb](https://github.com/DarkNoah/langgraph-claude-code/tree/7e1e4fba64ab708be4b8b316c3874850577b0abf)（工具目录、计划模式文档、subagent、创建 agent 的 JSON 规格）。

**不**把第三方逆向的超长系统提示原文当依赖；落地用本 skill 的工程约束 + 官方/自有提示。

专项：`agent-plan-mode`、`agent-subagent-orchestration`、`agent-spec-creator`。

## 总览拓扑

```text
User
  ↓
Main Agent (工具环)
  ├─ EnterPlanMode / ExitPlanMode     → 只读规划闸门
  ├─ Task(subagent_type=Explore|Plan|general-purpose) → 并行子代理
  ├─ Read/Glob/Grep/Bash(ro) / Edit/Write
  ├─ TodoWrite / AskUserQuestion
  └─ Skill / WebSearch / WebFetch
  ↓
CLAUDE.md / 项目约定 作为持续上下文
```

## 仓库结构对照（可作 LangGraph 节点拆分）

| 上游路径 | 职责 | LangGraph 建议 |
| --- | --- | --- |
| `tools/*.md` | 工具契约（名、描述、schema） | ToolNode + 绑定 LLM |
| `05.计划模式.md` + `EnterPlanMode`/`ExitPlanMode` | 只读规划闸门 | 条件边：`mode==plan` 禁用写工具 |
| `subagent/Explore.md` | 快搜代码库 | 轻量模型子图 |
| `subagent/Plan.md` | 架构/实现计划 | 中等模型子图 |
| `01.创建agents的prompt.md` | 生成自定义 agent JSON | 元 Agent 节点 |
| `03.创建CLAUDE.md` | 项目记忆文件 | 启动时注入 system |
| `06.后台任务.md` | 长任务 | 异步 worker / interrupt |
| `krio/` | Power/Spec/Vibe 变体 | 可选 persona 配置 |

## 主循环原则

1. **模式显式**：`normal | plan`；plan 下禁止写文件/改配置/安装/提交  
2. **探索并行**：不确定范围时最多 3 个 Explore Task 同消息发出  
3. **计划审批**：实现前 `ExitPlanMode`（或等价「用户确认」中断）  
4. **子代理无状态**：prompt 写全背景 + 要求返回的字段；结果由主代理摘要给用户  
5. **小任务不派 Task**：已知路径用 Read/Glob，避免子代理开销  

## 与 Cursor / 本机 skill 对齐

| 需求 | 本机 skill |
| --- | --- |
| 计划闸门细节 | `agent-plan-mode` |
| Explore/Plan/Task | `agent-subagent-orchestration` |
| 写自定义 agent | `agent-spec-creator` |
| 工程 TDD/增量实现 | `spec-driven-development`、`incremental-implementation` |
| 并行探索 | `dispatching-parallel-agents`、`parallel-exploring` |

## Agent 执行清单（用本仓思想搭 LangGraph）

1. 列出工具 schema（对齐 Read/Edit/Bash/Task…）  
2. 实现 `plan` 状态位 + 写工具守卫  
3. 注册 Explore / Plan / general-purpose 子图  
4. 注入项目 `CLAUDE.md`（或等价）  
5. 可选：元节点按 JSON 规格动态注册子代理  

## 禁止

- 把逆向得到的厂商完整系统提示大段粘进生产  
- 用 README 中的 API 反向代理手法作为 skill 内容（与 Agent 架构无关）  
- plan 模式下偷偷 Write/Edit  
