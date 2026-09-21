---
name: unitree-embodied-skills
description: >-
  Use when developing Unitree G1 humanoid or Go2 quadruped: voice, Nav2 tour,
  vision/YOLO, video, motion, face check-in, person following, integrated
  tour+checkin+follow missions. Routes to installed skills and local pipelines.
  Trigger on 宇树、Unitree、G1、Go2、机器狗、人形、人脸签到、跟随、导览、
  YOLO、语音导航、视觉感知。
---

# 宇树 G1 / Go2 具身能力路由

先读本 skill，再打开对应专项。自建配套：`embodied-voice-stack`、`embodied-tour-nav`、`face-checkin-robot`、`robot-person-follow`；**一体编排**用 `tour-checkin-follow`。

## 平台与 SDK

| 机型 | 优先 skill | 说明 |
| --- | --- | --- |
| Go2 机器狗 | `unitree-go2-sdk-skill`、`go2-robot-control` | SDK / 运控入口 |
| G1 人形 | `unitree-g1`、`unitree-g1-dev-copilot` | 开发辅助 |
| 多机型通用 | `unitree-robot`、`unitree-robots`、`unitree-docs` | Go1/Go2/G1/H1 控制与文档 |
| ROS2 底座 | `ros2-robotics`、`nav2-integration` | 导航/话题集成 |

## 能力分层（推荐架构）

```text
相机/麦/雷达
    ↓
感知层: YOLO / 人脸 / VAD·ASR        ← 小模型边端
    ↓
任务层: Tour Mission / 签到 / 跟随
    ↓
语音层: TTS 讲解 + 问答              ← embodied-voice-stack
    ↓
运动层: Nav2 / 步态 / 手臂动作       ← Go2 运控 or G1 motion
    ↓
安全: 急停 > 取消导航 > 停 TTS > 跳过 POI
```

**原则：** 感知与运动解耦；语音只发意图 topic；运动栈做安全校验。

## 语音 + 导航 + 导览

| 任务 | Skill |
| --- | --- |
| ASR/TTS/打断 | `embodied-voice-stack` |
| 多点导览 / POI | `embodied-tour-nav` |
| SLAM / 激光建图 | `nav-slam`、`laser-slam`、`occupancy-map` |
| Nav2 | `nav2-integration` |

典型 topic：`/asr/text`、`/tts/say`、`/tour/command`、`/tour/poi_arrived`、`/interrupt`。

## 视觉 / 视频 / 小模型

| 任务 | 优先 | 备选 |
| --- | --- | --- |
| YOLO 检测/分割/姿态 | `yolo` | `yolo-models`、`yolo-pipeline`、`yolo-integration` |
| 训 YOLO / 数据集 | `yolo-training`、`yolo-datasets` | — |
| OpenCV 管线 | `computer-vision-opencv`、`opencv` | `ffmpeg-opencv-integration` |
| 大位移光流 / 点跟踪 | **`megaflow`** | `opencv/video-analysis` |
| 通用 CV 流水线 | `computer-vision-pipeline` | `senior-computer-vision` |
| 边端视觉 SDK | `spacemit-robot-vision` | — |
| 视频采集/处理 | `python-video-pipeline` | `ffmpeg-opencv-integration` |
| 姿态/关键点 | `cv-mediapipe` | YOLO-Pose（经 `yolo`） |
| 动作识别训练 | `tao-train-action-recognition` | — |

**边端建议：** Go2/G1 机载优先 YOLO11n/s 或导出 TensorRT/ONNX；ROS2 用 `yolo-integration` 发 `Detection2DArray`。

## 人脸签到

| 任务 | Skill |
| --- | --- |
| 机器人人脸签到全流程 | **`face-checkin-robot`** |
| 人脸系统参考 | `face-recognition-system` |

## 人员跟随

| 任务 | Skill |
| --- | --- |
| 视觉跟人 / 丢失恢复 | **`robot-person-follow`** |
| 检测跟踪底座 | `yolo`、`yolo-integration`、`multi-object-tracking` |

## 导览 + 签到 + 跟随（一体）

| 任务 | Skill |
| --- | --- |
| 展馆迎宾→签到→跟人→导览编排 | **`tour-checkin-follow`** |

流程摘要见该 skill 状态机；禁止三模块各自抢 `cmd_vel`。

## 动作 / 运动

| 任务 | 优先 | 备选 |
| --- | --- | --- |
| ROS2 运动控制 | `motion-control` | `unitree-robot`、`go2-robot-control` |
| 运动扩散/生成 | `kimodo-motion-diffusion` | — |
| 导览到达后行为 | `embodied-tour-nav`（对齐/等待） | AprilTag / 人脸朝向 |

G1：语音触发手势/鞠躬等走动作库或 SDK API，勿在 ASR 回调里直接写关节角。  
Go2：速度指令与 Nav2 `cmd_vel` 二选一主控，避免双写。

## 场景配方

### A. 展馆导览（G1 或 Go2）

`unitree-*` + `nav-slam` + `embodied-tour-nav` + `embodied-voice-stack` +（可选）`yolo` 人流避让

### B. 迎宾 + 人脸签到

`face-checkin-robot` + `embodied-voice-stack` + `unitree-robot`（到位点站定）+ 摄像头 `python-video-pipeline`

### C. 视觉跟随

`robot-person-follow` + `yolo` / `multi-object-tracking` + `motion-control`

### D. 导览 + 签到 + 跟随（完整业务）

**`tour-checkin-follow`**（内部调用 tour / checkin / follow 三专项）

### E. 巡检录像

`python-video-pipeline` + `ffmpeg-opencv-integration` + waypoint 巡游

## Agent 执行清单

1. 确认机型（G1 vs Go2）与 SDK/ROS2 发行版
2. 按场景选配方；Read 对应 skill，勿凭记忆编造 Unitree API
3. 感知结果进 topic/服务，不直连 `cmd_vel`
4. 边端模型先选 nano 级，再量延迟与功耗
5. 人脸数据合规：本地库、脱敏日志、授权告知
6. 真机前仿真或牵绳限速；急停可触达

## 禁止

- 在语音节点内硬编码步态/关节
- 未定位发导览 goal
- 云端人脸 API 作为唯一路径且无断网兜底（展馆常无网）
- 把 YOLO 置信度当身份认证（签到必须用人脸特征/ID 库）
