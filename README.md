# agents-skills

Cursor / Agent Skills 完整备份仓库。

对应本机目录：`~/.agents/skills`（Windows：`%USERPROFILE%\.agents\skills`）。

| 项 | 值 |
| --- | --- |
| 维护账号 | [ZeroTokenClaw](https://github.com/ZeroTokenClaw) |
| Skill 数量 | **303**（每个子目录含 `SKILL.md`） |
| 默认可见性 | Private |
| 主分支 | `main` |

---

## 仓库结构

```text
agents-skills/
├── README.md                 # 本说明
├── .gitignore
├── practical-skills-index/   # 总路由索引（优先读）
├── anbeime-skills-index/     # 中文垂直技能路由
├── <skill-name>/
│   ├── SKILL.md              # 必需：frontmatter + 使用说明
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

Private 仓库需已登录 GitHub（`gh auth login` 或配置 credential）。

### 已有本地目录，只拉取更新

```bash
cd ~/.agents/skills
git pull origin main
```

### 本地改完后推回 GitHub

```bash
cd ~/.agents/skills
git add -A
git status
git commit -m "feat(skills): update ..."
git push origin main
```

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

在 Cursor 对话里直接描述任务即可；Agent 会按 description 触发对应 skill。也可显式要求：「按 `practical-skills-index` 选型」。

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

### Agent 协作与工程流程

`agent-plan-mode` · `agent-team` · `agent-subagent-orchestration` · `agent-spec-creator` · `langgraph-coding-agent` · `spec-driven-development` · `test-driven-development` · `systematic-debugging` · `creating-pr` · `git-workflow-and-versioning` · `parallel-code-review` · `brainstorming` · `writing-plans` · …

完整目录名列表可用：

```bash
ls ~/.agents/skills
# 或
git -C ~/.agents/skills ls-tree -d --name-only HEAD
```

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
5. 提交前确认无 `.env`、密钥、本地绝对路径隐私

可参考：`writing-skills`、`building-skills-from-patterns`。

---

## 同步与协作说明

- 本仓库是 **Cursor 本地 skills 的镜像**；Cursor 运行时读的是本机 `~/.agents/skills`，不是 GitHub 远程。
- 改 skill 后需 `git push`，换机用 `git pull` / `clone` 才能对齐。
- 部分 skill 来自公开技能商店或上游项目（如 anbeime、各类开源模板），保留原 License / 来源说明（见各 skill 内 `LICENSE*`、`references/source.md`）。
- 聚合分发请自行核对第三方许可；默认保持 **Private**。

---

## 常用命令速查

```bash
# 仓库状态
git -C ~/.agents/skills status -sb

# 统计 skill 数
find ~/.agents/skills -mindepth 1 -maxdepth 1 -type d ! -name '.git' | wc -l

# 搜索含某关键词的 skill
rg -l "MegaFlow|光流" ~/.agents/skills --glob 'SKILL.md'
```

---

## 相关链接

- 仓库：https://github.com/ZeroTokenClaw/agents-skills
- 总索引：[`practical-skills-index/SKILL.md`](./practical-skills-index/SKILL.md)
- 中文垂直索引：[`anbeime-skills-index/SKILL.md`](./anbeime-skills-index/SKILL.md)
