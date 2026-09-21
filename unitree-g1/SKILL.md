---
name: unitree-g1
description: 'Unitree G1 bipedal humanoid: variants and DOF counts, joint index map, DDS topics and LowCmd fields, LocoClient and MotionSwitcher APIs, safety rules, and common mistakes. Use whenever working with a Unitree G1 (the bipedal humanoid): its SDK code, joint control, specs, or troubleshooting. For the wheeled dual-arm G1D, use the unitree-g1d skill instead.'
---

# Unitree G1 (bipedal humanoid)

## Identity: which G1 is this?

| Variant | Body DOF | Notes |
| --- | --- | --- |
| G1 (base) | 23 | 1 waist DOF, 5-DOF arms, no dexterous hands |
| G1-EDU | 23 to 43 | Optional: +2 waist DOF, +2 wrist DOF per arm, Dex3-1 7-DOF hands |

The often-cited "29-DOF G1" is an EDU configuration: base 23 + 2 waist + 2 wrist per arm. Never assume the DOF count: read it from the robot (`LowState_.mode_machine`).

- `mode_machine` identifies the variant; a mismatched value makes commands silently rejected. The support site documents legacy values 1 = 23-DOF, 2 = 29-DOF, 9 = 14-DOF upper body (9 is current as `g1_dual_arm`), while the up-to-date model files in unitree_ros use ids 4/5/6/10-18. Read `LowState_.mode_machine` from the robot and match it; never hard-code.
- Hardware quick facts: about 1320 mm tall, about 35 kg with battery, 9000 mAh quick-release battery (about 2 h), Intel RealSense D435i + Livox MID360, knee torque 90 N.m base / 120 N.m EDU.
- Onboard: motion MCU/PC 192.168.123.161 (closed, not developer-accessible), EDU dev PC is a Jetson Orin NX at 192.168.123.164 (default login `unitree` / `123`).

## Joint index map

`unitree_hg::msg::dds_::LowCmd_.motor_cmd` (35 slots, body joints at 0-28):

| Indices | Region |
| --- | --- |
| 0-5 | Left leg: hip pitch, hip roll, hip yaw, knee, ankle pitch, ankle roll |
| 6-11 | Right leg: same order |
| 12-14 | Waist: yaw (12), roll (13), pitch (14); the 23-DOF variant only has 12 |
| 15-21 | Left arm: shoulder pitch/roll/yaw, elbow, wrist roll (+ wrist pitch, wrist yaw on 29-DOF) |
| 22-28 | Right arm: same order as the left |

Traps: the left arm starts at 15, not 12. On 23-DOF, slots 13, 14, 20, 21, 27, 28 are empty. Ankle names swap with `mode_pr` (0: ankle pitch/roll, 1: ankle A/B).

Full per-variant tables, joint limits, and the Dex3-1 hand motor order: [JOINTS.md](JOINTS.md).

## Low-level DDS interface

| Topic | Type | Purpose |
| --- | --- | --- |
| `rt/lowcmd` | `LowCmd_` | Motor commands, all body joints |
| `rt/lowstate` | `LowState_` | Full state, IMU, wireless remote |
| `rt/arm_sdk` | `LowCmd_` | Arm + waist while sport mode is active; `motor_cmd[29].q` is a 0-1 blend weight |
| `rt/user_lowcmd` | `LowCmd_` | User control in SwitchToUserCtrl mode |
| `rt/dex3/left/cmd`, `rt/dex3/right/cmd` | `HandCmd_` | Dex3-1 hand commands |
| `rt/dex3/left/state`, `rt/dex3/right/state` | `HandState_` | Dex3-1 hand state |
| `rt/secondary_imu` | `IMUState_` | Torso IMU |

MotorCmd fields: `mode` (0 disabled, 1 enabled), `q`, `dq`, `tau`, `kp`, `kd`. Control law: `tau = kp*(q - q_meas) + kd*(dq - dq_meas) + tau_ff`. The control loop runs at 500 Hz (2 ms), not 1 kHz. Every `LowCmd_` must carry a valid CRC32 (polynomial 0x04c11db7, computed over the message minus the crc field).

## High-level: LocoClient, not Go2 SportClient

G1 high-level motion is `unitree::robot::g1::LocoClient`, service name `sport`, API IDs 7001-7111. Convenience methods: `Damp()` (FSM 1), `Squat()` (2), `Sit()` (3), `StandUp()` (4), `ZeroTorque()` (0), `Start()` (FSM 500), `Move(vx, vy, vyaw)`, `StopMove()`, `HighStand()`, `LowStand()`, `BalanceStand()`, `ContinuousGait(flag)`, `WaveHand`, `ShakeHand` (via SetTaskId).

Caveat: the SDK source maps `Start()` to FSM 500, while the NVIDIA Isaac ROS G1 bridge docs report firmware 1.5.x uses 200. Treat the Start FSM ID as firmware-dependent: query `GetFsmId` on the target robot instead of hard-coding.

Go2's `SportClient` API IDs (1001+) do not exist on G1.

## MotionSwitcher: release before low-level control

Before publishing `rt/lowcmd`, stop the internal motion service: `MotionSwitcherClient::ReleaseMode()`, then check the returned name is empty. Never send `rt/lowcmd` and sport/LocoClient commands at the same time (conflicts and jitter). For SDK work, put the robot in debug mode: L2 + R2 per the quick-start and manual (L2 + A is the diagnostic/position-mode confirmation, not debug mode; button maps are firmware-dependent). Debug mode disables `ai_sport`, so high-level RPC calls like `Move` stop working until you re-enable or reboot.

## Safety

- No physical e-stop button exists. Damping entry on unexpected state: L2 + B on firmware 1.0.4 (older firmware: L1 + A). Button maps are firmware-dependent.
- Damp first, then power off.
- Arms straight down at power-on.
- The SDK's termination-check example uses these thresholds: 1.0 rad tilt, 10 rad/s joint velocity, 6 rad/s base angular velocity, 120 C winding / 85 C casing, 20% battery, 1000 ms link loss.
- `rt/arm_sdk` commands require `StandUp()` (which requires `Damp()` first).

## Common mistakes

| Wrong | Right |
| --- | --- |
| "G1 is 29-DOF" | Base is 23-DOF; EDU is 23-43; read `mode_machine` |
| Left arm starts at index 12 | Left arm is 15-21 |
| Go2 `SportClient` on G1 | `LocoClient`, service `sport`, IDs 7001+ |
| 1 kHz control loop | 500 Hz |
| Missing crc on LowCmd | CRC32 on every message |
| `rt/lowcmd` while the sport service is active | `ReleaseMode()` first |
| One "G1 URDF" for all units | Match the variant to `mode_machine` (see JOINTS.md) |
| Hard-coded Start FSM ID | 500 in SDK source, firmware-dependent in practice; query the robot |
| H1/H2 motor counts for G1 | G1 body array is 29 slots (0-28); H1/H2 differ |

## Pointers

Fetch these when facts may have drifted (firmware behavior, limits, releases, downloads) rather than trusting cached values:

| Link | For |
| --- | --- |
| [about_G1](https://support.unitree.com/home/en/G1_developer/about_G1) | Identity, specs, joint limits |
| [joint_motor_sequence](https://support.unitree.com/home/en/G1_developer/joint_motor_sequence) | Canonical joint tables, Dex3-1 hand order |
| [sdk_overview](https://support.unitree.com/home/en/G1_developer/sdk_overview) | SDK scope and middleware |
| [basic_motion_development](https://support.unitree.com/home/en/G1_developer/basic_motion_development) | Debug mode, release rule, command-conflict warnings |
| [motion_witcher_service_interface](https://support.unitree.com/home/en/G1_developer/motion_witcher_service_interface) | MotionSwitcherClient API and error codes |
| [ros2_communication_routine](https://support.unitree.com/home/en/G1_developer/ros2_communication_routine) | Network and CycloneDDS setup |
| [G1 FAQ](https://support.unitree.com/home/en/G1_developer/FAQ) | Firmware notes, factory images, recalibration |
| [unitree_sdk2](https://github.com/unitreerobotics/unitree_sdk2) / [example/g1](https://github.com/unitreerobotics/unitree_sdk2/tree/main/example/g1) | C++ SDK and G1 examples (loco_client, arm5/arm7, ankle_swing, dual_arm, dex3, audio) |
| [unitree_sdk2_python](https://github.com/unitreerobotics/unitree_sdk2_python) | Python bindings |
| [unitree_ros2](https://github.com/unitreerobotics/unitree_ros2) | ROS2 packages and G1 examples |
| [g1_description](https://github.com/unitreerobotics/unitree_ros/tree/master/robots/g1_description) | URDF/MJCF variants |
| [G1 user manual (MYBOTSHOP)](https://www.docs.mybotshop.de/downloads/G1_User_Manual.pdf) | Operations, safety, button maps |
| [NVIDIA Isaac ROS G1 bridge](https://nvidia-isaac-ros.github.io/repositories_and_packages/isaac_ros_robots/unitree_g1_bridge/index.html) | Third-party bridge; source of the FSM 200 report |

Firmware behavior, factory images, torque recipes, and pricing drift: fetch the pages above rather than hard-coding.
