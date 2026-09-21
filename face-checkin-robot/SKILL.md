---
name: face-checkin-robot
description: >-
  Use when implementing robot face check-in / attendance on Unitree G1/Go2 or
  other service robots: enroll, detect, recognize, debounce, log, TTS feedback.
  Trigger on 人脸签到、刷脸、考勤、迎宾识别、face attendance、face check-in。
---

# 机器人人脸签到

适用于展馆迎宾、办公签到、活动核验。与 `unitree-embodied-skills`、`embodied-voice-stack`、`robot-person-follow`、`tour-checkin-follow` 配合。

签到成功后可选：发布 `checkin.succeeded` → Mission 启动跟随（见 `tour-checkin-follow`）。

## 标准流水线

```text
相机帧
 → 人脸检测 (SCRFD / RetinaFace / YOLO-Face / InsightFace detect)
 → 关键点对齐 + 质量门控 (模糊/侧脸/过小 → 拒绝)
 → 特征提取 (InsightFace / ArcFace ONNX)
 → 与底库比对 (cosine / L2，阈值 τ)
 → 去抖 (同一 person_id 冷却 T 秒)
 → 写签到记录 (本地 DB / 后端 API)
 → TTS 「张三，签到成功」+ 可选屏显
 → 失败：提示重试 / 登记新用户流程
```

## 模块职责

| 模块 | 职责 | 不做 |
| --- | --- | --- |
| `face_detect` | bbox + landmarks | 不判身份 |
| `face_embed` | 512-d 特征 | 不存原图明文（可选项） |
| `face_gallery` | 注册/更新/删除 | 不发运动 |
| `checkin_service` | 阈值、去抖、写库 | 不播 TTS 细节文案以外逻辑 |
| `voice` | `/tts/say` 播报 | 不做识别 |
| `robot_pose` | 到签到点站定 | 不碰人脸库 |

## 数据模型（最小）

```yaml
person:
  id: emp_001
  name: 张三
  embedding: <float32[512]>   # 或多模板 mean
  active: true
checkin_event:
  person_id: emp_001
  ts: 2026-03-21T09:00:00+08:00
  score: 0.82
  camera_id: head_cam
  robot_id: go2_01
  mode: auto | manual_enroll
```

## 关键参数（起点，需现场标定）

| 参数 | 建议起点 | 说明 |
| --- | --- | --- |
| 相似度阈值 τ | 0.35–0.45（cosine 视模型而定） | 过低误识、过高拒识 |
| 最小脸宽 | ≥ 80 px | 远距拒识 |
| 质量分 | blur / pose 门控 | 侧脸 >30° 可拒 |
| 去抖冷却 | 60–300 s | 防重复播报 |
| 推理后端 | ONNX Runtime / TensorRT | 机载优先 |

## 与宇树对接

1. 导航到 `/poi/checkin`（`embodied-tour-nav`）
2. 到位后切 `state=checkin_listening`，开流识别
3. 成功：`/tts/say` + 可选挥手动作（G1 动作库 / Go2 站立保持）
4. 陌生人：TTS 引导扫码或人工登记；**勿自动入库**除非业务允许

## 注册（Enroll）流程

1. 授权告知 → 采集 3–5 张不同微角度
2. 质量过滤 → 多模板或均值 embedding
3. 写入 gallery + 备份
4. 立刻 1:1 自测通过才激活

## 安全与合规

- 人脸特征本地存储；传输 TLS；日志不落原图或仅短时缓存
- 提供删除/导出接口（用户请求）
- 活体：展馆可选简单动作活体或红外；防照片攻击按安保等级选型
- 签到结果不可仅用 YOLO 人物框；必须人脸特征链路

## 推荐开源组件（实现时查最新 README）

| 用途 | 常见选型 |
| --- | --- |
| 检测+识别一体 | InsightFace（buffalo_l / SCRFD+ArcFace） |
| 轻量检测 | YOLO11n-face / YuNet |
| 运行时 | onnxruntime、TensorRT |
| 参考 skill | `face-recognition-system`、`yolo`、`computer-vision-opencv`、`cv-mediapipe` |

## Agent 执行清单

1. 明确：1:N 签到还是 1:1 核验；是否允许现场注册
2. 选定检测+识别模型与机载算力预算
3. 实现 gallery CRUD + 阈值/去抖/审计日志
4. 接线 `/tts/say` 与导览到位事件
5. 用正/负样本集标定 τ 与 FAR/FRR
6. 真机光照（逆光/侧光）回归后再上线

## 禁止

- 用检测框 ID 或 ReID 弱特征替代人脸签到
- 未授权批量采集入库
- 识别线程阻塞 Nav2 / 运控循环（独立节点+队列）
