---
name: go2-robot-control
description: Control Unitree Go2 robot dog — move, stop, actions (stand/sit/dance/backflip), check status and battery
version: 1.0.0
author: dongsheng123132
triggers:
  - 机器狗
  - robot dog
  - Go2
  - walk
  - 向前走
  - 坐下
  - 跳舞
  - 站起来
  - 后空翻
  - 停
  - stop the dog
  - dog status
  - battery
---

# Go2 Robot Dog Control

You can control a Unitree Go2 robot dog through a local HTTP gateway running at `http://localhost:8520`.

## Safety Rules (MUST follow)

1. **Default speed is 0.3 m/s** — never exceed 0.5 m/s unless user explicitly says "full speed"
2. **Before backflip**: always check battery > 20% by calling `/battery` first
3. **"停" or "stop"** → immediately call `/stop`, no confirmation needed
4. **Duration**: default 1 second per movement, max 10 seconds
5. **Always call /stop if anything seems wrong**

## Available Commands

### Check Status
```bash
curl -s http://localhost:8520/status
```
Returns: battery, mode, velocity, position, IMU data, connection status.

### Check Battery
```bash
curl -s http://localhost:8520/battery
```
Returns: `{"battery": 85}`

### Move
```bash
curl -s -X POST http://localhost:8520/move \
  -H "Content-Type: application/json" \
  -d '{"direction": "forward", "speed": 0.3, "duration": 1.0}'
```
Directions: `forward`, `backward`, `left`, `right`, `turn_left`, `turn_right`

### Emergency Stop
```bash
curl -s -X POST http://localhost:8520/stop
```

### Preset Actions
```bash
curl -s -X POST http://localhost:8520/action \
  -H "Content-Type: application/json" \
  -d '{"action": "stand"}'
```
Actions: `stand`, `sit`, `dance`, `backflip`, `shake_hand`, `stretch`

## Natural Language Mapping

| User says | Action |
|-----------|--------|
| 向前走 / walk forward / go forward | POST /move `{"direction":"forward","speed":0.3,"duration":1.0}` |
| 后退 / go back | POST /move `{"direction":"backward","speed":0.3,"duration":1.0}` |
| 左转 / turn left | POST /move `{"direction":"turn_left","speed":0.3,"duration":1.0}` |
| 右转 / turn right | POST /move `{"direction":"turn_right","speed":0.3,"duration":1.0}` |
| 快点走 / walk faster | POST /move `{"direction":"forward","speed":0.5,"duration":1.0}` |
| 走远一点 / walk further | POST /move `{"direction":"forward","speed":0.3,"duration":3.0}` |
| 停 / stop | POST /stop |
| 坐下 / sit | POST /action `{"action":"sit"}` |
| 站起来 / stand up | POST /action `{"action":"stand"}` |
| 跳舞 / dance | POST /action `{"action":"dance"}` |
| 后空翻 / backflip | Check /battery first, then POST /action `{"action":"backflip"}` |
| 握手 / shake hand | POST /action `{"action":"shake_hand"}` |
| 伸懒腰 / stretch | POST /action `{"action":"stretch"}` |
| 电量 / battery | GET /battery |
| 状态 / status | GET /status |

## Error Handling

- If gateway returns connection error → tell user "网关未启动，请先运行 make run"
- If robot shows connected=false → tell user "机器狗未连接，请检查 WiFi 连接"
- If backflip blocked by low battery → tell user the current battery level and that >20% is needed
