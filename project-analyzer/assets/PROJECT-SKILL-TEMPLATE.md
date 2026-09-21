# Project-Specific Skill Template

**Location:** `project-root/.{agent}/skills/PROJECT.md`

根据当前使用的AI Agent工具选择目录：
- Claude Code → `.claude/skills/`
- OpenCode → `.opencode/skills/`
- Codex → `.codex/skills/`
- Cursor → `.cursor/skills/`
- 其他 → `.ai/skills/`

This template guides agents in understanding and following project-specific constraints. Copy this template into your project's `.{agent}/skills/` directory and fill in the blanks with your actual project data.

## Template Structure

```markdown
---
name: [project-name]
description: Use when working on [project-name] to follow specific conventions and avoid breaking changes
---

# [Project Name] Constraints

## Identity
**Tech Stack:**
- Language: [e.g., TypeScript 5.3]
- Runtime: [e.g., Node.js 20 (from package.json engines)]
- Package manager: [e.g., pnpm 8.10]
- Framework: [e.g., React 18.2, Next.js 14]

**Commands:**
\`\`\`bash
pnpm install          # Install dependencies
pnpm run dev          # Start dev server (port 3000)
pnpm run build        # Production build
pnpm run test         # Run test suite
pnpm run type-check   # TypeScript validation
pnpm run lint         # ESLint check
\`\`\`

**Tools & Configuration:**
- Build: [Vite/Webpack/esbuild] (config in [file])
- Linter: ESLint (see .eslintrc.json)
- Formatter: Prettier (see .prettierrc)
- Type checker: [if separate from build]
- Test runner: Jest (config in jest.config.ts)

## Architecture Summary

**Directory structure:**
\`\`\`
src/
  pages/           → Route components (Next.js)
  components/      → Reusable UI components
  hooks/           → Custom React hooks
  lib/             → Utilities & helpers
  types/           → Shared TypeScript types
  styles/          → Global styles (CSS modules)
  __tests__/       → Test files (mirror src structure)
\`\`\`

**Module organization:**
- [Describe pattern: flat, feature-based, layered, etc.]
- [Entry point: src/index.ts]
- [Public APIs: Exported from feature index files]
- [Dependency flow: Describe allowed directions]

**Architectural decisions:**
- State management: [Zustand/Redux/Context/useState]
- Data fetching: [React Query/SWR/fetch/graphql]
- Styling: [CSS Modules/Tailwind/styled-components]
- Component style: [Functional components + hooks only]
- Async patterns: [async/await (not promises)]

## Naming Conventions

**Variables & functions:**
```typescript
// ✓ CORRECT: camelCase, descriptive names
const userEmail = "test@example.com"
function validateEmail(email: string): boolean { }
const handleButtonClick = () => { }

// ✗ WRONG: Hungarian notation, abbreviations
const strEmail = "test@example.com"
const btn_click = () => { }
const usr = { } // "user" is better than "usr"
```

**Components:**
```typescript
// ✓ CORRECT: PascalCase, clear purpose
export function UserCard({ user }: UserCardProps) { }
export const LoginForm = () => { }

// ✗ WRONG: kebab-case, generic names
export const user-card = () => { }
export const Component = () => { }
```

**Files:**
```
// ✓ CORRECT structure
src/
  components/
    UserCard/
      UserCard.tsx        (component)
      UserCard.module.css (styles)
      UserCard.types.ts   (types)
      __tests__/
        UserCard.test.tsx

// ✗ WRONG structure
src/
  UserCard.tsx
  usercardstyles.css
  types.ts
```

## Code Style

**Type definitions:**
```typescript
// ✓ CORRECT: Explicit interface for props
interface ButtonProps {
  label: string
  onClick: (e: React.MouseEvent) => void
  disabled?: boolean
}

// ✗ WRONG: Implicit any, loose types
const Button = (props) => { }
```

**State management (using Zustand):**
```typescript
// ✓ CORRECT: Slice pattern with clear actions
export const useUserStore = create<UserStore>((set) => ({
  user: null,
  setUser: (user: User) => set({ user }),
  clearUser: () => set({ user: null }),
}))

// ✗ WRONG: Unorganized, unclear responsibilities
const store = createStore()
store.user = null
```

**Error handling:**
```typescript
// ✓ CORRECT: Try-catch with specific error types
try {
  const user = await fetchUser(id)
} catch (error) {
  if (error instanceof UserNotFoundError) {
    console.error('User not found')
  }
}

// ✗ WRONG: Swallowing errors, generic catch
try {
  await fetchUser(id)
} catch (e) {
  console.log('error')
}
```

**Async patterns:**
```typescript
// ✓ CORRECT: async/await, promises only when needed
async function loadUsers() {
  const users = await api.getUsers()
  return users
}

// ✗ WRONG: Mixing promises and callbacks
function loadUsers() {
  return api.getUsers().then(u => u).catch(err => console.log(err))
}
```

## Testing

**Test file structure:**
```
src/
  components/
    Button/
      __tests__/
        Button.test.tsx  (mirror the component)
```

**Test naming:**
```typescript
// ✓ CORRECT: Describe-it structure
describe('Button', () => {
  it('should render with label text', () => {
    render(<Button label="Click me" />)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })
})

// ✗ WRONG: Unclear test names
describe('Button', () => {
  it('works', () => { })
})
```

**Coverage requirements:**
- Critical path: ≥ 80% coverage
- New code: ≥ 90% coverage
- Skip coverage only with explicit comment: `// skip coverage` with reason

## Component Templates

### Functional Component with Hooks
```typescript
import { FC } from 'react'
import styles from './MyComponent.module.css'

interface MyComponentProps {
  title: string
  onClose?: () => void
}

export const MyComponent: FC<MyComponentProps> = ({ title, onClose }) => {
  // Hooks
  const [isOpen, setIsOpen] = useState(false)

  // Effects
  useEffect(() => {
    // Side effects
  }, [])

  // Handlers
  const handleOpen = () => setIsOpen(true)

  // Render
  return (
    <div className={styles.container}>
      <h1>{title}</h1>
      {/* Content */}
    </div>
  )
}
```

### Custom Hook
```typescript
interface UseMyHookReturn {
  data: T | null
  isLoading: boolean
  error: Error | null
}

export function useMyHook(id: string): UseMyHookReturn {
  const [data, setData] = useState<T | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    // Implementation
  }, [id])

  return { data, isLoading, error }
}
```

## Prohibited Patterns

**NEVER do these in this project:**

| Pattern | Why | Alternative |
|---------|-----|-------------|
| `any` type | Type safety broken | Use `unknown` with type guard |
| Class components | Against project style | Use functional + hooks |
| Redux | Uses Zustand | Add to Zustand store |
| Direct DOM manipulation | React manages DOM | Use React refs if absolutely needed |
| Inline styles | Breaks styling system | Use CSS modules |
| console.log in production code | Noisy logs | Use logger utility (src/lib/logger.ts) |
| Props drilling (>3 levels) | Maintainability issue | Use context or Zustand |
| Promise chains | Harder to read | Use async/await |

## Import Rules

**Allowed imports:**
```typescript
// ✓ Relative imports within same feature
import { utils } from '../utils'
import { Button } from '../components/Button'

// ✓ Absolute imports from src
import { useUserStore } from '@/stores/userStore'
import { validateEmail } from '@/lib/validation'

// ✓ External packages
import { useEffect } from 'react'
import axios from 'axios'
```

**Forbidden imports:**
```typescript
// ✗ Crossing layer boundaries
import { useUserStore } from '../../../../../stores' // Use absolute path

// ✗ Circular dependencies
// components/A imports components/B
// components/B imports components/A

// ✗ Importing from nested folders
import { util } from '../lib/utils/nested/deep/util' // Export from index.ts instead
```

## Environment & Configuration

**Environment variables:**
- Required: `NEXT_PUBLIC_API_URL` (backend API endpoint)
- Optional: `NEXT_PUBLIC_DEBUG` (set to "true" for verbose logging)
- Never commit: Database credentials, secrets

**Configuration files (DO NOT MODIFY):**
- tsconfig.json (TypeScript settings)
- jest.config.ts (test configuration)
- .eslintrc.json (linting rules)
- .prettierrc (formatting)

## Performance Considerations

- Keep components under 300 lines (break into smaller components)
- Memoize expensive computations: `useMemo()`
- Prevent unnecessary re-renders: `useCallback()` for handlers
- Code split: Use `React.lazy()` for route components
- Bundle size: Check before adding external dependencies

## Common Mistakes to Avoid

1. **Forgetting dependency arrays:** Every useEffect must have explicit deps array
2. **Mutating state directly:** Use setState, not `state.property = value`
3. **Missing keys in lists:** Always provide stable key prop
4. **Mixing CSS-in-JS:** Stick to CSS modules only
5. **Hardcoded strings:** Extract to constants or i18n
6. **Silent failures:** Always handle and log errors
7. **Not reusing CBB:** Check `src/lib/`, `src/components/` before writing new code
8. **Performance anti-patterns:** Creating objects/functions in render

## Core Development Principles

### Principle 1: Prefer In-Project Methods

**Priority Order:**

| Priority | Source | Rule |
|----------|--------|------|
| 1 | Existing code | Copy existing patterns, don't invent |
| 2 | Project utilities | Use `src/lib/`, `src/utils/` |
| 3 | Project config | Use `src/config/` not hardcoded |
| 4 | Project types | Use `src/types/` not re-define |
| 5 | External libraries | Last resort |

### Principle 2: Maximize CBB Reuse

**CBB Levels:**

- **L1 Atoms:** `src/lib/common/` - utils, constants
- **L2 Components:** `src/components/` - UI, business components
- **L3 Features:** `src/features/` - complete modules
- **L4 Cross-project:** Company CBB repository

**Before Writing New Code:**

1. [ ] Check `src/lib/` for utilities
2. [ ] Check `src/components/` for UI
3. [ ] Check `src/features/` for similar logic
4. [ ] Check company CBB
5. [ ] Consider extracting current code as new CBB

### Principle 3: Readability + Performance Balance

**Readability First:**

- Clear variable names over abbreviations
- Single-responsibility functions
- Comments explain "why", not "what"
- Extract magic numbers to constants

**Performance Non-Negotiables:**

- Use `useCallback` for handlers passed to children
- Use `useMemo` for expensive computations
- Stable object references (don't create in render)
- No deep copies unless necessary

## Questions Before Starting Work

1. Is the feature already in the codebase? Search first!
2. Does it violate any prohibited patterns?
3. Does it follow the naming convention exactly?
4. Are types explicit? (No `any`, no implicit types)
5. Is there test coverage? (New code requires tests)
6. Does it fit the architecture? (Ask before major refactors)
7. Can I reuse existing CBB? (Check `src/lib/`, `src/components/`)
8. Are performance patterns correct? (`useCallback`, `useMemo`)

## Questions Before Starting Work

1. Is the feature already in the codebase? Search first!
2. Does it violate any prohibited patterns?
3. Does it follow the naming convention exactly?
4. Are types explicit? (No `any`, no implicit types)
5. Is there test coverage? (New code requires tests)
6. Does it fit the architecture? (Ask before major refactors)

---

**Remember:** This skill exists to help AI agents (and you!) understand constraints quickly. Keep it updated as the project evolves.
```

## How to Use This Template

### Step 1: Create Project Skill Directory
```bash
mkdir -p .claude/skills
```

### Step 2: Copy and Customize
```bash
cp ~/.config/opencode/superpowers/skills/project-analyzer/PROJECT-SKILL-TEMPLATE.md .claude/skills/PROJECT.md
```

### Step 3: Fill in Your Project Details

For each section, follow these rules:

| Section | Rule |
|---------|------|
| Identity | Copy exact versions from package.json & actual shell commands |
| Architecture | List actual directories, not theoretical patterns |
| Naming | Show 3-5 real examples from your codebase |
| Code Style | Include actual code snippets from your project |
| Testing | Show exact test structure with real examples |
| Templates | Copy working code from your project |
| Prohibited | List actual violations you've seen |

### Step 4: Keep It Updated

Update the skill when you:
- Upgrade frameworks or major dependencies
- Change architectural decisions
- Establish new conventions
- Add or remove prohibited patterns

**Version it in git** like any other documentation.

---

## Checklist: Is Your Project Skill Complete?

- [ ] Identity section has exact versions (copy-paste from package.json)
- [ ] Every command listed actually works (`pnpm run build` runs successfully)
- [ ] Architecture section matches your actual directory structure
- [ ] Naming convention shows real examples from code
- [ ] Code style shows actual patterns from existing codebase
- [ ] Component templates are copy-pasted, not invented
- [ ] Test examples use your actual test framework
- [ ] Prohibited patterns list at least 5 real mistakes
- [ ] All import paths are correct
- [ ] Environment variables are documented
- [ ] Performance rules match project constraints

If any item is missing or invented, fix it before sharing with AI agents.
