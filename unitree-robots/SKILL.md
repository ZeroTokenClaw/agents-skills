---
name: unitree-robots
description: 'Unitree robot software stack: which SDK, repo, or package applies to a given Unitree robot, CycloneDDS and network setup, install paths, and legacy-SDK traps. Use whenever writing or reviewing code that talks to Unitree robots (G1, G1D, Go2, B2, H1, H2), or when choosing ROS/ROS2 packages, simulators, or model assets for them.'
---

# Unitree robot software stack

Shared facts for the Unitree fleet. Robot-specific facts live in the unitree-g1 and unitree-g1d skills: load the one matching the robot in front of you.

## Two SDK generations

| SDK | Middleware | Robots | Status |
| --- | --- | --- | --- |
| `unitree_sdk2` (C++) and `unitree_sdk2_python` | CycloneDDS | G1, G1D, Go2, B2, H1 and newer | current |
| `unitree_legged_sdk` | LCM/UDP | Go1 only per its README | legacy; NOT for G1 or G1D |

The most common Unitree coding mistake is reaching for the wrong generation. G1 and G1D code goes through `unitree_sdk2` / `unitree_sdk2_python`, never `unitree_legged_sdk`.

## Repo map

| Repo | What it is | Notes |
| --- | --- | --- |
| [unitree_sdk2](https://github.com/unitreerobotics/unitree_sdk2) | C++ SDK: low-level, high-level, video, lidar clients | Current. Prebuilt static libs for x86_64 and aarch64. |
| [unitree_sdk2_python](https://github.com/unitreerobotics/unitree_sdk2_python) | Official Python bindings | Install from source; PyPI names are ambiguous. |
| [unitree_ros2](https://github.com/unitreerobotics/unitree_ros2) | ROS2 message packages and examples | README robot list is stale: G1 and H1-2 examples exist in the repo. |
| [unitree_ros](https://github.com/unitreerobotics/unitree_ros) | ROS1/Gazebo simulation and URDF descriptions | `robots/g1_description` (URDF/MJCF) lives here. |
| [unitree_model on Hugging Face](https://huggingface.co/datasets/unitreerobotics/unitree_model) | URDF/MJCF/USD model assets | The GitHub unitree_model repo is deprecated; this is the current home. |
| [unitree_mujoco](https://github.com/unitreerobotics/unitree_mujoco) | MuJoCo simulator speaking the same DDS topics | Sim-to-real path. Sim runs DDS domain 1 to avoid colliding with a live robot on domain 0. |
| [unitree_rl_gym](https://github.com/unitreerobotics/unitree_rl_gym) | Isaac-Gym RL training (G1, H1, Go2) | Older stack. |
| [unitree_rl_lab](https://github.com/unitreerobotics/unitree_rl_lab) | Isaac-Lab RL training (G1 29-DOF) | Newer stack. |
| [unitree_slam](https://github.com/unitreerobotics/unitree_slam) | SLAM and navigation example clients (`rt/qt_command` protocol) | Robot-side service, not part of unitree_sdk2. |
| [teleimager](https://github.com/unitreerobotics/teleimager) | Camera streaming server (ZMQ and WebRTC) | Runs on the robot dev PC; replaces the older image_server.py. |

## IDL namespaces

| Robot family | Namespace |
| --- | --- |
| G1, G1D, H1, H2 (humanoid generation) | `unitree_hg::msg::dds_` |
| Go2, B2 (quadruped generation) | `unitree_go::msg::dds_` |

Applying `unitree_go` message types to G1/G1D code is a hard error: the layouts differ.

## Network and DDS setup

- Robots live on `192.168.123.x/24`. Set the dev PC to a static IP in that subnet (official examples use `192.168.123.99`), connected by Ethernet.
- CycloneDDS version is 0.10.2 across the stack. The C++ SDK bundles it; the Python SDK needs `cyclonedds == 0.10.2` (set `CYCLONEDDS_HOME` if pip cannot find it).
- DDS domain: 0 for a real robot; unitree_mujoco uses 1.
- ChannelFactory init: `ChannelFactory::Instance()->Init(0, "eth0")` with the domain and the wired interface name.
- Raw SDK topics carry the `rt/` prefix (`rt/lowcmd`); ROS2 remapping drops it (`/lowcmd`). Never invent topic names.
- ROS2: `export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` and point `CYCLONEDDS_URI` at XML naming the wired interface. Use `lo` for simulation.

## Install

How the SDK is installed, for reference. Setup is the user's action: present the steps and let the user run them.

```bash
# C++
git clone https://github.com/unitreerobotics/unitree_sdk2.git
cd unitree_sdk2 && mkdir build && cd build && cmake .. && make

# Python: install from source, do not guess the PyPI name
git clone https://github.com/unitreerobotics/unitree_sdk2_python.git
cd unitree_sdk2_python && pip3 install -e .
```

PyPI has packages named unitree-sdk2 and unitree-sdk2py, but naming is ambiguous; source install is the reproducible path.

## Platform support and environment discipline

The officially supported SDK platform is Ubuntu 20.04 LTS, x86_64 and aarch64; Windows and macOS are not supported. In practice the Ubuntu target is the robot's onboard dev PC: the G1 EDU Jetson at 192.168.123.164 runs JetPack, so onboard setup over SSH uses Ubuntu commands.

That is a statement about where the SDK is supported, not permission to run Ubuntu commands on whatever machine you are on:

- Detect before acting: read `/etc/os-release` and `uname -m` so the instructions you give match the machine. Never assume apt.
- Never run package managers or installers yourself, and never install as a side effect of writing robot code. When something is missing (SDK, CycloneDDS, system packages), instruct the user: name what is needed and give the exact command for their distro. The user runs it; you record the outcome.
- Commands intended for the robot's PC belong on 192.168.123.164 over SSH. Hand the user those commands too; do not execute installs on the robot's PC yourself.
- A non-Ubuntu workstation is unofficial territory: the Python SDK may work there if cyclonedds 0.10.2 can be built, but verify instead of assuming, and never resolve an OS mismatch by installing Ubuntu packages on a non-Ubuntu host.
- If the repo has `docs/agents/robots.md` (written by /setup-robotics-skills), read it first: it records this workstation's actual OS and setup.

## Common mistakes

| Wrong | Right |
| --- | --- |
| `unitree_legged_sdk` for G1/G1D | `unitree_sdk2` / `unitree_sdk2_python` |
| Guessed pip name (`pip install unitree_sdk2`) | Clone the repo and `pip3 install -e .` |
| Invented topics like `/joint_commands` | The robot skill's topic table (`rt/lowcmd`, `rt/lowstate`, ...) |
| `unitree_go` types for a humanoid | `unitree_hg` types |
| unitree_model on GitHub | Hugging Face dataset |
| Trusting the unitree_ros2 README robot list | README is stale; G1 examples are in the repo |
| Assuming the workstation is Ubuntu | Detect the distro first (`/etc/os-release`); the Ubuntu target is the robot's Jetson over SSH |
| Running package managers or installers yourself | Instruct the user with the exact command for their OS; the user runs it |
| Skipping CycloneDDS setup | 0.10.2, domain 0, correct interface in CYCLONEDDS_URI |

## What to defer to the web

Release tags, changelogs, firmware downloads, PyPI naming, and README claims drift over time. Fetch the live sources instead of trusting cached values:

- [G1 developer docs](https://support.unitree.com/home/en/G1_developer/about_G1) and [G1D developer docs](https://support.unitree.com/home/en/G1D_Developer/)
- [SDK downloads](https://support.unitree.com/home/en/developer/Obtain%20SDK)
- The repo map above: each README is the current truth for install steps and supported robots

Deep reference material (full manuals, torque tables, RL training configs) also lives behind those links, not in this skill.
