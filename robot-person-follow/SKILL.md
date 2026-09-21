---
name: robot-person-follow
description: >-
  Use when implementing person-following on Unitree Go2/G1 or service robots:
  select target, track, maintain distance, lose/reacquire, handoff with Nav2
  tour and face check-in. Trigger on 跟随、跟人、视觉跟随、person follow、
  human following、跟谁走。
---

# 机器人人员跟随

适用于迎宾带路、导览中跟人、签到后人跟随入场。配套：`yolo`、`yolo-integration`、`multi-object-tracking`、`megaflow`、`motion-control`、`unitree-embodied-skills`。

## 标准流水线

```text
选目标 (语音「跟我」/ 人脸锁定 / 举手 / 最近人体)
 → 检测 YOLO person (+ 可选 ReID / 人脸绑定)
 → 多目标跟踪 (ByteTrack / BotSORT / DeepSORT)
 → 估计相对位姿 (bbox 中心 + 深度/单目尺度 / 激光投影)
 → 跟随控制器 (保持距离 d*、朝向、限速)
 → 丢失恢复 (搜索旋转 / 短时记忆 / 放弃回待命)
 ↔ 与 Nav2：跟随期间暂停 waypoint；恢复导览时取消 follow
```

## 选目标策略

| 模式 | 触发 | 绑定键 |
| --- | --- | --- |
| 语音点名 | 「跟我走」且面前 1 人 | 当前最大人脸/人体 |
| 人脸绑定 | 签到成功 `person_id` | gallery id + ReID |
| 手势 | 举手 / 招手 | 短时 track_id |
| 显式选择 | 屏点选 / 工牌码 | track_id |

**规则：** 绑定后只跟 `target_id`；其他人进入画面不切换，除非超时丢失并重新授权。

## 控制参数（起点）

| 参数 | 建议 | 说明 |
| --- | --- | --- |
| 期望距离 d* | 1.2–1.8 m（Go2）；1.0–1.5 m（G1） | 过近碰撞、过远丢跟 |
| 死区 | ±0.2 m | 防振荡 |
| 最大线速度 | Go2 ≤ 0.8–1.2 m/s 室内 | 人流场景再降 |
| 最大角速度 | 0.8–1.2 rad/s | — |
| 丢失超时 | 2–4 s | 超则 `searching` |
| 搜索超时 | 8–15 s | 超则 `lost` → 待命 |

## 相对位姿估计

优先序：

1. RGB-D / 立体深度 + bbox 中心  
2. LiDAR 扇区投影（人体框水平角）  
3. 单目：bbox 高度先验（成人身高假设，误差大，仅辅助）

输出：`target_pose` in `base_link` 或 `odom`（x,y,yaw）。

## 状态机

```text
idle
 → locking          # 选目标 / 人脸确认
 → following        # 正常跟人
 → holding          # 目标过近或语音暂停
 → searching        # 短暂丢失
 → lost             # 放弃；TTS 提示
 → handoff_nav      # 交回导览 Nav2
```

仲裁：`estop` > `cancel_follow` > `tour_active` 互斥 > 跟随。

## 与导览 / 签到交接

| 来源事件 | 动作 |
| --- | --- |
| 签到成功 | 可选 `start_follow(person_id)` 带至展区入口 |
| 「开始导览」 | `cancel_follow` → Tour Mission 接管 |
| POI 讲解中 | 默认禁止跟随抢 `cmd_vel`；可「边跟边讲」需单主控 |
| 「别跟着了」 | `cancel_follow` → idle |

## Topic 契约（建议）

| Topic | 方向 | 含义 |
| --- | --- | --- |
| `/follow/command` | sub | `{action: start\|stop\|pause, person_id?, track_id?}` |
| `/follow/state` | pub | `idle\|locking\|following\|searching\|lost` |
| `/follow/target` | pub | `{track_id, person_id?, x, y, score}` |
| `/cmd_vel` | pub | **仅 follow 激活且 tour 未占用时** |
| `/tts/say` | pub | 「好的，我跟着您」/「跟丢了」 |

## 模块职责

| 模块 | 做 | 不做 |
| --- | --- | --- |
| detector | YOLO person | 不发速度 |
| tracker | 稳定 track_id | 不选业务目标 |
| binder | person_id ↔ track | 不规划路径 |
| follow_ctrl | PID/MPC → twist | 不改地图 |
| safety | 激光急停膨胀 | — |

## 安全

- 跟随与 Nav2 **互斥写** `cmd_vel`（mutex / 主控仲裁节点）
- 前方障碍：局部避障或停住喊话，禁止硬闯
- 下楼梯/玻璃门：禁跟随或限速 + 人工确认
- 隐私：不录制跟随全程人脸视频除非业务授权

## 推荐组件

| 层 | 选型 |
| --- | --- |
| 检测 | YOLO11n-person（`yolo` / `yolo-integration`） |
| 跟踪 | ByteTrack / BotSORT（`multi-object-tracking`） |
| 深度 | RealSense / 机载 RGB-D |
| 运控 | `motion-control` / `unitree-robot` / `go2-robot-control` |

## Agent 执行清单

1. 定选目标策略与丢失策略  
2. 实现检测→跟踪→位姿→控制闭环，单独节点  
3. 与 Tour Mission 做 `cmd_vel` 仲裁  
4. 签到成功可选自动 `start_follow`  
5. 人流密集场实测 FAR（跟错人）与丢失率  

## 禁止

- 多节点同时发 `cmd_vel`  
- 无 track 绑定仅跟「画面最大人」（易跟错）  
- 把跟随当导航全局规划替代（长距离回 Nav2）  
