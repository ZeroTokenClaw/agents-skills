# agents-skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Skills](https://img.shields.io/badge/skills-305-blue.svg)](./SKILLS.md)
[![GitHub](https://img.shields.io/badge/GitHub-ZeroTokenClaw%2Fagents--skills-181717?logo=github)](https://github.com/ZeroTokenClaw/agents-skills)

**开源**的 Cursor / Agent Skills 合集与备份镜像。

对应本机目录：`~/.agents/skills`（Windows：`%USERPROFILE%\.agents\skills`）。

| 项 | 值 |
| --- | --- |
| 维护账号 | [ZeroTokenClaw](https://github.com/ZeroTokenClaw) |
| Skill 数量 | **305**（每个子目录含 `SKILL.md`） |
| 可见性 | **Public** |
| 主分支 | `main` |
| 仓库许可 | [MIT](./LICENSE)（子目录可另有第三方许可） |
| 完整目录 | [`SKILLS.md`](./SKILLS.md) |

> Cursor 运行时读取的是本机 skills 目录；本仓库用于备份、分享与跨机同步。

---

## 目录

- [仓库结构](#仓库结构)
- [快速开始](#快速开始)
- [在 Cursor 中使用](#在-cursor-中使用)
- [如何选 Skill](#如何选-skill)
- [能力域概览](#能力域概览)
- [Skill 编写约定](#skill-编写约定)
- [贡献指南](#贡献指南)
- [许可与归属](#许可与归属)
- [FAQ](#faq)
- [相关链接](#相关链接)

---

## 仓库结构

```text
agents-skills/
├── README.md                 # 本说明
├── LICENSE                   # 仓库级 MIT + 第三方声明
├── SKILLS.md                 # 303 个 skill 完整目录
├── .gitignore
├── practical-skills-index/   # 总路由索引（优先读）
├── anbeime-skills-index/     # 中文垂直技能路由
├── <skill-name>/
│   ├── SKILL.md              # 必需：frontmatter + 使用说明
│   ├── LICENSE*              # 可选：该 skill 自身许可
│   ├── references/           # 可选：资料、源链接
│   ├── scripts/              # 可选：辅助脚本
│   ├── agents/               # 可选：openai.yaml 等
│   └── ...
└── ...
```

每个一级子目录 = 一个独立 skill。Agent 通过 `SKILL.md` 头部的 `name` / `description` 做触发匹配。

---

## 快速开始

### 全新安装到本机

```bash
# 建议先备份已有目录
mv ~/.agents/skills ~/.agents/skills.bak 2>/dev/null || true

git clone https://github.com/ZeroTokenClaw/agents-skills.git ~/.agents/skills
```

Windows（PowerShell）：

```powershell
$dest = "$env:USERPROFILE\.agents\skills"
if (Test-Path $dest) { Rename-Item $dest "skills.bak.$(Get-Date -Format yyyyMMdd)" }
git clone https://github.com/ZeroTokenClaw/agents-skills.git $dest
```

### 浅克隆（体积更小、更快）

```bash
git clone --depth 1 https://github.com/ZeroTokenClaw/agents-skills.git ~/.agents/skills
```

### 只取某一个 skill

```bash
# 稀疏检出示例：只要 megaflow
git clone --filter=blob:none --sparse https://github.com/ZeroTokenClaw/agents-skills.git /tmp/agents-skills
cd /tmp/agents-skills
git sparse-checkout set megaflow
cp -r megaflow ~/.agents/skills/
```

### 已有本地目录，只拉取更新

```bash
cd ~/.agents/skills
git pull origin main
```

### 本地改完后推回 GitHub（维护者）

```bash
cd ~/.agents/skills
git add -A
git status
git commit -m "feat(skills): update ..."
git push origin main
```

---

## 在 Cursor 中使用

1. 确认 skills 落在 Cursor 可发现路径（常见为 `~/.agents/skills` 或 Cursor Agent Stores 同步目录）。
2. 新开 Agent 对话，直接描述任务；模型会按各 skill 的 `description` 自动匹配。
3. 也可显式指定：「按 `practical-skills-index` 选型」或「使用 `megaflow` skill」。
4. 修改 skill 后一般无需重启；若未生效，新开一轮对话即可。

### 跨项目 Cursor Rules

精选 `.mdc` 已独立维护于 [ZeroTokenClaw/rules](https://github.com/ZeroTokenClaw/rules)。跨项目安装：

```powershell
git clone https://github.com/ZeroTokenClaw/rules.git $env:TEMP\ztc-rules
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.cursor\rules" | Out-Null
Copy-Item "$env:TEMP\ztc-rules\*.mdc","$env:TEMP\ztc-rules\RULES.md" "$env:USERPROFILE\.cursor\rules\" -Force
```

本地开发目录：`~/.agents/rules`（与 GitHub 仓同步）。

可选发现渠道：

- 本地索引：`practical-skills-index` / `anbeime-skills-index`
- 社区：`npx skills find <关键词>` · [skills.sh](https://skills.sh/)

---

## 如何选 Skill

不要从 300+ 目录里盲翻。按场景读索引：

| 场景 | 入口 Skill |
| --- | --- |
| 总路由（办公 / Web / 产品 / 算法 / 机器人 / 内容） | **`practical-skills-index`** |
| 内容创作、短视频、电商、TTS、数字人、Obsidian | **`anbeime-skills-index`** |
| LangGraph / 编码 Agent 编排 | `langgraph-coding-agent` |
| 计算 / 财务 / 数据分析 | `calc-analysis-skills` |
| 产品 / 前端 / 测试工具链 | `product-dev-skills` |
| 宇树具身能力包 | `unitree-embodied-skills` |

### 快捷路由（摘自总索引）

| 任务 | Skill |
| --- | --- |
| 网页 / UI | `frontend-design` |
| React 性能 | `vercel-react-best-practices` |
| E2E | `playwright-testing` |
| PPT | `pptx` / `ppt-generator` |
| 大位移光流 / 点跟踪 | `megaflow` |
| 专利交底 / 权利要求 | `patent-drafting` |
| 软著登记材料 | `software-copyright-cn` |
| 人脸签到 + 导览跟随 | `tour-checkin-follow` |
| 短视频全流程 | `video-creation-suite` |
| 跨境电商 | `ecommerce-full-pipeline` |
| 架构交互图 | `archify` |

完整清单见 [`SKILLS.md`](./SKILLS.md)。

---

## 能力域概览

以下为便于浏览的粗分（有交叉，以索引表为准）：

### 索引与 Skill 工程

`practical-skills-index` · `anbeime-skills-index` · `find-skills` · `suggesting-skills` · `writing-skills` · `building-skills-from-patterns` · `using-agent-skills` · `using-superpowers`

### 计算机视觉 / 机器人 / 具身

含 YOLO 全家桶、OpenCV、SLAM/Nav2、宇树 G1/Go2、人脸签到跟随、光流点跟踪等：

`yolo` · `yolo-pipeline` · `yolo-training` · `yolo-models` · `yolo-datasets` · `yolo-integration` · `opencv` · `computer-vision-opencv` · `computer-vision-pipeline` · `megaflow` · `multi-object-tracking` · `cv-mediapipe` · `slam` · `laser-slam` · `nav-slam` · `nav2-integration` · `occupancy-map` · `unitree-g1` · `unitree-go2-sdk-skill` · `unitree-robot` · `go2-robot-control` · `robot-person-follow` · `face-checkin-robot` · `tour-checkin-follow` · `embodied-tour-nav` · `embodied-voice-stack` · `drone-cv-expert` · `deepstream-dev` · `kimodo-motion-diffusion` · `motion-control` · `spacemit-robot-vision` · …

### 内容创作 / 短视频 / 电商 / 语音

`intelligent-content-system` · `content-creation-publisher` · `video-creation-suite` · `viral-video-copywriting` · `ecommerce-full-pipeline` · `infinitetalk` · `digital-avatar-shopping-video` · `tts-voice-synthesis` · `qwen3-tts-local` · `qwen3-asr-assistant` · `baoyu-*` · `wechat-hotspot-publisher` · `xiaohongshu-makeup` · …

### 前端 / UI / 设计

`frontend-design` · `design-system` · `ui-design` · `ui-ux-pro-max` · `web-design-guidelines` · `figma-generate-design` · `canvas-design` · `mobile-app-ui-design` · `vercel-react-best-practices` · `nextjs-react-typescript` · `accessibility-a11y` · …

### 后端 / DevOps / 安全

`fastapi-backend-template` · `backend-api-design` · `api-architect` · `mcp-builder` · `docker-patterns` · `multi-stage-dockerfile` · `kubernetes-deploying` · `ci-cd-and-automation` · `setting-up-ci` · `frontend-security` · `security-and-hardening` · `antinet-security-scan` · …

### 数据 / 金融 / 办公文档

`data-analysis` · `exploratory-data-analysis` · `financial-modeling` · `dcf-model` · `3-statement-model` · `stock-analysis` · `xlsx` · `docx` · `pdf` · `pptx` · `ppt-generator` · `meeting-notes` · `excel` · …

### 知识产权（专利 / 软著）

`patent-drafting` · `software-copyright-cn` · `contract-review` · `law-to-markdown`

### Agent 协作与工程流程

`agent-plan-mode` · `agent-team` · `agent-subagent-orchestration` · `agent-spec-creator` · `langgraph-coding-agent` · `spec-driven-development` · `test-driven-development` · `systematic-debugging` · `creating-pr` · `git-workflow-and-versioning` · `parallel-code-review` · `brainstorming` · `writing-plans` · …

---

## Skill 编写约定

新增或修改 skill 时建议遵守：

1. **目录名** = skill `name`（小写、短横线）
2. **`SKILL.md` 必需**，YAML frontmatter 至少包含：

   ```yaml
   ---
   name: example-skill
   description: >-
     何时触发、关键词、适用任务（中英均可）。
   ---
   ```

3. 正文写清：环境依赖、输入输出、命令/API、风险与选型对比
4. 长资料放 `references/`，可执行逻辑放 `scripts/`
5. 若有上游，在 `references/source.md` 写明仓库 / 论文 / License
6. 提交前确认无 `.env`、密钥、本地绝对路径隐私

可参考：`writing-skills`、`building-skills-from-patterns`。

---

## 贡献指南

欢迎 PR / Issue：

1. Fork 本仓库并基于 `main` 开分支
2. 每个 PR 尽量只改一个 skill（或一组强相关 skill）
3. 更新 `SKILL.md` 时同步检查 description 触发词是否准确
4. 新增 skill 后更新 [`SKILLS.md`](./SKILLS.md)（或说明由维护者代更）
5. 不要提交：`node_modules/`、权重文件、数据集、密钥

Issue 建议包含：skill 名、期望行为、复现对话摘要。

---

## 许可与归属

- **仓库级**：MIT（见 [`LICENSE`](./LICENSE)）
- **子目录**：部分 skill 自带 `LICENSE` / `LICENSE.txt`，以其为准
- **来源示例**：
  - 中文垂直合集路由参考 [anbeime/skill](https://github.com/anbeime/skill)
  - 个别 skill 内 `references/source.md`（如 MegaFlow → [cvg/megaflow](https://github.com/cvg/megaflow)）

再分发子集时请保留对应子目录的许可与归属信息。

---

## FAQ

**Q: Clone 后 Cursor 仍找不到 skill？**  
A: 确认路径是否为 Cursor 实际扫描目录；必要时在对话中显式点名 skill，或检查 Agent Stores 是否另有副本。

**Q: 可以只装部分 skill 吗？**  
A: 可以。用稀疏检出，或直接复制单个子目录到 `~/.agents/skills/<name>/`。

**Q: 仓库很大吗？**  
A: 约数十 MB 量级（以文档与脚本为主）。可用 `--depth 1` 浅克隆。

**Q: 与 skills.sh / 官方商店是什么关系？**  
A: 本仓库是个人维护的合集镜像，不替代官方商店；可并存，按名称去重即可。

---

## 常用命令速查

```bash
# 仓库状态
git -C ~/.agents/skills status -sb

# 统计 skill 数
find ~/.agents/skills -mindepth 1 -maxdepth 1 -type d ! -name '.git' | wc -l

# 搜索含某关键词的 skill
rg -l "MegaFlow|光流" ~/.agents/skills --glob 'SKILL.md'

# 列出全部目录名
git -C ~/.agents/skills ls-tree -d --name-only HEAD
```

---

## 相关链接

- 仓库：https://github.com/ZeroTokenClaw/agents-skills
- 完整目录：[`SKILLS.md`](./SKILLS.md)
- 总索引：[`practical-skills-index/SKILL.md`](./practical-skills-index/SKILL.md)
- 中文垂直索引：[`anbeime-skills-index/SKILL.md`](./anbeime-skills-index/SKILL.md)
- 社区发现：[skills.sh](https://skills.sh/) · [anbeime/skill](https://github.com/anbeime/skill)
