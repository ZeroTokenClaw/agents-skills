---
name: agent-spec-creator
description: >-
  Use when creating custom coding subagent specs as JSON: identifier, whenToUse
  with examples, systemPrompt. Trigger on 创建agent、自定义子代理、agent
  JSON、whenToUse、agent architect。
---

# 自定义 Agent 规格生成器

流程对齐：[langgraph-claude-code 创建 agents 的 prompt](https://github.com/DarkNoah/langgraph-claude-code/blob/7e1e4fba64ab708be4b8b316c3874850577b0abf/01.%E5%88%9B%E5%BB%BAagents%E7%9A%84prompt.md)。

## 输出 JSON（仅此三字段）

```json
{
  "identifier": "code-reviewer",
  "whenToUse": "Use this agent when... <example>...</example>",
  "systemPrompt": "You are... You will..."
}
```

## 生成步骤

1. **抽意图**：职责、成功标准、隐式需求；尊重项目 CLAUDE.md  
2. **人设**：领域专家身份，指导决策风格  
3. **写 systemPrompt**（第二人称）：边界、方法、边界情况、输出格式、质量自检  
4. **identifier**：小写+连字符，2–4 词，忌 helper/assistant  
5. **whenToUse**：以 `Use this agent when...` 开头，并含 `<example>`：用户语境 → 助手应 **走 Task/Agent 工具** 而非直接干完  

## whenToUse 示例形态

```xml
<example>
Context: 用户刚写完一块逻辑，需要审查。
user: "请写判断质数的函数"
assistant: [写完代码后]
commentary: 显著代码已完成，应启动 code-reviewer
assistant: 使用 Task 启动 code-reviewer
</example>
```

若用户希望 **主动触发**，示例中体现无显式点名也会调用。

## 保留字

勿占用已存在 id（如 `general-purpose`、`Explore`、`Plan`、以及注册表已有名）。

## 质量原则

- 具体，忌空话  
- 有决策框架与失败回退  
- 与仓库编码规范一致  
- 只返回 JSON，无前后废话  

## 禁止

- 输出非 JSON 包裹物  
- 审查类默认「扫全仓库」（除非用户明确）  
- identifier 含空格/下划线/大写  
