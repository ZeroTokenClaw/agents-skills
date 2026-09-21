---
name: embodied-voice-stack
description: >-
  Use when designing or implementing embodied-AI / robot voice pipelines
  (Wake/KWS → VAD → ASR → LLM/Agent → TTS → Actuator), choosing ASR/TTS/VAD
  stacks for ROS2/Jetson/RISC-V/edge robots, or integrating barge-in, AEC, and
  tool-calling with motion. Trigger on 具身智能语音、机器人语音、ASR+LLM+TTS、
  ROS2 voice, EdgeVox, FunASR, CosyVoice, sherpa-onnx, Piper.
---

# 具身智能语音技术栈

## 何时使用

- 为机器人 / 具身 Agent 选型或落地语音链路
- 对比本地 / 云端 / 混合 ASR·TTS·VAD·KWS
- 对接 ROS2 topic、打断（barge-in）、回声消除（AEC）
- 查阅 GitHub 上可复用的开源参考实现

相关 skill：`embodied-tour-nav`（导览导航 / Nav2 / POI）；`spacemit-robot-speech`（SpacemiT SDK）；本 skill 覆盖跨厂商语音选型。

## 标准流水线

```text
Mic
 → Wake / KWS（可选）
 → VAD / 端点检测
 → ASR（流式优先）
 → LLM / Agent（流式 + tools → 运动/导航/抓取）
 → TTS（流式优先）
 → Speaker
 ↔ Barge-in / AEC（播报时可被打断；抑制自听）
```

具身差异点（相对纯语音助手）：

1. ASR 结果必须能触发 **tool / skill → 本体动作**，不只是闲聊
2. TTS 与运动并行时需 **安全抢占**（急停 > 语音打断 > 技能取消）
3. 现场噪声、电机噪声、自扬声 → 必须考虑 **VAD 门限 + AEC + 能量比门控**
4. 边端算力有限 → 优先 **流式小模型 / ONNX / sherpa**，云端仅作可选升级

## 组件选型矩阵（GitHub 高频）

| 层 | 中文 / 边端优先 | 英文 / 通用本地 | 云 / 混合 | 备注 |
| --- | --- | --- | --- | --- |
| KWS | sherpa-onnx KeywordSpotter | openWakeWord / pymicro-wakeword | 厂商 SDK | 中文唤醒用 sherpa 训练关键词 |
| VAD | FunASR fsmn-vad / Silero / FireRedVAD | Silero VAD / WebRTC VAD | — | 流式帧 20–32 ms 常见 |
| ASR | FunASR Paraformer / SenseVoice / Fun-ASR-Nano | faster-whisper / Whisper / Parakeet | DashScope / OpenAI 兼容 | 中文工业首选 FunASR 系 |
| LLM | 本地 llama.cpp / Ollama / vLLM | 同左 | OpenAI 兼容 API | 流式 + function call |
| TTS | CosyVoice 3 / sherpa-onnx TTS | Piper / Kokoro / Qwen3-TTS | 豆包 / DashScope | CosyVoice 双向流式 ~150 ms 级 |
| 全双工 | RoboBrain-Audio / FLM-Audio (`cofe-ai/flm-audio`) | HF speech-to-speech | Realtime API | 原生全双工仍早期 |
| 总线 | ROS2 topics `/asr/text` `/tts/say` | WebSocket / Pipeline Stage | MCP tools | 具身推荐 ROS2 解耦 |

详细仓库表见 `references/github-stack.md`。

## 推荐参考栈（按场景）

### A. 离线机器人语音 Agent（ROS2 / Jetson）

- **参考**：`nrl-ai/edgevox`
- **链路**：Silero VAD → faster-whisper → llama.cpp LLM → Kokoro/Piper TTS
- **要点**：barge-in、specsub AEC、ROS2Adapter、唤醒词
- **适用**：隐私优先、无云、Unitree / Franka / MuJoCo 对接

### B. Jetson 最小可跑通

```text
Wake → VAD → Whisper → /asr/text → Ollama → /tts/say → Piper
```

- 桥接节点只做「ASR 文本 → LLM 流式分句 → TTS」
- topic 契约保持薄：`/asr/text`、`/tts/say`、`/interrupt`

### C. 中文具身 / 消费级机器人

- **ASR**：FunASR Paraformer-zh-streaming 或 SenseVoiceSmall
- **TTS**：CosyVoice 3（质量）或 Piper / sherpa-onnx（延迟与体积）
- **参考工程**：`wwbin2017/bailing`（ASR+LLM+TTS 本地对话）、`heyangHEY/HeyAR_ChatBot`（FunASR + 可打断流式 TTS）、`sk-0508/xiaoban-ai`（RISC-V 具身：唤醒→ASR→LLM→TTS→电机）
- **边端一体推理**：`k2-fsa/sherpa-onnx`（ASR/TTS/VAD/KWS 同运行时）

### D. 云端低延迟产品管线

- **参考**：`LiusCraft/orion-x`（Go Pipeline：Silero VAD + 阿里云 ASR/TTS + OpenAI 兼容 LLM + MCP tools）
- **适用**：快速上线、工具调用、长期记忆；注意隐私与断网兜底

### E. 原生全双工（研究 / 预研）

- **参考**：`cofe-ai/flm-audio`（RoboBrain-Audio / FLM-Audio）
- **定位**：边听边说、打断；尚不宜作为唯一生产路径，可与半双工流水线并行评估

### F. 模块化可替换后端

- **参考**：`huggingface/speech-to-speech`
- **链路**：VAD → STT → LLM → TTS，组件可热换；适合做评测床

## 选型决策（简）

1. **必须离线 / 机载** → EdgeVox 模式或 sherpa-onnx 一体；Jetson 用 Whisper + Piper
2. **中文质量优先** → FunASR / SenseVoice + CosyVoice
3. **延迟优先（对话感）** → 全链路流式 + 短句 flush TTS；评估 FLM-Audio
4. **要控本体** → LLM 必须接 tools；ROS2 用独立 action/skill topic，语音节点不做运动学
5. **电机噪声大** → 先 AEC + 能量比门控，再调 VAD；勿只降 ASR 模型

## Agent 执行清单

落地或改栈时按序做：

1. 画清半双工还是目标全双工；写出 topic / API 契约
2. 选定 KWS / VAD / ASR / LLM / TTS 各一主一备（表内挑）
3. 实现 barge-in：用户开口 → 停 TTS → 取消 LLM 生成（≤50 ms 目标）
4. 实现 AEC 或播放能量门控，避免自激
5. LLM tool 与运动栈解耦；语音栈只发意图，运动栈做安全校验
6. 量延迟：VAD / ASR partial / TTFT / TTS first-audio / 端到端 TTFA
7. 噪声场景实测（行走、关节运动、风扇）后再定模型尺寸

## 禁止

- 不要把云厂商私有协议写成唯一路径而不给本地 fallback
- 不要在语音节点内硬编码关节轨迹；经 Agent tools / ROS action
- 不要未验证 AEC 就宣称「可打断」
- 不要凭记忆编造模型名；以 `references/github-stack.md` 与上游 README 为准
