# GitHub 具身 / 机器人语音技术栈参考

> 检索基准：2026-03。星标数为当时近似值，落地前再查上游 README。

## 端到端机器人 / Agent 框架

| 仓库 | Stars≈ | 技术栈摘要 | 具身相关点 |
| --- | --- | --- | --- |
| [nrl-ai/edgevox](https://github.com/nrl-ai/edgevox) | 16+ | Silero VAD → faster-whisper → llama.cpp(Gemma) → Kokoro/Piper/Supertonic；pymicro-wakeword | ROS2 原生、barge-in、AEC、Unitree G1 / Franka / MuJoCo |
| [huggingface/speech-to-speech](https://github.com/huggingface/speech-to-speech) | — | 可换 VAD/STT/LLM/TTS；Realtime 事件集 | 评测床、本地或远端 LLM |
| [wwbin2017/bailing](https://github.com/wwbin2017/bailing) | 1.7k+ | ASR+LLM+TTS 本地对话；目标亚秒延迟 | 桌面/边端语音 Agent 模板 |
| [LiusCraft/orion-x](https://github.com/LiusCraft/orion-x) | — | Go Pipeline；Silero VAD；DashScope ASR/TTS；GLM；MCP tools | 工具调用 + 记忆，适合产品管线 |
| [heyangHEY/HeyAR_ChatBot](https://github.com/heyangHEY/HeyAR_ChatBot) | — | FunASR/SenseVoice + 流式 LLM + 豆包双向 TTS | 可打断、中文实时对话 |
| [sk-0508/xiaoban-ai](https://github.com/sk-0508/xiaoban-ai) | — | 唤醒→ASR→LLM→TTS→电机；RISC-V SpacemiT | 完整具身演示（语音+动作+表情） |
| [LD-Robots/voice_ros2](https://github.com/LD-Robots/voice_ros2) | — | OpenWakeWord + WebRTC VAD + faster-whisper + Piper + barge-in | ROS2 节点化拆分范例 |
| [AlinaYuhan/SURF2026_VoiceModule](https://github.com/AlinaYuhan/SURF2026_VoiceModule) | — | sherpa-onnx 中文 KWS + openWakeWord + FunASR + ROS2 | Unitree G1 语音模块结构 |
| [cofe-ai/flm-audio](https://github.com/cofe-ai/flm-audio) | 75+ | RoboBrain-Audio / FLM-Audio 原生全双工 | 智源具身语音预研 |

## 基础设施组件

| 仓库 | Stars≈ | 角色 |
| --- | --- | --- |
| [modelscope/FunASR](https://github.com/modelscope/FunASR) | 20k+ | 工业 ASR 工具箱：流式 Paraformer、VAD、标点、说话人 |
| [QwenAudio/SenseVoice](https://github.com/QwenAudio/SenseVoice) | 9k+ | 多语 ASR + 情感 + 事件 |
| [QwenAudio/CosyVoice](https://github.com/QwenAudio/CosyVoice) | 23k+ | 多语 TTS，双向流式，零样本克隆（CosyVoice 3） |
| [k2-fsa/sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) | 14k+ | 边端 ONNX：ASR/TTS/VAD/KWS/说话人，跨平台 |
| [rhasspy/piper](https://github.com/rhasspy/piper) | 11k+ | 轻量本地 TTS，Jetson/ROS 常用 |
| [FireRedTeam/FireRedVAD](https://github.com/FireRedTeam/FireRedVAD) | 500+ | 工业 VAD，对标 Silero/FunASR-VAD |
| [dscripka/openWakeWord](https://github.com/dscripka/openWakeWord) | — | 英文唤醒词 |
| [snakers4/silero-vad](https://github.com/snakers4/silero-vad) | — | 通用 VAD |

## SpacemiT / SDK 专用

| 资源 | 说明 |
| --- | --- |
| [spacemit-robotics/robot-skills@spacemit-robot-speech](https://github.com/spacemit-robotics/robot-skills) | SDK：audio / ASR / VAD / TTS / voiceprint / DOA 构建与 API 路由 |
| skills.sh：`spacemit-robotics/robot-skills@spacemit-robot-speech` | 安装：`npx skills add spacemit-robotics/robot-skills@spacemit-robot-speech` |

## ROS2 Topic 契约（建议最小集）

| Topic | 方向 | 载荷 |
| --- | --- | --- |
| `/asr/text` | pub | 最终或 partial 转写 |
| `/tts/say` | sub | 待播报文本（短句分片） |
| `/interrupt` | sub | 任意消息 → 停播 + 取消生成 |
| `/voice/state` | pub | `listening\|transcribing\|thinking\|speaking\|interrupted` |
| `/agent/tool_call` | pub | JSON：意图 → 运动栈 |

EdgeVox 另暴露 `transcription`、`response`、`metrics`、`tts_request`、`set_language` 等，按需扩展。

## 延迟预算参考

| 段 | 目标量级 |
| --- | --- |
| VAD 帧 | 20–32 ms |
| ASR partial | 100–300 ms |
| LLM TTFT | 模型/硬件相关 |
| TTS first-audio | Piper/Kokoro 边端数百 ms；CosyVoice 流式可至 ~150 ms 级（官方宣称） |
| 端到端 first-audio | EdgeVox 目标亚秒（消费级 GPU） |
| barge-in 停播 | ≤40–50 ms |

## 相关 Agent Skills（skills.sh）

| Skill | 用途 |
| --- | --- |
| `spacemit-robotics/robot-skills@spacemit-robot-speech` | SpacemiT 语音组件 |
| `curiositech/some_claude_skills@voice-audio-engineer` | 通用语音音频工程 |
| `omer-metin/skills-for-antigravity@ros2-robotics` | ROS2 |
| `theneoai/awesome-skills@embodied-ai-researcher` | 具身研究辅助 |
