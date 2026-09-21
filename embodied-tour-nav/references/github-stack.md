# GitHub 导览导航参考

> 检索基准：2026-03。落地前核对上游 README 与 ROS 发行版（Humble/Jazzy）。

## 端到端导览系统

| 仓库 | 技术栈摘要 | 适用 |
| --- | --- | --- |
| [Hyaxon/tour-guide-robot](https://github.com/Hyaxon/tour-guide-robot) | ROS 2 Jazzy、TurtleBot4、Nav2、SLAM Toolbox、AprilTag、自定义 action（对齐/等门/穿门）、YAML landmarks | 室内地图导览教学与行为拆分范例 |
| [hsp-iit/tour-guide-robot](https://github.com/hsp-iit/tour-guide-robot) | R1、YARP+ROS2、Tour Manager、SLAM/导航、语音 Docker（talk） | 综合导览 + HRI |
| [ros-navigation/navigation2](https://github.com/ros-navigation/navigation2) | Nav2：规划、控制、BT、`FollowWaypoints`、`NavigateToPose` | 导航底座（必选依赖认知） |

## Nav2 关键接口

| Action | 用途 |
| --- | --- |
| `navigate_to_pose` (`NavigateToPose`) | 单 POI |
| `follow_waypoints` (`FollowWaypoints`) | 多点序列；feedback：`current_waypoint`；result：`missed_waypoints` |

导览若需「每点讲解/对齐」，常见做法：

1. Mission 循环：`NavigateToPose` → 行为 → TTS → 下一点
2. 或 Waypoint + 自定义 task executor（到达回调里跑讲解）

## 建图 / 定位

| 组件 | 角色 |
| --- | --- |
| SLAM Toolbox | 建图与定位切换 |
| AMCL | 经典粒子滤波定位（视栈而定） |
| AprilTag / apriltag_ros | POI 确认与朝向对齐 |
| TF2 | `map`→`odom`→`base_link`→传感器 |

## 与语音 / 具身栈

| Skill / 仓库 | 关系 |
| --- | --- |
| `embodied-voice-stack` | `/asr/text`、`/tts/say`、barge-in |
| `nrl-ai/edgevox` | 语音 ROS2Adapter，可挂到 tour topics |
| skills.sh `miuav/vibe-coding-ros2@nav2-*` | Nav2 配置类 skill |
| skills.sh `robotics-playground/skills@nav-slam` | SLAM/导航 |
| skills.sh `isaac-sim/isaacsim@isaac-sim-robot-navigation` | Isaac Sim 导航 |

## Tour Mission 状态建议

```text
idle
 → navigating     # Nav2 goal active
 → arrived        # pose/tag OK
 → narrating      # TTS playing
 → paused         # 人工/语音暂停
 → recovering     # Nav2 recoveries / 重定位
 → error
 → docking/home
```

仲裁优先级：`estop` > `cancel_nav` > `interrupt_tts` > `skip_poi` > 正常推进。
