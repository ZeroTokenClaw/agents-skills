---
name: {{PROJECT_NAME}}
description: Use when working on {{PROJECT_NAME}} to follow project conventions and constraints
---
# } 项目约束

> **AI 必读**：此文档是本项目的最高法律。违反此文档约束的代码将被视为错误代码。分析项目现有代码优先于此文档，但此文档优先于你的默认知识。

## 1. 身份与工具链

| 维度               | 值                    | 备注                                 |
| ------------------ | --------------------- | ------------------------------------ |
| **语言**     | {{LANGUAGE}}          | 遵循 {{STRICTNESS}} 模式             |
| **运行时**   | {{RUNTIME_VERSION}}   | 严格遵守版本特性限制                 |
| **框架**     | {{FRAMEWORK_VERSION}} | 使用此版本的最佳实践                 |
| **包管理器** | {{PACKAGE_MANAGER}}   | 仅使用此工具安装依赖                 |
| **构建工具** | {{BUILD_TOOL}}        |                                      |
| **样式方案** | {{STYLING_SOLUTION}}  | (e.g. Tailwind, CSS Modules, Styled) |

## 2. 核心命令

```bash
{{INSTALL_CMD}}     # 安装依赖
{{DEV_CMD}}         # 启动开发 (端口: {{PORT}})
{{BUILD_CMD}}       # 生产构建
{{TEST_CMD}}        # 运行测试
{{LINT_CMD}}        # 代码检查 (必须通过)
{{TYPE_CHECK_CMD}}  # 类型检查 (必须通过)
```

## 3. 架构与目录

**根目录结构：**

```
{{ACTUAL_DIRECTORY_STRUCTURE}}
```

**关键路径约定：**

- **源码根目录**: `{{SRC_ROOT}}`
- **公共组件**: `{{COMPONENTS_PATH}}`
- **业务页面/路由**: `{{PAGES_PATH}}`
- **工具函数**: `{{UTILS_PATH}}`
- **类型定义**: `{{TYPES_PATH}}`
- **静态资源**: `{{ASSETS_PATH}}`

**导入规则：**

- 别名: 使用 `{{ALIAS_PREFIX}}` (e.g. `@/components`) 而非 `../../`
- 边界: `{{BOUNDARY_RULE}}` (e.g. components 不能引用 pages)

## 4. 命名规范 (严格执行)

| 实体           | 格式                 | 示例                   | 禁止                  |
| -------------- | -------------------- | ---------------------- | --------------------- |
| **变量** | {{VAR_CONVENTION}}   | `{{VAR_EXAMPLES}}`   | 单字母变量 (除 i,j,k) |
| **函数** | {{FUNC_CONVENTION}}  | `{{FUNC_EXAMPLES}}`  | 动词缺失              |
| **组件** | {{COMP_CONVENTION}}  | `{{COMP_EXAMPLES}}`  | 非名词短语            |
| **文件** | {{FILE_CONVENTION}}  | `{{FILE_EXAMPLES}}`  | 大小写混用            |
| **类型** | {{TYPE_CONVENTION}}  | `{{TYPE_EXAMPLES}}`  | I前缀 (如 IUser)      |
| **常量** | {{CONST_CONVENTION}} | `{{CONST_EXAMPLES}}` | 魔术数字              |

## 5. 编码规范 (Coding Standards)

### 5.1 类型系统 (Type System)

- **显式类型**: {{EXPLICIT_TYPE_RULE}} (e.g. 导出函数必须标注返回值)
- **Any 策略**: **禁止使用 `any`**。使用 `unknown` 并配合类型守卫。
- **类型定义**: 优先使用 `{{INTERFACE_OR_TYPE}}`。
- **非空断言**: 禁止使用 `!`，必须处理 null/undefined。

### 5.2 状态管理 (State Management)

**方案**: 使用 **{{STATE_LIB}}**

```{{LANG}}
{{STATE_MANAGEMENT_EXAMPLE}}
```

### 5.3 异步模式 (Async Pattern)

**方案**: 统一使用 **{{ASYNC_STYLE}}**

```{{LANG}}
{{ASYNC_PATTERN_EXAMPLE}}
```

### 5.4 错误处理 (Error Handling)

**方案**: {{ERROR_STRATEGY}}

```{{LANG}}
{{ERROR_HANDLING_EXAMPLE}}
```

### 5.5 数据获取 (Data Fetching)

**方案**: 使用 **{{DATA_FETCHING_LIB}}**

```{{LANG}}
{{DATA_FETCHING_EXAMPLE}}
```

### 5.6 注释规范 (Comments)

- **JSDoc**: 公共函数必须包含 JSDoc (Params, Returns)。
- **行内注释**: 仅解释“为什么” (Why)，不解释“是什么” (What)。
- **TODO**: 使用 `// TODO(user): description` 格式。

## 6. 标准模板 (Templates)

### 6.1 通用组件模板

```{{LANG}}
{{COMPONENT_TEMPLATE}}
```

### 6.2 测试文件模板

**位置**: `{{TEST_LOCATION}}`

```{{LANG}}
{{TEST_TEMPLATE}}
```

## 7. 质量检查清单 (Quality Checklist)

### 7.1 禁止模式 (Prohibited Patterns)

| ❌ 绝对禁止      | ✅ 替代方案          | 原因         |
| ---------------- | -------------------- | ------------ |
| {{PROHIBITED_1}} | {{ALTERNATIVE_1}}    | {{REASON_1}} |
| {{PROHIBITED_2}} | {{ALTERNATIVE_2}}    | {{REASON_2}} |
| {{PROHIBITED_3}} | {{ALTERNATIVE_3}}    | {{REASON_3}} |
| console.log      | Logger util          | 生产环境污染 |
| 内联样式         | {{STYLING_SOLUTION}} | 样式难以维护 |
| 魔法数字         | 常量定义             | 含义不明     |

### 7.2 UI/样式规范

- **响应式**: 使用 {{RESPONSIVE_STRATEGY}} (e.g. mobile-first, breakpoints)
- **颜色**: 必须使用 `{{THEME_VARS}}` 中定义的变量。
- **间距**: 必须使用 `{{SPACING_SYSTEM}}` (e.g. 4px grid)。

### 7.3 性能铁律

- 列表渲染必须包含唯一且稳定的 `key`。
- 图片必须包含 `alt` 属性和尺寸/预加载设置。
- 避免在渲染循环中定义函数 (useCallback)。
- 重计算逻辑必须使用 memoization。

## 8. 工作流规范

**Git 提交信息**:
格式: `<type>(<scope>): <subject>`
示例: `feat(auth): add login validation`
Types: feat, fix, docs, style, refactor, test, chore

**环境变量**:

- 必需变量: `{{REQUIRED_ENV_VARS}}`
- **警告**: 禁止将密钥硬编码在代码中。

---

**生成信息**:

- Date: {{GENERATED_DATE}}
- Version: v1.1
