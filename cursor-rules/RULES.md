# Cursor Rules 索引（精选）

来源：[sanjeed5/awesome-cursor-rules-mdc](https://github.com/sanjeed5/awesome-cursor-rules-mdc) `rules-mdc/`  
共 **52** 条 · 均 `alwaysApply: false`

## 安装位置

| 用途 | 路径 |
| --- | --- |
| **跨项目运行时（User Rules 文件）** | `%USERPROFILE%\.cursor\rules\` |
| **本仓库镜像（git）** | `skills/cursor-rules/` |

同步到本机全局：

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.cursor\rules" | Out-Null
Copy-Item "$env:USERPROFILE\.agents\skills\cursor-rules\*" "$env:USERPROFILE\.cursor\rules\" -Force
```

## 选型原则

对照本仓库 `skills/` 技术栈精选；未全量导入（上游 243），避免规则噪声。

## Frontmatter 策略

| 类型 | 策略 | 示例 |
| --- | --- | --- |
| 语言 / 框架文件匹配 | 保留或收紧 `globs` | `python`、`react`、`docker`、`next-js` |
| 库级 / 服务级 | 去掉 `globs` → Agent 按 description 拉取 | `fastapi`、`langchain`、`openai`、`stripe` |

> 上游大量 Python 库规则原为 `globs: **/*.py`，全开会冲突，故改为 agent-requested。

## 文件匹配（globs）

| Rule | Globs |
| --- | --- |
| `python` | `**/*.py` |
| `typescript` | `**/*.{ts,tsx}` |
| `react` | `**/*.{jsx,tsx}` |
| `next-js` | `**/app/**/*`、`**/pages/**/*`、`**/next.config.*` |
| `tailwind` | `**/*.{css,html,jsx,tsx}` |
| `zod` | `**/*.{ts,tsx}` |
| `eslint` | `**/*.{js,jsx,ts,tsx,mts,cts}` |
| `axios` | `**/*.{js,jsx,ts,tsx}` |
| `vite` | `**/vite.config.*` + JS/TS |
| `jest` | `**/*.{test,spec}.*`、`**/__tests__/**` |
| `playwright` | e2e/spec + `playwright.config.*` |
| `docker` | `Dockerfile`、`docker-compose*.{yml,yaml}` |
| `github-actions` | `**/.github/workflows/*.{yml,yaml}` |
| `kubernetes` | `**/k8s|kubernetes|helm/**` |
| `terraform` | `**/*.tf` |
| `graphql` | `**/*.{graphql,gql}` |

## Agent-requested（无 globs）

**Python 生态：** `fastapi` `pytest` `pydantic` `sqlalchemy` `numpy` `pandas` `opencv-python` `pytorch` `httpx` `requests` `poetry` `langchain` `langgraph` `huggingface` `transformers` `matplotlib` `scikit-learn` `streamlit` `pillow` `asyncio` `aiohttp`

**前端 / 移动：** `react-native` `shadcn` `css` `bash`

**基建 / SaaS：** `git` `ffmpeg` `nginx` `mongodb` `postgresql` `redis` `sqlite` `openai` `sentry` `stripe` `vercel`

## 与 Skills 映射（摘要）

| Skills 域 | Rules |
| --- | --- |
| FastAPI / Python TDD | `python` `fastapi` `pytest` `pydantic` `poetry` |
| Next/React/TS | `typescript` `react` `next-js` `tailwind` `vite` `zod` `eslint` |
| E2E / 单测 | `playwright` `jest` |
| Docker / K8s / CI | `docker` `kubernetes` `github-actions` `terraform` |
| CV / 科学计算 | `opencv-python` `numpy` `pandas` `pytorch` `matplotlib` `scikit-learn` |
| Agent / LLM | `langchain` `langgraph` `openai` `huggingface` `transformers` |
| 支付 / 可观测 | `stripe` `sentry` `vercel` |