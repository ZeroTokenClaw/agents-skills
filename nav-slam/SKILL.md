---
name: nav-slam
description: >
  Expert guidance for SLAM and Nav2 navigation in ROS 2 — slam_toolbox, AMCL, robot_localization, costmaps, planners, and controllers. Use when working with "SLAM", "slam_toolbox", "Nav2", "navigation2", "costmap", "costmap_2d", "path planning", "controller", "DWB", "MPPI", "behavior tree", "AMCL", "amcl", "particle filter", "robot_localization", "EKF", "navigate_to_pose", "navigate_through_poses", "planner_server", "controller_server", "bt_navigator", "inflation layer", "obstacle layer", "voxel layer", "static layer", "global costmap", "local costmap", "nav2_bringup", "nav2_params", "lifecycle manager", "tf tree", "occupancy grid", "map_server", "map_saver", "recovery behavior", or when the robot hits walls, gets lost, the map drifts, navigation fails, costmaps are wrong, or path planning breaks down.
---

# Navigation and SLAM Specialist

> **Quick navigation**
> - SLAM concepts, slam_toolbox config, map saving/loading --> `references/slam.md`
> - Nav2 architecture, costmaps, planners, controllers --> `references/nav2-stack.md`
> - Behavior trees, BT XML, custom nodes, waypoint patterns --> `references/behavior-trees.md`
> - Parameter tuning, inflation radius, speed limits, tracked robots --> `references/tuning.md`
> - Narrow passages, corridor following, confined space configs --> `references/confined-spaces.md`

---

## Who This Skill Is For

This skill is written for experienced software developers who are transitioning into robotics.
It focuses on practical, copy-paste-ready configurations over academic theory.

---

## SLAM vs Localization: When to Map vs When to Use an Existing Map

Before you do anything with navigation, answer one question: **do you already have a map?**

| Situation | What to run | Why |
|-----------|------------|-----|
| First time in environment, no map exists | **SLAM** (slam_toolbox online mode) | You need to build the map while driving around |
| Map exists but environment changes often | **SLAM** (slam_toolbox localization mode) | Use old map as starting point, update as you go |
| Map exists, environment is stable | **Localization only** (AMCL or slam_toolbox localization) | Just figure out where you are on the known map |
| Repeated visits to same location | **SLAM once**, then localization on subsequent runs | Build map on first visit, reuse it later |

**Key distinction:** SLAM builds the map while simultaneously tracking the robot's position
on it. Localization assumes the map already exists and only determines where the robot is.
You only need SLAM when the environment is new or has changed significantly.

For full SLAM details --> `references/slam.md`

---

## Nav2 Architecture Overview

**Nav2 is a modular architecture for robot movement.** Each component handles one concern
(planning, control, recovery), they communicate through ROS 2 actions/topics, and a
behavior tree orchestrates the overall navigation workflow.

```
                    +------------------+
                    |   bt_navigator   |  <-- The orchestrator
                    +--------+---------+
                             |
              +--------------+--------------+
              |              |              |
     +--------v---+  +------v------+  +----v--------+
     | planner    |  | controller  |  | behavior    |
     | _server    |  | _server     |  | _server     |
     +------------+  +-------------+  +-------------+
     Computes path   Follows path     Recovery actions
     (A* / Dijkstra) (steering cmds)  (spin, backup)
              |              |
     +--------v--------------v--------+
     |         costmap_2d              |
     +---------------------------------+
     Layered "danger map" of the world
```

### Nav2 Core Components

| Nav2 Component | What It Does |
|----------------|--------------|
| `bt_navigator` | Orchestrates the navigation workflow using a behavior tree |
| `planner_server` | Computes a path from A to B on the map |
| `controller_server` | Converts the planned path into velocity commands |
| `behavior_server` | Recovery behaviors when things go wrong (spin, backup, wait) |
| `costmap_2d` | Maintains a layered grid of obstacle information |
| `map_server` | Serves the pre-built map |
| `robot_localization` / AMCL | Answers "where am I?" on the map |
| Lifecycle manager | Manages node startup/shutdown order |

For detailed Nav2 architecture --> `references/nav2-stack.md`

---

## Navigation Stack Component Selection

### Planner Selection (How to compute the path)

| Planner | Best For | Trade-off |
|---------|----------|-----------|
| **NavFn** (Dijkstra/A*) | Simple environments, circular robots | Fast but paths hug obstacles |
| **Smac 2D** | Grid-based planning, any robot shape | Better quality than NavFn, slightly slower |
| **Smac Hybrid-A*** | Car-like robots (Ackermann steering) | Considers turning radius, slower |
| **Smac Lattice** | Complex kinematic constraints | Most accurate for non-holonomic, slowest |
| **Theta*** | Open environments with few obstacles | Produces smooth, any-angle paths |

### Controller Selection (How to follow the path)

| Controller | Best For | Trade-off |
|------------|----------|-----------|
| **DWB** (Dynamic Window) | General purpose, well-tested | Many parameters to tune |
| **MPPI** | Complex environments, dynamic obstacles | Best quality, higher CPU usage |
| **Regulated Pure Pursuit** | Tracked/skid-steer robots, corridors | Simple, reliable, fewer params |

### Recommended Combinations

| Robot Type | Planner | Controller | Why |
|------------|---------|------------|-----|
| Tracked/skid-steer (inspection bot) | Smac 2D | Regulated Pure Pursuit | Handles tight turns, simple tuning |
| Differential drive (indoor) | NavFn | DWB | Well-tested combo, good docs |
| Fast outdoor robot | Smac Hybrid-A* | MPPI | Respects kinematics, handles dynamics |
| Confined spaces / tunnels | Smac 2D | Regulated Pure Pursuit | Predictable in narrow passages |

---

## Common Navigation Failure Diagnosis

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Robot won't move at all | Lifecycle nodes not active, or costmap shows robot inside obstacle | Check `ros2 lifecycle list`, verify footprint size |
| Path not found | Inflation radius too large, or start/goal inside inflated zone | Reduce `inflation_radius`, check `cost_scaling_factor` |
| Robot oscillates back and forth | Controller gains too aggressive, or goal tolerance too tight | Increase `xy_goal_tolerance`, reduce `max_vel_x` |
| Robot hits obstacles | Local costmap not seeing obstacles, or inflation too small | Check sensor topics in costmap config, increase `inflation_radius` |
| Robot gets stuck in doorways | Inflation makes doorway impassable | Reduce `inflation_radius` to < half doorway width |
| Robot spins in place forever | Rotation speed too low for recovery, or angular goal tolerance too tight | Increase recovery spin speed, relax `yaw_goal_tolerance` |
| Map drifts over time | Poor odometry, no loop closures in SLAM | Calibrate odometry, ensure loop closure opportunities |
| Localization jumps suddenly | Too few AMCL particles, or kidnapped robot | Increase `max_particles`, add `recovery_alpha_slow/fast` |
| Costmap not clearing obstacles | Obstacle layer not decaying, or sensor not publishing | Check `observation_sources`, set `obstacle_max_range` |
| Navigation is very slow | Controller frequency too low, or speed limits too conservative | Increase `controller_frequency` to 20Hz, raise speed limits |

---

## Costmap Layers Explained

The costmap is a layered grid representing danger zones around the robot. Multiple layers are
stacked on top of each other, each contributing different obstacle information. The final
costmap is the composite of all layers, used by planners and controllers to avoid collisions.

```
Final Costmap = Static Layer + Obstacle Layer + Inflation Layer
                (the map)     (live sensors)   (safety buffer)
```

| Layer | What It Does |
|-------|-------------|
| **Static Layer** | Loads the pre-built map (walls, permanent obstacles) |
| **Obstacle Layer** | Adds real-time sensor data (LiDAR, depth camera) |
| **Inflation Layer** | Expands obstacles by a safety radius to create a buffer zone |
| **Voxel Layer** | 3D version of obstacle layer (for depth cameras) |

**Key insight:** The inflation layer is what actually keeps the robot from hitting walls. Without
it, the planner would plan paths that graze obstacles. The `inflation_radius` should be at least
the robot's radius, and the `cost_scaling_factor` controls how quickly the "danger" falls off
with distance.

```yaml
# Costmap configuration example
global_costmap:
  global_costmap:
    ros__parameters:
      plugins: ["static_layer", "obstacle_layer", "inflation_layer"]
      static_layer:
        plugin: "nav2_costmap_2d::StaticLayer"
        map_subscribe_transactional: true
      obstacle_layer:
        plugin: "nav2_costmap_2d::ObstacleLayer"
        observation_sources: scan
        scan:
          topic: /scan
          max_obstacle_height: 2.0
          clearing: true
          marking: true
          raytrace_max_range: 3.0
          obstacle_max_range: 2.5
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        inflation_radius: 0.35        # meters -- at least robot radius
        cost_scaling_factor: 5.0       # higher = danger drops off faster
```

For full costmap configuration --> `references/nav2-stack.md`
For confined space costmap tuning --> `references/confined-spaces.md`

---

## Quick-Start: Zero to Navigating in 30 Minutes

This assumes you have a robot with a LiDAR and working odometry in ROS 2 (Humble or later).

### Step 1: Install Nav2 and slam_toolbox (2 minutes)

```bash
sudo apt install ros-${ROS_DISTRO}-navigation2 \
                 ros-${ROS_DISTRO}-nav2-bringup \
                 ros-${ROS_DISTRO}-slam-toolbox
```

### Step 2: Build a Map with SLAM (10 minutes)

```bash
# Terminal 1: Launch your robot (provides /scan and /odom)
ros2 launch my_robot_bringup robot.launch.py

# Terminal 2: Launch slam_toolbox in online mode
ros2 launch slam_toolbox online_async_launch.py

# Terminal 3: Launch RViz to visualize
ros2 launch nav2_bringup rviz_launch.py

# Terminal 4: Drive the robot around (teleop)
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Drive around your environment slowly and completely. Watch the map build in RViz. When done:

```bash
# Save the map
ros2 run nav2_map_server map_saver_cli -f ~/my_map
# This creates my_map.pgm (image) and my_map.yaml (metadata)
```

### Step 3: Configure Nav2 Parameters (10 minutes)

Create a `nav2_params.yaml` file. Start with the default from nav2_bringup and modify:

```yaml
# Key parameters to customize for YOUR robot:
robot_radius: 0.15                    # Your robot's radius in meters
inflation_radius: 0.25                # Safety buffer (> robot_radius)
max_vel_x: 0.3                        # Max forward speed (m/s)
max_vel_theta: 1.0                    # Max rotation speed (rad/s)
xy_goal_tolerance: 0.1                # How close to goal (meters)
yaw_goal_tolerance: 0.15              # How close to goal angle (radians)
controller_frequency: 20.0            # How often to send velocity commands
```

For a complete params file --> `references/nav2-stack.md`
For tuning guidance --> `references/tuning.md`

### Step 4: Launch Navigation (5 minutes)

```bash
# Terminal 1: Launch your robot
ros2 launch my_robot_bringup robot.launch.py

# Terminal 2: Launch Nav2 with your map and params
ros2 launch nav2_bringup bringup_launch.py \
  map:=$HOME/my_map.yaml \
  params_file:=nav2_params.yaml

# Terminal 3: Launch RViz
ros2 launch nav2_bringup rviz_launch.py
```

In RViz:
1. Click "2D Pose Estimate" and click/drag on the map to set the robot's initial position
2. Click "Nav2 Goal" and click/drag to set a navigation goal
3. Watch the robot plan a path and navigate to the goal

### Step 5: Iterate (3 minutes)

If navigation doesn't work well:
- Robot hits things --> increase `inflation_radius` --> `references/tuning.md`
- Robot won't fit through doors --> decrease `inflation_radius`
- Robot oscillates --> see tuning guide --> `references/tuning.md`
- Robot gets stuck --> check recovery behaviors --> `references/behavior-trees.md`

---

## Behavior Trees: The Navigation Brain

Behavior trees are how Nav2 decides **what to do and when**. They are a composable
alternative to complex if/else chains or state machines. Each node in the tree either
succeeds, fails, or is still running. Parent nodes decide whether to try alternatives
(Fallback) or require all children to succeed (Sequence).

For full BT details --> `references/behavior-trees.md`

---

## Sensor Fusion and Localization

Your robot needs to know where it is. This typically involves fusing multiple data sources:

| Source | What It Provides | Accuracy |
|--------|-----------------|----------|
| Wheel odometry | Relative position from wheel encoders | Drifts over time (5-10% error) |
| IMU | Angular velocity, linear acceleration | Good for rotation, noisy for position |
| LiDAR + AMCL | Global position on known map | Good when map matches reality |
| LiDAR + SLAM | Global position while building map | Good during active mapping |

**`robot_localization` (EKF)** fuses odometry + IMU into a smooth odometry estimate. This feeds
into AMCL or SLAM for global localization. It acts as a preprocessing step that cleans up
raw sensor data before the global localization system uses it.

```
Wheel encoders ----+
                   +--> robot_localization (EKF) --> /odom --> AMCL/SLAM --> /map
IMU ---------------+
```

---

## TF Tree: The Coordinate System

Every robot in ROS 2 has a transform tree (TF tree) that describes how different parts
relate spatially. The three critical frames for navigation:

```
map --> odom --> base_link
 |       |         |
 |       |         +-- Where the robot body is
 |       +------------ Smooth but drifting odometry frame
 +-------------------- Global, corrected frame (from AMCL/SLAM)
```

**How the frames work together:** `base_link` represents the robot body. `odom` provides a
smooth but slowly drifting local reference frame based on wheel encoders/IMU. `map` is the
global frame that periodically corrects drift using AMCL or SLAM observations.

**Common TF problems:**
- "Transform timeout" --> Some node isn't publishing its transform. Check with `ros2 run tf2_tools view_frames`
- "Extrapolation into the future" --> Clock sync issue between nodes. Check time sources
- "Could not find transform" --> Missing link in the chain. Verify your URDF and state publishers

---

## Essential ROS 2 Navigation Commands

Cheat sheet for the most common commands you'll use during development.

### Building and launching

```bash
# Install all Nav2 packages
sudo apt install ros-${ROS_DISTRO}-navigation2 ros-${ROS_DISTRO}-nav2-bringup \
                 ros-${ROS_DISTRO}-slam-toolbox ros-${ROS_DISTRO}-robot-localization

# Source your workspace
source /opt/ros/${ROS_DISTRO}/setup.bash
source ~/ros2_ws/install/setup.bash

# Launch Nav2 with your params
ros2 launch nav2_bringup bringup_launch.py \
  map:=/path/to/map.yaml \
  params_file:=/path/to/nav2_params.yaml
```

### Debugging commands

```bash
# Check what nodes are running
ros2 node list

# Check what topics are available
ros2 topic list

# Check TF tree (FIRST thing to check when navigation doesn't work)
ros2 run tf2_tools view_frames
# Generates frames.pdf showing the full transform tree

# Check if a specific transform exists
ros2 run tf2_ros tf2_echo map base_link

# Monitor costmap
ros2 topic echo /local_costmap/costmap_raw --once | head -20

# Check Nav2 lifecycle states
ros2 lifecycle list /controller_server
ros2 lifecycle list /planner_server
ros2 lifecycle list /bt_navigator

# Manually activate a lifecycle node
ros2 lifecycle set /controller_server activate

# Send a navigation goal from command line
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: 'map'}, pose: {position: {x: 2.0, y: 1.0}}}}"

# Save a map during SLAM
ros2 run nav2_map_server map_saver_cli -f ~/maps/my_map
```

### Monitoring navigation

```bash
# Watch navigation feedback (distance remaining, ETA)
ros2 topic echo /navigate_to_pose/_action/feedback

# Watch velocity commands being sent to robot
ros2 topic echo /cmd_vel

# Watch costmap update rate
ros2 topic hz /local_costmap/costmap_raw

# Record a rosbag for later analysis
ros2 bag record /scan /odom /tf /tf_static /cmd_vel /map -o inspection_run_001
```

---

## Glossary

| Robotics Term | Definition |
|--------------|-----------|
| **Odometry** | Estimate of robot position from wheel encoders |
| **TF (Transform)** | Coordinate frame relationships describing how frames relate spatially |
| **Topic** | Pub/sub message channel in ROS 2 |
| **Action** | Long-running ROS 2 request with feedback and cancellation support |
| **Service** | Request/response RPC call in ROS 2 |
| **Costmap** | Grid of obstacle costs used for path planning and obstacle avoidance |
| **Occupancy grid** | Map of free/occupied/unknown cells (the output of SLAM) |
| **Frame** | A coordinate system (e.g., `map`, `odom`, `base_link`) |
| **Lifecycle node** | ROS 2 node with managed state transitions (configure/activate/deactivate) |
| **Behavior tree** | Decision-making structure that orchestrates navigation actions |
| **Planner** | Computes a collision-free path from A to B on the costmap |
| **Controller** | Follows a planned path by sending velocity commands to the robot |
| **Recovery behavior** | Action taken when navigation fails (e.g., backup, clear costmap) |
| **Localization** | Determining the robot's position on a known map |
| **SLAM** | Simultaneously building a map and localizing the robot within it |
| **Loop closure** | Recognizing a previously visited location to correct accumulated drift |
| **Inflation** | Safety buffer around obstacles in the costmap |
| **Footprint** | Physical shape/size of the robot used for collision checking |

---

## Reference File Index

| File | Read When |
|------|-----------|
| `references/slam.md` | Setting up SLAM, building maps, tuning slam_toolbox, diagnosing map quality issues |
| `references/nav2-stack.md` | Configuring Nav2, choosing planners/controllers, setting up costmaps, writing params YAML |
| `references/behavior-trees.md` | Customizing navigation behavior, adding inspection logic, understanding BT nodes |
| `references/tuning.md` | Robot hits things, oscillates, gets stuck, goes too slow/fast, tracked robot setup |
| `references/confined-spaces.md` | Narrow passages, corridors, tunnels, confined spaces, wall following |
