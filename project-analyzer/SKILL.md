---
name: project-analyzer
description: Use when entering an unfamiliar project to analyze it and generate a project-specific skill in the project's .{agent}/skills/ directory
---
# Project Analyzer

## Iron Law

```
分析项目 → 生成项目skill → 然后才能开发
```

**核心职责：** 分析当前目录下的项目，生成 `.{agent}/skills/PROJECT.md`

## 触发条件

**必须执行：**

- 首次进入新项目
- 项目无 `.{agent}/skills/PROJECT.md`
- 用户请求分析项目

**跳过：**

- 已存在完整的项目skill
- 仅查询信息（不修改代码）

---

## Agent目录映射

| Agent工具   | 项目Skill目录         |
| ----------- | --------------------- |
| Claude Code | `.claude/skills/`   |
| OpenCode    | `.opencode/skills/` |
| Codex       | `.codex/skills/`    |
| Cursor      | `.cursor/skills/`   |
| 其他        | `.ai/skills/`       |

---

## 分析流程

### Step 1: 快速识别 (30秒)

```bash
# 识别项目类型
ls -la                          # 根目录文件
cat package.json 2>/dev/null    # Node项目
cat Cargo.toml 2>/dev/null      # Rust项目
cat go.mod 2>/dev/null          # Go项目
cat pyproject.toml 2>/dev/null  # Python项目
```

**输出：** 语言、框架、包管理器

### Step 2: 五维分析 (5分钟)

| 维度           | 检查内容           | 关键文件                    |
| -------------- | ------------------ | --------------------------- |
| **身份** | 版本、依赖、工具链 | package.json, tsconfig.json |
| **架构** | 目录结构、模块边界 | src/, lib/, 实际目录        |
| **风格** | 命名、代码模式     | 采样5+文件                  |
| **版本** | 运行时、框架版本   | engines, .nvmrc             |
| **工具** | 脚本、hooks、CI    | scripts, .husky/            |

### Step 3: 生成项目Skill

**输出位置：** `{project-root}/.{agent}/skills/PROJECT.md`

**执行步骤：**
1. 读取模板：`assets/PROJECT.template.md`
2. 替换变量：将 `{{VARIABLE}}` 替换为 Step 2 分析出的实际值
3. 写入文件：确保目录存在，写入 `{project-root}/.{agent}/skills/PROJECT.md`

```
project-root/
  .{agent}/              ← 根据当前agent确定 (.opencode/.claude/.codex等)
    skills/
      PROJECT.md         ← 必须生成
```

---

## 模板说明

请直接使用 `assets/PROJECT.template.md` 作为生成的基础。

**关键填充变量 (需从项目提取):**

| 类别 | 变量 | 说明 |
|------|------|------|
| **身份** | `{{PROJECT_NAME}}` | package.json name |
| | `{{LANGUAGE}}`, `{{RUNTIME_VERSION}}` | TypeScript/Go/Rust, Node版本 |
| | `{{FRAMEWORK_VERSION}}`, `{{BUILD_TOOL}}` | React/Vue版本, Vite/Webpack |
| **架构** | `{{ACTUAL_DIRECTORY_STRUCTURE}}` | `tree -L 2 src/` 输出 |
| | `{{SRC_ROOT}}`, `{{COMPONENTS_PATH}}` | 关键路径 |
| **规范** | `{{VAR_EXAMPLES}}`, `{{COMP_EXAMPLES}}` | **必须**采样真实代码，不可臆造 |
| **风格** | `{{STATE_LIB}}`, `{{ASYNC_STYLE}}` | Zustand/Redux, async/await |
| **模板** | `{{COMPONENT_TEMPLATE}}` | 复制一个典型的现有组件 |
| **约束** | `{{PROHIBITED_1}}` | 根据反模式推断 |

**AI生成原则：**
- 如果某项无法确定，标记为 "TBD" 或询问用户，**不要编造**。
- `{{COMPONENT_TEMPLATE}}` 是最重要的部分，务必原样复制一个好的现有组件。

---

## AI约束规则

### 硬性约束 (违反即重写)

| 检查项       | 验证方法           |
| ------------ | ------------------ |
| 依赖必须存在 | 检查package.json   |
| 路径必须真实 | 检查目录存在       |
| 版本必须兼容 | 检查engines/target |
| 风格必须一致 | 对比现有代码       |

### 生成规则

1. **只用存在的依赖** - 不发明import
2. **只用存在的目录** - 不创建新结构
3. **复制真实代码** - 不编造示例
4. **引用版本号** - 从配置文件复制

---

## 红旗警告

发现以下情况立即停止：

- ❌ 无package.json等项目文件 → 确认项目类型
- ❌ 混合命名风格 → 需要人工确认规范
- ❌ 循环依赖 → 架构问题需讨论
- ❌ 无测试框架 → 无法安全开发

---

## 输出检查清单

生成PROJECT.md后验证：

- [ ] 所有版本号从配置文件复制
- [ ] 所有命令可实际执行
- [ ] 目录结构与实际一致
- [ ] 命名示例来自真实代码
- [ ] 组件模板来自真实文件
- [ ] 禁止模式基于项目现状

---

## 核心开发原则

### 原则 1：优先使用项目内方法

**优先级顺序：**

| 优先级 | 来源 | 使用规则 |
|--------|------|----------|
| 1 | 项目现有代码 | 优先复制现有模式，而非发明新方法 |
| 2 | 项目内工具函数 | 使用 `src/lib/`、`src/utils/` 中的工具 |
| 3 | 项目配置 | 使用 `src/config/` 中的配置，而非硬编码 |
| 4 | 项目类型定义 | 使用 `src/types/` 中的类型，而非重新定义 |
| 5 | 官方库方法 | 最后才考虑引入新依赖 |

**验证方法：**

```bash
# Step 1: 搜索现有实现
grep -r "function.*similar" src/ --include="*.ts"
grep -r "util\|helper" src/lib/ --include="*.ts"

# Step 2: 检查类型定义
grep "interface.*Similar" src/types/ --include="*.ts"

# Step 3: 检查配置
grep "SIMILAR_CONFIG" src/config/ --include="*.ts"
```

**禁止行为：**

- 引入项目已存在的工具库（如 lodash 当项目有 utils）
- 硬编码项目中有配置的值
- 重新定义项目已有的类型
- 使用与项目风格不符的第三方库

---

### 原则 2：提高 CBB 代码复用率

**CBB（Common Building Block）复用策略：**

| 复用级别 | 目标 | 实施方法 |
|----------|------|----------|
| L1: 原子复用 | 工具函数、常量 | 提取到 `src/lib/common/` |
| L2: 组件复用 | UI 组件、业务组件 | 提取到 `src/components/` |
| L3: 特性复用 | 完整功能模块 | 提取到 `src/features/` |
| L4: 跨项目复用 | 通用解决方案 | 提取到公司 CBB 仓库 |

**复用检查清单：**

```markdown
在编写新代码前，检查是否可复用：

1. [ ] 功能相似代码是否存在于 `src/lib/` 或 `src/utils/`？
2. [ ] 是否有可复用的 UI 组件在 `src/components/`？
3. [ ] 是否有相似业务逻辑在 `src/features/`？
4. [ ] 是否有跨项目的 CBB 可用（公司仓库）？
5. [ ] 当前代码是否可提取为新的 CBB？
```

**提取为 CBB 的标准：**

- 被 3+ 个地方使用
- 逻辑独立，无业务耦合
- 有完整的类型定义
- 有单元测试覆盖

**复用示例：**

<Good>
```typescript
// 优先使用项目内工具
import { formatDate, parseISO } from '@/lib/date-utils'
// 而不是引入 moment.js 或 date-fns
```
</Good>

<Bad>
```typescript
// 错误：引入项目已有功能
import moment from 'moment'
const date = moment().format('YYYY-MM-DD')
// 项目已有 date-utils，但未检查
```
</Bad>

---

### 原则 3：代码阅读友好 + 避免性能问题

**平衡原则：**

```
代码可读性 > 微量性能优化
但：明显的性能反模式不可接受
```

**可读性优先规则：**

| 场景 | 推荐做法 | 避免 |
|------|----------|------|
| 变量命名 | `const userEmailAddress` | `const uea` |
| 函数长度 | 单一职责，<50 行 | 函数做多件事 |
| 注释 | 解释为什么，而非做什么 | 逐行注释 |
| 结构 | 扁平优于深层嵌套 | 超过 3 层嵌套 |
| 魔法值 | 提取为常量 | 硬编码数字/字符串 |

**不可接受的性能反模式：**

| 反模式 | 影响 | 替代方案 |
|--------|------|----------|
| 在渲染中创建函数/对象 | 每次渲染都重新创建 | `useCallback`, `useMemo` |
| 大对象浅比较 | React.memo 失效 | 保持对象引用稳定 |
| 同步阻塞主线程 | UI 卡顿 | 使用 `setTimeout` 分片或 Web Worker |
| 不必要的深拷贝 | 内存浪费 | 浅拷贝或结构共享 |
| 循环中同步操作 | O(n²) 复杂度 | 批量操作或异步化 |

**性能检查清单：**

```markdown
代码提交前检查：

1. [ ] 事件处理函数是否使用 `useCallback`？
2. [ ] 复杂计算是否使用 `useMemo`？
3. [ ] 传递给子组件的对象引用是否稳定？
4. [ ] 是否有不必要的深拷贝？
5. [ ] 大数据是否使用了虚拟列表？

可读性检查：

1. [ ] 变量名是否自解释？
2. [ ] 函数是否单一职责？
3. [ ] 复杂逻辑是否有注释？
4. [ ] 魔法值是否提取为常量？
```

**正确示例：**

<Good>
```typescript
// 可读性优先，适当性能优化
const UserList: FC<Props> = ({ userIds }) => {
  // useMemo 避免重复计算
  const users = useMemo(() => 
    userIds.map(id => userMap[id]),
    [userIds, userMap]
  )

  // useCallback 保证引用稳定
  const handleSelect = useCallback((user: User) => {
    selectUser(user)
  }, [selectUser])

  return (
    <List>
      {users.map(user => (
        <UserItem 
          key={user.id}
          user={user}
          onSelect={handleSelect}  // 稳定引用
        />
      ))}
    </List>
  )
}
```
</Good>

<Bad>
```typescript
// 性能问题 + 可读性差
const UserList = ({ userIds }) => {
  const users = userIds.map(id => userMap[id])  // 无 useMemo
  const handleSelect = (user) => selectUser(user)  // 无 useCallback

  return (
    <List>
      {users.map(user => (
        <UserItem user={user} onSelect={handleSelect} />
      ))}
    </List>
  )
}
```
</Bad>

**底线：**

- 可读性永远优先于"可能"的性能收益
- 但明显的反模式（如渲染中创建对象）必须修复
- 性能优化基于测量，而非猜测

---

## 集成

**配套脚本：**
- `scripts/analyze.ps1`: Windows PowerShell 快速分析脚本
- `scripts/*.sh`: Linux/Mac Bash 分析脚本

**参考文档：** `references/` 目录下的详细指南
**模板素材：** `assets/PROJECT.template.md` (Handlebars风格模板)

**与其他agent协作：**

- @oracle: 架构决策分析
- @explore: 深度代码搜索See **PROJECT-SKILL-TEMPLATE.md** for complete template structure.
