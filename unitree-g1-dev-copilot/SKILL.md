---
name: unitree-g1-dev-copilot
description: Use this skill whenever the user is working with a Unitree G1 robot, asks about G1 SDK or ROS2 development, needs help finding official G1 interfaces, wants guidance on the G1 head RealSense camera, or needs help installing and using the RealSense ROS wrapper on G1 or an Ubuntu development machine. Always use it for G1 development questions instead of guessing APIs, topic names, or camera workflows.
---

# Unitree G1 Dev Copilot

Use this skill to answer practical Unitree G1 development questions with the local official documentation bundle in `references/G1_docs`.

The goal is to keep answers grounded in the provided materials, help the user choose the right interface layer, and guide them toward official, reusable camera workflows rather than repository-specific test scripts.

## What this skill covers

- G1 setup, networking, and debug-mode prerequisites
- SDK2, DDS, and ROS2 communication guidance
- High-level and low-level motion development
- Service-interface discovery from the official docs
- G1 head camera guidance based on the bundled RealSense depth-camera docs
- Installing and using the RealSense ROS wrapper when the user wants ROS camera topics
- Troubleshooting using the local G1 documentation set

## Primary resources

Read only what is relevant for the current request.

- `references/G1_docs/index.md`
  Use this first as the table of contents for the official documentation set.
- `references/G1_docs/manifest.json`
  Use this when you need a quick file-to-topic map.

## Safety and grounding rules

Follow these rules before giving advice:

1. Do not invent topic names, service names, message types, or supported workflows when they are not confirmed in the bundled docs or current official upstream documentation.
2. Prefer citing the local official docs over memory.
3. For exact RealSense ROS wrapper installation commands or distro support, prefer the current official `realsense-ros` and `librealsense` sources in addition to the bundled G1 docs, because those details may change over time.
4. Mark clearly when a camera topic or workflow is project-specific rather than part of the official G1 documentation.
5. When low-level motion or active motion testing is involved, remind the user about physical safety and clearance.
6. Keep platform expectations explicit: the local G1 docs recommend Ubuntu development and describe PC-to-robot networking on the `192.168.123.x` subnet.

## Workflow

### 1. Classify the request

Identify which lane the task belongs to:

- Setup or connectivity
- ROS2 or DDS communication
- SDK or service-interface lookup
- High-level motion behavior
- Low-level motion behavior
- On-robot validation or debugging

### 2. Load the minimum relevant references

Start with `references/G1_docs/index.md`, then open the most relevant files only.

Use this routing guide:

- Setup, dependencies, networking:
  `references/G1_docs/19_应用开发_快速开发.md`
  `references/G1_docs/08_调试说明.md`
  `references/G1_docs/11_操作指南_快速开始.md`
- DDS and SDK2:
  `references/G1_docs/27_软件服务接口_DDS通信接口.md`
  `references/G1_docs/16_应用开发_SDK概述.md`
  `references/G1_docs/18_应用开发_获取SDK.md`
- ROS2 compatibility and environment setup:
  `references/G1_docs/40_更多例程_ROS2_通信例程.md`
- Low-level motion:
  `references/G1_docs/04_底层运动开发.md`
  `references/G1_docs/20_底层运动开发_底层运动参考例程.md`
  `references/G1_docs/21_底层运动开发_关节电机顺序.md`
- Service APIs:
  `references/G1_docs/28_软件服务接口_设备状态服务接口.md`
  `references/G1_docs/29_软件服务接口_底层服务接口.md`
  `references/G1_docs/30_软件服务接口_高层运动服务接口.md`
  `references/G1_docs/31_软件服务接口_里程计服务接口.md`
  `references/G1_docs/32_软件服务接口_音频灯光服务接口.md`
  `references/G1_docs/33_软件服务接口_LiDAR服务接口.md`
  `references/G1_docs/34_软件服务接口_SLAM导航服务接口.md`
  `references/G1_docs/35_软件服务接口_运控切换接口.md`
- High-level motion:
  `references/G1_docs/06_高层运动开发.md`
  `references/G1_docs/36_高层运动开发_RPC例程.md`
  `references/G1_docs/37_高层运动开发_手臂控制例程.md`
  `references/G1_docs/38_高层运动开发_手臂动作服务接口.md`
- G1 head camera and RealSense:
  `references/G1_docs/43_更多例程_深度相机例程.md`
- Troubleshooting:
  `references/G1_docs/09_常见问题.md`
  `references/G1_docs/10_常见错误及释义.md`

### 3. Answer in a practical order

Prefer this structure:

1. State the confirmed interface or workflow.
2. Call out prerequisites such as Ubuntu, network setup, or debug mode.
3. Give the implementation or debugging steps.
4. End with a concrete validation step the user can run.

## When the user asks about the G1 camera

Use `references/G1_docs/43_更多例程_深度相机例程.md` as the starting point.

The bundled G1 docs confirm:

- The G1 head depth camera is a RealSense D435i.
- On the robot's NX platform, `librealsense` should be installed before using RealSense tools.
- For ROS access, the docs point users to the official `realsense-ros` repository.
- For routine use, the docs note that SDK access is often recommended directly.

Use this section to explain:

- what the official G1 docs say about the hardware
- when ROS wrapper installation makes sense
- when SDK access may be simpler than ROS
- why project-local ROS topics should not be treated as official G1 defaults

Do not claim that any repository-local camera topic names are official G1 camera defaults unless the bundled docs confirm them.

## When the user asks to install RealSense ROS wrapper

Guide them with this order:

1. Confirm Ubuntu and ROS2 distro.
2. Confirm whether they are installing on the G1 development computer or an external Ubuntu PC.
3. Use the bundled G1 docs for G1-specific context.
4. Use the current official `realsense-ros` and `librealsense` docs for exact install commands.
5. End with a validation flow using commands such as `realsense-viewer`, `rs-enumerate-devices`, `ros2 node list`, and `ros2 topic list`.

The skill should be explicit that the bundled G1 docs provide the direction and official repository links, but the exact wrapper installation steps come from upstream RealSense documentation.

## English template: install `realsense-ros` on G1

Reuse and adapt the following template when the user explicitly asks how to install the RealSense ROS wrapper on a G1. Keep the answer in English unless the user asks for another language.

````markdown
Use these references first:

- G1 camera overview: `references/G1_docs/43_更多例程_深度相机例程.md`
- G1 ROS2 setup: `references/G1_docs/40_更多例程_ROS2_通信例程.md`
- G1 development environment and networking: `references/G1_docs/19_应用开发_快速开发.md`

According to the bundled G1 docs, the head camera on G1 is a RealSense D435i, and the NX development computer should have `librealsense` installed before using RealSense tools. The same docs point ROS users to the official `realsense-ros` repository.

I’d install it in this order:

1. Confirm the OS and ROS2 distro on the G1 development computer.
2. Confirm that `librealsense` is installed and the camera is visible.
3. Install the ROS2 wrapper from the official `realsense-ros` repository.
4. Launch the camera node.
5. Validate the node and topics from ROS2.

Typical validation commands:

```bash
realsense-viewer
rs-enumerate-devices
ros2 node list | grep camera
ros2 topic list | grep -E 'camera|image|depth'
```

Important note: if you already see custom camera topics on the robot, those may come from an application-specific bridge or capture node rather than from the official RealSense ROS wrapper. Do not treat custom topic names as the default G1 camera interface unless the docs confirm them.

For the exact install commands, follow the current upstream documentation here:

- `realsense-ros`: https://github.com/IntelRealSense/realsense-ros
- `librealsense`: https://github.com/IntelRealSense/librealsense

If you want, I can also help tailor the installation steps to your exact ROS2 distro on the G1 machine.
````

## Validation guidance for camera setup

When a user has installed or launched RealSense tooling, prefer these checks:

```bash
realsense-viewer
```

```bash
rs-enumerate-devices
```

```bash
ros2 node list | grep camera
```

```bash
ros2 topic list | grep -E 'camera|image|depth'
```

If the user is still using project-specific camera topics, explain that they may be emitted by a custom bridge or application node rather than by the official wrapper itself.

## Implementation guidance rules

- If the user asks which layer to use, explain the tradeoff between SDK2 or DDS-oriented workflows and ROS2-based workflows using the official docs.
- If the user asks for code, align the code with the interfaces confirmed in the docs or with the official RealSense ROS wrapper, and mark any project-specific adaptations clearly.
- If a request is under-specified, make the smallest safe assumption and state it briefly.
- If you cannot confirm a detail from the bundled references, say what is confirmed locally and what should be checked in the current official upstream docs or on hardware.

## Response style

- Be concise but concrete.
- Prefer local file references over vague statements.
- Highlight safety notes plainly when motion control or robot-side testing is involved.
- End with a next action the user can actually run or check.

## Example prompts this skill should trigger on

- "Help me install the RealSense ROS wrapper on the G1 robot."
- "Which G1 docs explain the head camera and how to use RealSense on G1?"
- "Should I use the RealSense ROS wrapper or the SDK directly on G1?"
- "I have custom camera topics on my robot. Are they official G1 topics or app-specific?"
- "Which G1 docs explain DDS topics and service interfaces?"
- "Should I use SDK2 or ROS2 for my G1 integration?"
