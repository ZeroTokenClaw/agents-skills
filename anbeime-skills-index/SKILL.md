---
name: anbeime-skills-index
description: >-
  Route to Chinese vertical skills sourced from anbeime/skill store: content
  publishing, short video, ecommerce, TTS/ASR, digital avatar, arch diagrams,
  multi-agent teams, legal docs, stock analysis, Obsidian, resume. Trigger on
  内容创作、公众号、小红书、短视频、电商、带货、TTS、配音、数字人、架构图、
  archify、多智能体、合同审核、专利、软著、软件著作权、论文分析、Obsidian、简历、
  技能商店、anbeime。
---

# anbeime 技能商店路由

来源：[anbeime/skill](https://github.com/anbeime/skill)（`skills/` + `antinet-agentteams/skills` 已全量可用包拷入）。  
总索引：`practical-skills-index`。具身实时语音优先 `embodied-voice-stack`。

空壳未装：`NanoBanana-PPT-Skills`、`baoyu-skills`（仓库内为空目录/未检出子模块）。  
未装：`_template`。

## 内容创作与发布

| 任务 | 优先 | 备选 |
| --- | --- | --- |
| 采集→配图→多平台发布 | **`intelligent-content-system`** | `content-creation-publisher` |
| 网页→MD→微信/X | `content-creation-publisher` | `baoyu-url-to-markdown` + `baoyu-post-to-wechat` |
| 长文配图 | `article-illustrator` | — |
| 研究写作 | `content-research-writer` | — |
| 微信热点 / 同步发布 | `wechat-hotspot-publisher` | `wechatsync-publisher` |
| 发 X 长文 | `qiaomu-x-article-publisher` | `baoyu-post-to-x` |
| 小红书封面 / 美妆 | `atutun-xhs-cover` | `xiaohongshu-makeup` |
| MD 格式化 | `baoyu-format-markdown` | — |

## 短视频 / 数字人

| 任务 | 优先 | 备选 |
| --- | --- | --- |
| 视频创作总入口 | **`video-creation-suite`** | `video-creation-collaborator`、`video-creation-pro` |
| 爆款文案 | `viral-video-copywriting` | — |
| 二创 / 抽帧 / 字幕下载 | `video-recreation` | `video-frame-extractor`、`video-transcript-downloader` |
| 媒体转码 / Remotion | `media-processor` | `remotion-video-enhancer` |
| 音频驱动口型 | **`infinitetalk`** | `infinitetalk-shopping-avatar` |
| 数字人带货成片 | `digital-avatar-shopping-video` | `agentkit-multimedia-shopping` |
| 即梦提示词 | `dream-video-prompt-generator` | — |
| 历史科普 / 访谈 / 三体向 | `historical-science-video-prod` | `historical-interview-scripts`、`three-body-video-creator` |

## 电商与营销

| 任务 | 优先 | 备选 |
| --- | --- | --- |
| 跨境全链路 | **`ecommerce-full-pipeline`** | — |
| 商品图文案 | `ecommerce-copywriter` | `product-marketing-copywriter` |
| 带货视频脚本 | `ecommerce-video-marketing` | `product-video-creator`、`pet-commerce-creator` |
| 生图 Prompt | `gpt-image-2-prompt-engine` | `icon-generator` |

## 语音（内容向）

| 任务 | 优先 | 备选 |
| --- | --- | --- |
| 配音 / 音色克隆 | **`tts-voice-synthesis`** | `qwen3-tts-local` |
| ASR 转写 | `qwen3-asr-assistant` | — |
| 机器人实时语音环 | `embodied-voice-stack` | 上二者作 offline |

## 工程可视化 / Agent / 自动化

| 任务 | 优先 | 备选 |
| --- | --- | --- |
| 架构/时序交互图 | **`archify`** | `design-doc-mermaid` |
| 依赖图 / 影响分析 | `ontoly-software-graph` | — |
| 动态 AI 团队 | `agent-team` | `multi-agent-meeting` |
| Chrome CDP | `chrome-automation` | — |
| 网页→桌面应用 | `web-to-app` | — |
| 现有站设计分析 | `web-design-analyzer` | `frontend-design` |

## 文档 / 法务 / 知识库 / 分析 / PPT

| 任务 | 优先 | 备选 |
| --- | --- | --- |
| 多格式文档解析 | `antinet-doc-parse` / `doc-parse` | `pdf-processing-pro`、`pdf` |
| 四色卡片研报 | `antinet-four-color-cards` / `four-color-cards` | — |
| 溯源审计 / 安全扫描 | `antinet-provenance`、`antinet-security-scan` | `provenance`、`security-scan` |
| 合同 / 法条 | `contract-review` | `law-to-markdown` |
| 专利交底 / 权利要求 / 说明书 | **`patent-drafting`** | — |
| 软著登记材料 / 鉴别材料 | **`software-copyright-cn`** | — |
| Obsidian 笔记 | `obsidian-skills-integrated` | `obsidian-markdown`、`obsidian-bases`、`json-canvas` |
| arXiv / 个股 / 数据叙事 | `paper-analysis-assistant` | `stock-analysis`、`data-storytelling` |
| 产品经理 / 简历 | `product-manager-toolkit` | `tailored-resume-generator` |
| PPT | `ppt-generator` | `pptx`、`pptx-generator`、`nanobanana-ppt-visualizer`、`ppt-roadshow-generator` |

## 文化 / 轻量创作

| 任务 | 优先 |
| --- | --- |
| 睡前故事 | `bedtime-story` |
| 诗词配图配乐 | `poetry-music-visual` |
| 立体书插画 | `pop-up-book-illustration` |
| Agent 社交人设 | `moltbook` |

## 快捷路由

1. 自媒体全流程 → `intelligent-content-system`
2. 短视频 → `video-creation-suite`；数字人带货 → `digital-avatar-shopping-video`
3. 跨境电商 → `ecommerce-full-pipeline`
4. 配音 → `tts-voice-synthesis`；机器人语音 → `embodied-voice-stack`
5. 架构图 → `archify`；四色研报 → `four-color-cards`
6. Obsidian → `obsidian-skills-integrated`
7. 多智能体 → `agent-team`

补装单包：`npx skills add anbeime/skill --full-depth -s <name> -g -y`  
商店：https://github.com/anbeime/skill
