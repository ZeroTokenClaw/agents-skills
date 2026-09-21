---
name: tour-checkin-follow
description: >-
  Use when integrating tour guide + face check-in + person following on Unitree
  G1/Go2 or service robots into one mission. Trigger on 导览签到跟随、迎宾导览、
  签到后跟随、tour check-in follow、展馆一体机业务流程。
---

# 导览 + 人脸签到 + 跟随（一体业务）

编排三个专项 skill，不重复实现细节：

| 能力 | Skill |
| --- | --- |
| 导览 / POI / Nav2 | `embodied-tour-nav` |
| 人脸签到 | `face-checkin-robot` |
| 人员跟随 | `robot-person-follow` |
| 语音 | `embodied-voice-stack` |
| 机型 | `unitree-embodied-skills` |

## 端到端状态机

```text
boot / dock
 → ready                    # 定位 OK，语音待命
 → greet                    # 迎宾话术
 → checkin                  # 人脸签到（站定点）
 → follow_to_gate           # 可选：跟人到展区入口
 → tour_active              # Nav2 多点讲解（跟随默认关闭）
 → follow_assist            # 可选：讲解间隙短时跟人
 → tour_done / checkout
 → dock
```

互斥表：

| 模式 | Nav2 tour | Follow cmd_vel | Checkin cam |
| --- | --- | --- | --- |
| checkin | 暂停 | 关 | 开 |
| follow_to_gate | 关 | 开 | 关或低优先级 |
| tour_active | 开 | **关** | 关 |
| follow_assist | 暂停当前 goal | 开 | 关 |

## 推荐业务流程（展馆）

1. **到位迎宾点**（固定 pose 或充电桩出航）  
2. TTS：「欢迎，请正对镜头签到」  
3. `face-checkin-robot` → 成功得 `person_id`、`name`  
4. TTS：「签到成功。需要我带您去展厅吗？」  
5. 用户说「带我去」→ `robot-person-follow` `start(person_id)` 至 `poi:exhibition_gate`  
6. 到达入口 → `cancel_follow` → `embodied-tour-nav` 启动路线 `tour_id`  
7. 各 POI：讲解；若用户离开可视区，仅提示不自动跟丢重绑  
8. 结束 → 可选送回入口 / 回充  

## Mission 配置示例

```yaml
mission:
  id: museum_am
  robot: go2_01
  steps:
    - type: navigate
      poi: welcome_desk
    - type: checkin
      timeout_s: 60
      on_success: next
      on_fail: retry_or_skip
    - type: ask
      prompt: 需要我带您去展厅吗
      yes: follow_to_gate
      no: start_tour
    - type: follow
      id: follow_to_gate
      target: from_checkin_person
      goal_poi: exhibition_gate
      max_s: 180
    - type: tour
      id: start_tour
      route: hall_a_basic
      follow_during_tour: false
    - type: dock
```

## Topic / 事件总线

| 事件 | 生产者 | 消费者 |
| --- | --- | --- |
| `checkin.succeeded{person_id,name}` | checkin | mission、TTS、follow binder |
| `follow.arrived{goal_poi}` | follow | mission → 启 tour |
| `follow.lost` | follow | TTS；mission 可改纯导览 |
| `tour.poi_arrived` | tour | TTS 讲解 |
| `tour.finished` | tour | mission → dock |
| `voice.intent{follow\|tour\|stop}` | ASR | mission 仲裁 |

仲裁优先级：`estop` > `stop_all` > `checkin` 占用 > `tour`/`follow` 互斥。

## 语音意图映射

| 用户说 | 动作 |
| --- | --- |
| 签到 / 刷脸 | → checkin |
| 跟我走 / 带我去 | → follow（需已签到或当前锁定） |
| 开始讲解 / 导览 | → cancel_follow + tour |
| 停下 / 别跟着 | → cancel_follow；tour 可继续 |
| 下一个 | → tour next POI |

## 失败与降级

| 失败 | 降级 |
| --- | --- |
| 签到超时 | 游客模式导览（无 person_id）或人工二维码 |
| 跟随丢失 | TTS + 在入口等待 / 直接 tour |
| 定位丢失 | 停止运动；禁止 follow 与 tour goal |
| 人流阻塞 | tour 用 Nav2 recoveries；follow 改为 holding |

## Agent 执行清单

1. Read 三个专项 skill，确认 topic 命名一致  
2. 实现 **单一 Mission 节点** 做状态机与 `cmd_vel` 仲裁  
3. 先单测：仅签到 → 仅跟随 → 仅导览，再串起来  
4. 标定签到点 / 入口点 / 路线 YAML  
5. 真机：牵绳验证 follow 限速与 tour 互斥  

## 禁止

- 导览讲解中同时开跟随抢速度（除非明确单主控设计）  
- 未签到用人脸特征做跟随绑定却当已认证  
- 在三个专项里各写一份状态机（只在本 skill / Mission 编排）  
