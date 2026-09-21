# Go2 OpenClaw Skill

[中文](#中文) | [English](#english)

---

## English

Control a **Unitree Go2 robot dog** with natural language through OpenClaw AI.

### Architecture

```
Natural Language → OpenClaw AI → SKILL.md (curl commands)
                                      │
                                HTTP localhost:8520
                                      │
                                FastAPI Gateway
                                      │
                              unitree_sdk2py (CycloneDDS)
                                      │
                                Unitree Go2
                            (WiFi 192.168.123.161)
```

No full ROS2 installation needed — `unitree_sdk2py` communicates directly via CycloneDDS.

### Quick Start

```bash
# 1. Connect to Go2 WiFi hotspot (Unitree_Go2_XXXX)

# 2. Check connection
make check

# 3. Install dependencies
make install

# 4. Start gateway
make run

# 5. Test
curl http://localhost:8520/status
curl -X POST http://localhost:8520/action -H "Content-Type: application/json" -d '{"action":"stand"}'
```

### Install as OpenClaw Skill

Copy `SKILL.md` to your OpenClaw skills directory, then say:

- "让机器狗向前走" → robot walks forward
- "坐下" → robot sits down
- "跳舞" → robot dances
- "停" → emergency stop

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/status` | GET | Full robot status (battery, mode, velocity, IMU) |
| `/battery` | GET | Battery percentage |
| `/move` | POST | Move in direction with speed & duration |
| `/stop` | POST | Emergency stop |
| `/action` | POST | Preset action (stand/sit/dance/backflip/shake_hand/stretch) |

### Safety

- Speed capped at 0.5 m/s (default 0.3)
- Backflip requires battery > 20%
- "停/stop" triggers immediate halt

---

## 中文

通过 OpenClaw AI 用自然语言控制 **Unitree Go2 机器狗**。

### 架构

```
自然语言 → OpenClaw AI → SKILL.md (curl 命令)
                               │
                         HTTP localhost:8520
                               │
                         FastAPI 网关
                               │
                       unitree_sdk2py (CycloneDDS)
                               │
                         Unitree Go2 机器狗
                       (WiFi 192.168.123.161)
```

不需要安装完整 ROS2 — `unitree_sdk2py` 直接通过 CycloneDDS 通信。

### 快速开始

```bash
# 1. 连接 Go2 WiFi 热点 (Unitree_Go2_XXXX)

# 2. 检查连接
make check

# 3. 安装依赖
make install

# 4. 启动网关
make run

# 5. 测试
curl http://localhost:8520/status
curl -X POST http://localhost:8520/action -H "Content-Type: application/json" -d '{"action":"stand"}'
```

### 安装为 OpenClaw Skill

将 `SKILL.md` 复制到 OpenClaw skills 目录，然后对 AI 说：

- "让机器狗向前走" → 机器狗前进
- "坐下" → 机器狗坐下
- "跳舞" → 机器狗跳舞
- "停" → 紧急停止

### 安全限制

- 速度上限 0.5 m/s（默认 0.3）
- 后空翻需要电量 > 20%
- "停" 立即触发急停

## License

MIT
