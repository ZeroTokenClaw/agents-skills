# AI约束速查表

## 10条铁律

| # | 规则 | 验证方法 |
|---|------|---------|
| 1 | **只用存在的依赖** | 检查package.json |
| 2 | **只用存在的目录** | ls验证路径 |
| 3 | **复制真实代码** | 从项目采样 |
| 4 | **遵守版本约束** | 检查engines/target |
| 5 | **风格完全一致** | 对比5+文件 |
| 6 | **异步模式统一** | 全用async/await或全用promises |
| 7 | **错误处理一致** | 遵循项目模式 |
| 8 | **导入路径真实** | tsconfig paths验证 |
| 9 | **禁用通用命名** | 具体描述用途 |
| 10 | **遵守禁止模式** | 检查项目skill清单 |

## 幻觉检测

看到以下立即STOP：

```typescript
// ❌ 未知依赖
import { X } from 'unknown-package'

// ❌ 不存在的路径
import { Y } from '@/lib/features/deep/nested'

// ❌ 错误风格
class UserCard extends Component { }  // 项目用函数式

// ❌ 虚构API
const { data } = useGraphQL(query)  // 项目没有GraphQL

// ❌ 通用命名
const Component = () => { }
const data = fetchData()
```

## 代码审查清单

- [ ] imports都在package.json
- [ ] 路径都存在
- [ ] 命名遵循规范
- [ ] 无禁止模式
- [ ] 类型明确（无any）
- [ ] 有测试

## Prompt模板

```markdown
你在 {{project}} 项目中工作。
遵循 .{agent}/skills/PROJECT.md 中的约束。
# agent目录: .opencode/.claude/.codex/.cursor/.ai

任务: {{task}}

约束:
- 只用package.json中的依赖
- 遵循命名规范: {{naming}}
- 状态管理: {{state}}
- 必须包含测试

如有不确定，先问再做。
```
