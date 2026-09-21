---
name: agent-plan-mode
description: >-
  Use when entering read-only plan/design phase before coding: explore codebase,
  draft plan, get user approval, then exit to implement. Trigger on 计划模式、
  EnterPlanMode、ExitPlanMode、先规划再写代码、plan mode。
---

# Agent 计划模式（只读闸门）

工程模式对齐公开结构说明：[langgraph-claude-code 计划模式](https://github.com/DarkNoah/langgraph-claude-code/tree/7e1e4fba64ab708be4b8b316c3874850577b0abf)。

## 何时进入

满足任一则优先规划，而非直接改代码：

- 新功能 / 多文件（>2–3）改动  
- 多种合法方案（缓存、鉴权、实时通道等）  
- 需求不清，需先摸清架构  
- 会改变既有行为或公共 API  

**可跳过：** 单行笔误、明确单函数、纯问答调研。

## 闸门规则（硬约束）

计划模式激活期间：

1. **禁止** Write / Edit / MultiEdit / 改配置 / commit / install / 重定向写文件  
2. **允许** Read / Glob / Grep / 只读 Bash（ls、git status/log/diff、cat）  
3. 全面回答 + 产出可执行计划；用「退出计划 / 请用户确认」结束，勿直接动手  

中文提醒要点（自拟，勿依赖外部全文）：

> 计划模式已开启。在用户确认前不得修改系统状态；完成研究后提交计划供确认。

## 五阶段工作流

```text
Phase1 理解 → 仅 Explore 子代理（≤3 并行）+ AskUserQuestion
Phase2 设计 → Plan 子代理（通常 1 个）出实现方案
Phase3 复核 → 主代理读关键文件，对齐用户意图
Phase4 落盘 → 仅允许写「计划文件」本身（若产品支持）
Phase5 退出 → ExitPlanMode / 用户批准 → 再 TodoWrite + 编码
```

批准后典型系统回执语义：用户已批准计划，可开始编码；先更新 todo。

## 计划文档应含

- 目标与非目标  
- 方案与取舍（只保留推荐方案正文）  
- 步骤顺序与依赖  
- **Critical Files**（3–5 个绝对路径 + 一句话原因）  
- 风险与回滚点  

## 退出后

恢复写工具；按计划小步提交；发现计划偏离则再次进入计划模式，勿硬拧。

## 禁止

- 计划阶段「先改一点试试」  
- 相对路径列关键文件（用绝对路径）  
- 把未经用户确认的方案当已批准  
