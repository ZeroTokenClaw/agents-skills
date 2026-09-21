---
name: unitree-go2-sdk-skill
description: Unitree GO2 EDU bringup, SDK2, DDS, safety, and ROS 2 Humble integration workflow for real-robot projects. Use when Codex needs to configure or debug unitree_sdk2 and unitree_ros2, verify network and CycloneDDS assumptions, map GO2 control and state channels into ROS 2, review launch and bridge setup, or prepare safe real-robot motion before navigation work.
---

# Unitree GO2 SDK Skill

Use this skill as the GO2 real-robot foundation layer. It is the right skill when the task is about making the robot reachable, observable, and safe before higher-level navigation begins.

## Routing

Read only the reference file that matches the task:

- Bringup, environment, network, DDS, launch order: `references/bringup-checklist.md`
- Topic, state, command ownership, and bridge boundaries: `references/control-surfaces.md`
- Real-robot motion gating and lab safety: `references/safety-preflight.md`

Pair this skill with:

- `ros2-skill` when the task needs live ROS 2 inspection or commands on the robot.
- `ros2-engineering-skills` when the task needs code, launch, QoS, tf, or driver changes.

## Default Assumptions

Unless the user says otherwise, assume:

- Robot: Unitree GO2 EDU
- ROS distro: ROS 2 Humble
- OS: Ubuntu 22.04
- Target: real robot, not simulation
- Project phase: indoor navigation first, outdoor autonomy later

## Core Rules

1. Treat robot safety and command ownership as more important than speed of debugging.
2. Prefer official Unitree conventions before adding wrapper layers.
3. Confirm which process owns motion commands before testing movement.
4. Do not mix low-level SDK testing and Nav2 control in the same step without stating the handoff.
5. When a fact is runtime-dependent, verify it live instead of assuming it from documentation.

## Workflow

1. Confirm distro, network path, and ROS environment.
2. Verify the Unitree bridge or ROS 2 nodes publish stable state data before touching commands.
3. Identify the command path that should own motion for the current task.
4. Apply the preflight checklist before any real-robot movement.
5. Only then move on to SLAM, localization, or Nav2 tuning.

## Output Expectations

When using this skill, produce:

- The current GO2 integration layer being used
- The expected state and command interfaces
- The next safe verification step
- Any assumption that still needs live confirmation
