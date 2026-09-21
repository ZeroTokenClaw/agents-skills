---
name: agent-subagent-orchestration
description: >-
  Use when launching Explore/Plan/general-purpose subagents via Task-style
  fan-out: parallel research, readonly explore, detailed prompts, summarize
  results to user. Trigger on 子代理、Explore、Plan、Task工具、并行agent、
  subagent。
---

# 子代理编排（Explore / Plan / Task）

模式来源结构：[langgraph-claude-code subagent + Task](https://github.com/DarkNoah/langgraph-claude-code/tree/7e1e4fba64ab708be4b8b316c3874850577b0abf)。

## 类型与用途

| subagent_type | 用途 | 约束 |
| --- | --- | --- |
| Explore | 快找文件、关键词、回答「代码在哪/怎么走」 | 只读；thoroughness: quick/medium/very thorough |
| Plan | 基于探索结果做实现设计 | 只读；输出计划与关键文件 |
| general-purpose | 复杂多步调研或执行（按产品授权） | prompt 写明是否允许写代码 |

## 何时用 / 不用 Task

**用：** 范围不清、需多处搜索、要并行多视角、显著代码块后的专项审查。  

**不用：** 已知精确路径；单文件内搜；`class Foo` 一类可用 Glob 一次命中。

## 调用契约

每次调用提供：

1. `description`：3–5 词标题  
2. `prompt`：自包含任务（背景、范围、禁止事项、**返回字段清单**）  
3. `subagent_type`  

子代理 **无状态、单次回报**；主代理必须把结果摘要给用户（子结果默认对用户不可见）。

## 并行

用户要求并行或明显独立时：同一轮消息发出多个 Task。  
计划模式 Phase1：最多 3 个 Explore，能少则少。

## Explore 行为要点

- Glob 扩匹配 → Grep 内容 → Read 精读  
- 最终报告用**绝对路径** + 必要片段  
- 不改系统状态  

## Plan 行为要点

- 吃透需求与指定视角  
- 只读摸清现有模式与类似功能  
- 步骤化方案 + Critical Files  
- 禁止任何写操作  

## Prompt 模板（主代理 → 子代理）

```text
目标: ...
上下文: [关键绝对路径与已读结论]
约束: 只读 / 或允许编辑
thoroughness: quick|medium|very thorough
请返回:
1) 结论摘要
2) 绝对路径列表与原因
3) 风险/未知项
4) 建议的下一步（供主代理，勿直接改用户仓库除非授权）
```

## 禁止

- 把含糊一句「看看认证」丢给子代理  
- 子代理结果不摘要直接消失  
- 已知文件仍开 Explore 浪费延迟  
