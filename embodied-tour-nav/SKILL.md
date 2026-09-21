---
name: embodied-tour-nav
description: >-
  Use when designing or implementing embodied tour-guide robots: map/SLAM,
  Nav2 waypoint tours, POI narration, door/crowd behaviors, and coupling
  navigation with voice (ASR/TTS). Trigger on 导览、导航、巡游、Nav2、
  FollowWaypoints、展馆导览、园区机器人、tour-guide robot、POI。
---

# 具身导览导航

## 何时使用

- 展馆 / 园区 / 商场导览机器人：多点巡游 + 定点讲解
- Nav2 建图定位、waypoint 任务、到达后行为（对齐、等待、穿门）
- 将导航意图与 `embodied-voice-stack` 语音链路解耦对接
- 查阅导览导航相关 GitHub 参考实现

配套 skill：`embodied-voice-stack`（语音）；`face-checkin-robot`（签到）；`robot-person-follow`（跟随）；一体编排 `tour-checkin-follow`；宇树总路由 `unitree-embodied-skills`。本 skill 只管 **地图 → 导航 → POI 任务编排**；跟人时须释放 `cmd_vel` 给跟随或由 Mission 仲裁。

## 标准流水线

```text
地图 (SLAM / 先验 map)
 → 定位 (AMCL / slam_toolbox localization)
 → 导览任务机 (Tour Mission)
 → Nav2 (NavigateToPose / FollowWaypoints)
 → 到达 POI
 → 对齐 / 确认 (AprilTag / 视觉 / 位姿阈值)
 → 讲解 (TTS via /tts/say) + 可选问答 (ASR)
 → 下一 POI 或回充 / 待命
 ↔ 安全：急停 > 取消导航 > 语音打断讲解
```

## 分层职责

| 层 | 职责 | 不做什么 |
| --- | --- | --- |
| 感知定位 | LiDAR/视觉、TF、`map`→`odom`→`base` | 不讲内容 |
| Nav2 | 全局/局部规划、避障、恢复行为 | 不编排展项文案 |
| Tour Mission | POI 序列、到达条件、失败重试、跳过 | 不直接发 `cmd_vel` |
| 行为插件 | 对齐标签、等门开、穿门、人群等待 | 不替代 Nav2 规划 |
| 讲解 Agent | TTS 文案、多轮问答、切展项 | 不改规划器参数 |

## POI 数据模型（最小）

```yaml
pois:
  - id: hall_a_01
    name: 入口大厅
    pose: { frame_id: map, x: 1.2, y: 3.4, yaw: 1.57 }
    arrival: { type: pose_tolerance, xy: 0.35, yaw: 0.4 }  # 或 apriltag_id
    narrate:
      script_id: hall_a_01_zh
      wait_ms: 0          # 到位后再讲；可边走边预告
      barge_in: true
    next: [hall_a_02]
    on_fail: skip         # skip | retry | abort_tour
```

Mission 只消费该配置；地图坐标系与 `frame_id` 必须一致。

## Nav2 集成要点

1. **单点**：`NavigateToPose`；**巡游**：`FollowWaypoints`（`nav2_msgs/action/FollowWaypoints`）
2. 导览通常要「点到点 + 点上任务」，优先 **自管循环调用 NavigateToPose**，或 Waypoint + `task_executor`；不要假设 FollowWaypoints 自带讲解
3. 取消：`cancel_goal` 与语音 `/interrupt` 分开——取消导航 ≠ 停 TTS，需 Tour Mission 统一仲裁
4. 恢复行为（backup/spin/wait）对客流场景调参；展厅狭窄处提高代价地图膨胀并限制最大速度
5. 初始位姿：人工 RViz 设姿或二维码/充电桩对接位姿；未定位禁止发 goal

## 与语音栈契约

| Topic / 接口 | 方向 | 含义 |
| --- | --- | --- |
| `/tour/poi_arrived` | mission→ | `{poi_id}` 到位，可开讲 |
| `/tts/say` | mission→voice | 讲解文本分片 |
| `/asr/text` | voice→mission | 访客打断/提问 |
| `/tour/command` | voice→mission | `goto poi_id` / `next` / `pause` / `home` |
| `/interrupt` | 双向 | 停讲解；是否停导航由 mission 策略决定 |
| `/tour/state` | mission→ | `idle\|navigating\|arrived\|narrating\|paused\|error` |

原则：语音节点 **只发意图**；运动与路径由 Tour Mission + Nav2 执行。

## 推荐参考栈

| 场景 | 参考 | 要点 |
| --- | --- | --- |
| 教学级室内导览 | `Hyaxon/tour-guide-robot` | TurtleBot4 + Nav2 + AprilTag 对齐 + 穿门行为 + YAML landmarks |
| 人形/综合导览 | `hsp-iit/tour-guide-robot` | Tour Manager + SLAM/导航 + 语音 Docker 拆分 |
| 导航底座 | `ros-navigation/navigation2` | NavigateToPose / FollowWaypoints / BT |
| 建图 | SLAM Toolbox | 先验 map + 定位模式跑导览 |
| 语音对接 | `embodied-voice-stack` | `/asr/text` `/tts/say` barge-in |

详细仓库表见 `references/github-stack.md`。

## Agent 执行清单

1. 确认 map 与 TF 树；定位稳定后再接 mission
2. 用 YAML/DB 定义 POI；禁止硬编码坐标散落在多处
3. 实现状态机：`idle → navigating → arrived → narrating → next`
4. 到达判定：位姿容差 **或** 视觉标签；二者选一作主条件
5. 接线语音：到位发 `/tour/poi_arrived`，讲解走 `/tts/say`
6. 定义取消策略：访客说「停下」→ 停 TTS + 取消 Nav2 goal
7. 失败策略：超时 / 阻塞 / 丢定位 → `skip|retry|abort` 可配置
8. 仿真（Gazebo）跑通全路径后再上真机；真机先限速 + 急停验证

## 禁止

- 在语音节点里直接 `cmd_vel` 或改 Nav2 内部状态
- 无 map / 未定位时发导览 goal
- 讲解阻塞导航线程（TTS 必须异步；mission 用事件驱动）
- 把展项文案写死进 Nav2 BT XML（文案属内容层）
- 未处理人群阻塞就宣称「可商用导览」
