# Nav2 Stack Reference

## Table of Contents

1. [Nav2 Architecture](#1-nav2-architecture)
2. [Costmap Configuration](#2-costmap-configuration)
3. [Costmap Layers](#3-costmap-layers)
4. [Planner Selection](#4-planner-selection)
5. [Controller Selection](#5-controller-selection)
6. [When to Use Which Planner/Controller](#6-when-to-use-which-plannercontroller)
7. [Recovery Behaviors](#7-recovery-behaviors)
8. [Lifecycle Management](#8-lifecycle-management)
9. [Navigation Actions](#9-navigation-actions)
10. [Configuration Parameter Reference](#10-configuration-parameter-reference)
11. [Complete Example: Nav2 Params for a Tracked Robot](#11-complete-example-nav2-params-for-a-tracked-robot)

---

## 1. Nav2 Architecture

Nav2 is a collection of ROS 2 nodes that work together to make a robot navigate autonomously.
Each node is a separate process communicating via ROS 2 topics, services, and actions.

### Core components

| Component | ROS 2 Node | Purpose |
|-----------|-----------|---------|
| **BT Navigator** | `bt_navigator` | Orchestrates navigation using behavior trees |
| **Planner Server** | `planner_server` | Computes paths from A to B |
| **Controller Server** | `controller_server` | Follows paths by sending velocity commands |
| **Behavior Server** | `behavior_server` | Recovery behaviors (spin, backup, wait) |
| **Costmap 2D** | `*_costmap/costmap` | Layered obstacle maps |
| **Map Server** | `map_server` | Serves the static map |
| **AMCL** | `amcl` | Particle filter localization |
| **Lifecycle Manager** | `lifecycle_manager` | Manages startup/shutdown order |
| **Velocity Smoother** | `velocity_smoother` | Smooths velocity commands |
| **Collision Monitor** | `collision_monitor` | Emergency stop on imminent collision |

### Data flow

```
LiDAR (/scan) ---------> Costmap (obstacle layer)
                              |
Map Server (/map) ------> Costmap (static layer)
                              |
                    +---------v-----------+
                    |   Costmap 2D        |
                    | (global + local)    |
                    +---------+-----------+
                              |
BT Navigator ----> Planner Server: "Plan from A to B"
     |                    |
     |             Uses global costmap to find path
     |                    |
     |             Returns: nav_msgs/Path
     |                    |
     +-----------> Controller Server: "Follow this path"
     |                    |
     |             Uses local costmap to avoid obstacles
     |                    |
     |             Publishes: geometry_msgs/Twist (/cmd_vel)
     |                    |
     +-----------> Behavior Server: "Spin/Backup/Wait"
                          |
                   When controller fails, try recovery
```

### Two costmaps: global vs local

Nav2 uses **two separate costmaps** -- this is a critical concept:

| Costmap | Purpose | Size | Update rate | Used by |
|---------|---------|------|-------------|---------|
| **Global** | Full map for path planning | Entire map | Slow (map + obstacles) | Planner Server |
| **Local** | Rolling window for obstacle avoidance | 3-5m around robot | Fast (sensor data) | Controller Server |

The global costmap is comprehensive but updates slowly. The local costmap is smaller
but reflects real-time sensor data, making it responsive to dynamic obstacles.

---

## 2. Costmap Configuration

### Global costmap

The global costmap covers the entire environment and is used for path planning.

```yaml
global_costmap:
  global_costmap:
    ros__parameters:
      update_frequency: 1.0            # Hz -- doesn't need to be fast
      publish_frequency: 1.0
      global_frame: map
      robot_base_frame: base_link
      use_sim_time: false
      robot_radius: 0.15               # meters (circular robot)
      # OR for non-circular:
      # footprint: "[[0.15, 0.15], [0.15, -0.15], [-0.15, -0.15], [-0.15, 0.15]]"
      resolution: 0.05                 # meters per cell (match your map resolution)
      track_unknown_space: true        # Treat unknown as obstacle
      plugins: ["static_layer", "obstacle_layer", "inflation_layer"]
      static_layer:
        plugin: "nav2_costmap_2d::StaticLayer"
        map_subscribe_transactional: true
      obstacle_layer:
        plugin: "nav2_costmap_2d::ObstacleLayer"
        enabled: true
        observation_sources: scan
        scan:
          topic: /scan
          max_obstacle_height: 2.0
          clearing: true
          marking: true
          data_type: "LaserScan"
          raytrace_max_range: 5.0
          raytrace_min_range: 0.0
          obstacle_max_range: 4.5
          obstacle_min_range: 0.0
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 3.0
        inflation_radius: 0.35
```

### Local costmap

The local costmap is a rolling window around the robot, used for real-time obstacle avoidance.

```yaml
local_costmap:
  local_costmap:
    ros__parameters:
      update_frequency: 5.0            # Hz -- needs to be faster than global
      publish_frequency: 2.0
      global_frame: odom               # Note: odom, not map (for smoothness)
      robot_base_frame: base_link
      use_sim_time: false
      rolling_window: true             # Moves with the robot
      width: 3                         # meters (3m x 3m window)
      height: 3
      resolution: 0.05
      robot_radius: 0.15
      plugins: ["voxel_layer", "inflation_layer"]
      voxel_layer:
        plugin: "nav2_costmap_2d::VoxelLayer"
        enabled: true
        publish_voxel_map: true
        origin_z: 0.0
        z_resolution: 0.05
        z_voxels: 16
        max_obstacle_height: 2.0
        mark_threshold: 0
        observation_sources: scan
        scan:
          topic: /scan
          max_obstacle_height: 2.0
          clearing: true
          marking: true
          data_type: "LaserScan"
          raytrace_max_range: 3.0
          raytrace_min_range: 0.0
          obstacle_max_range: 2.5
          obstacle_min_range: 0.0
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 3.0
        inflation_radius: 0.35
```

---

## 3. Costmap Layers

### Static Layer

Loads the pre-built map from `map_server`. This is the "background" of your costmap.

```yaml
static_layer:
  plugin: "nav2_costmap_2d::StaticLayer"
  map_subscribe_transactional: true    # Wait for full map before using
  enabled: true
```

### Obstacle Layer

Adds real-time sensor observations. Each sensor is an "observation source."

```yaml
obstacle_layer:
  plugin: "nav2_costmap_2d::ObstacleLayer"
  enabled: true
  observation_sources: scan depth
  scan:
    topic: /scan
    data_type: "LaserScan"
    marking: true                      # Add obstacles to costmap
    clearing: true                     # Remove obstacles when no longer seen
    max_obstacle_height: 2.0
    obstacle_max_range: 4.5            # Only trust readings within this range
    obstacle_min_range: 0.0
    raytrace_max_range: 5.0            # Raytrace (clear) up to this range
    raytrace_min_range: 0.0
  depth:
    topic: /depth_camera/points
    data_type: "PointCloud2"
    marking: true
    clearing: true
    max_obstacle_height: 1.5
    min_obstacle_height: 0.1           # Ignore ground plane
```

### Inflation Layer

The most important layer for navigation behavior. It creates a gradient of cost around
obstacles, keeping the robot away from walls.

```yaml
inflation_layer:
  plugin: "nav2_costmap_2d::InflationLayer"
  cost_scaling_factor: 3.0             # How quickly cost decreases with distance
  inflation_radius: 0.35               # Maximum inflation distance (meters)
```

**Understanding `cost_scaling_factor` and `inflation_radius`:**

```
                     LETHAL (254)
Cost    |||||||||||
        |||||||||||\
        |||||||||||  \___  cost_scaling_factor = 3.0 (steep dropoff)
        |||||||||||      \_____
        |||||||||||             \____  cost_scaling_factor = 1.0 (gradual)
        |||||||||||                  \_______
        -----------|------|----------------> Distance from obstacle
                   ^      ^
              robot    inflation
              radius   radius
```

- `inflation_radius` = how far from obstacles the cost extends
- `cost_scaling_factor` = how steep the cost dropoff is (higher = steeper = robot drives closer to obstacles)

**Rule of thumb:**
- `inflation_radius` >= robot radius + safety margin (0.05-0.1m)
- `cost_scaling_factor` 3.0-5.0 for normal navigation, 8.0-10.0 for tight spaces (lets robot get closer)

### Voxel Layer

3D version of the obstacle layer. Used when you have depth cameras or 3D LiDAR and need
to track obstacles at different heights.

```yaml
voxel_layer:
  plugin: "nav2_costmap_2d::VoxelLayer"
  enabled: true
  publish_voxel_map: true              # Publish for debugging in RViz
  origin_z: 0.0
  z_resolution: 0.05                   # Height resolution (meters)
  z_voxels: 16                         # Number of voxel layers (0.05 * 16 = 0.8m height)
  max_obstacle_height: 2.0
  mark_threshold: 0                    # Min voxels in column to mark as obstacle
```

---

## 4. Planner Selection

### NavFn (default)

Classic Dijkstra/A* planner on the costmap grid. Fast and reliable.

```yaml
planner_server:
  ros__parameters:
    planner_plugins: ["GridBased"]
    GridBased:
      plugin: "nav2_navfn_planner/NavfnPlanner"
      tolerance: 0.5                   # Goal tolerance for planning
      use_astar: true                  # A* (faster) vs Dijkstra (optimal)
      allow_unknown: true              # Plan through unknown space
```

### Smac 2D

Better path quality than NavFn, considers 8-connected grid instead of 4-connected.

```yaml
planner_server:
  ros__parameters:
    planner_plugins: ["GridBased"]
    GridBased:
      plugin: "nav2_smac_planner/SmacPlanner2D"
      tolerance: 0.25
      max_iterations: 1000000
      allow_unknown: true
      max_on_approach_iterations: 1000
      cost_travel_multiplier: 2.0      # Penalize traveling through high-cost areas
```

### Smac Hybrid-A*

For robots with turning radius constraints (Ackermann steering, large tracked vehicles).

```yaml
planner_server:
  ros__parameters:
    planner_plugins: ["GridBased"]
    GridBased:
      plugin: "nav2_smac_planner/SmacPlannerHybrid"
      minimum_turning_radius: 0.40     # meters -- your robot's min turning radius
      motion_model_for_search: "DUBIN"  # or "REEDS_SHEPP" (allows reversing)
      allow_unknown: true
      max_iterations: 1000000
```

### Theta*

Any-angle planner that produces smooth paths in open environments.

```yaml
planner_server:
  ros__parameters:
    planner_plugins: ["GridBased"]
    GridBased:
      plugin: "nav2_theta_star_planner/ThetaStarPlanner"
      how_many_corners: 8              # 8-connected grid
      w_euc_cost: 1.0                  # Weight for euclidean cost
      w_traversal_cost: 2.0            # Weight for traversal cost
```

---

## 5. Controller Selection

### DWB (Dynamic Window Approach B)

General-purpose controller with many tunable parameters. Well-tested but requires
careful parameter tuning.

```yaml
controller_server:
  ros__parameters:
    controller_plugins: ["FollowPath"]
    FollowPath:
      plugin: "dwb_core::DWBLocalPlanner"
      min_vel_x: 0.0
      min_vel_y: 0.0
      max_vel_x: 0.3
      max_vel_y: 0.0                   # 0 for differential/tracked robots
      max_vel_theta: 1.0
      min_speed_xy: 0.0
      max_speed_xy: 0.3
      min_speed_theta: 0.0
      acc_lim_x: 2.5
      acc_lim_y: 0.0
      acc_lim_theta: 3.2
      decel_lim_x: -2.5
      decel_lim_y: 0.0
      decel_lim_theta: -3.2
      vx_samples: 20
      vy_samples: 0
      vtheta_samples: 40
      sim_time: 1.5
      transform_tolerance: 0.2
      xy_goal_tolerance: 0.15
      trans_stopped_velocity: 0.25
      short_circuit_trajectory_evaluation: true
      critics: ["RotateToGoal", "Oscillation", "BaseObstacle", "GoalAlign",
                "PathAlign", "PathDist", "GoalDist"]
      BaseObstacle.scale: 0.02
      PathAlign.scale: 32.0
      PathAlign.forward_point_distance: 0.1
      GoalAlign.scale: 24.0
      GoalAlign.forward_point_distance: 0.1
      PathDist.scale: 32.0
      GoalDist.scale: 24.0
      RotateToGoal.scale: 32.0
      RotateToGoal.slowing_factor: 5.0
      RotateToGoal.lookahead_time: -1.0
```

### MPPI (Model Predictive Path Integral)

State-of-the-art controller. Produces the best behavior but uses more CPU.

```yaml
controller_server:
  ros__parameters:
    controller_plugins: ["FollowPath"]
    FollowPath:
      plugin: "nav2_mppi_controller::MPPIController"
      time_steps: 56
      model_dt: 0.05
      batch_size: 2000
      vx_std: 0.2
      vy_std: 0.0
      wz_std: 0.4
      vx_max: 0.3
      vx_min: -0.1
      vy_max: 0.0
      wz_max: 1.0
      iteration_count: 1
      prune_distance: 1.7
      transform_tolerance: 0.1
      temperature: 0.3
      gamma: 0.015
      motion_model: "DiffDrive"        # or "Ackermann", "Omni"
      visualize: false
      critics: ["ConstraintCritic", "ObstaclesCritic", "GoalCritic",
                "GoalAngleCritic", "PathAlignCritic", "PathFollowCritic",
                "PathAngleCritic", "PreferForwardCritic"]
      ConstraintCritic:
        enabled: true
        cost_weight: 4.0
        cost_power: 1
      ObstaclesCritic:
        enabled: true
        cost_weight: 1.0
        repulsion_weight: 0.1
        critical_weight: 20.0
        consider_footprint: false
        collision_cost: 10000.0
        collision_margin_distance: 0.1
        near_goal_distance: 0.5
      GoalCritic:
        enabled: true
        cost_weight: 5.0
        cost_power: 1
        threshold_to_consider: 1.4
      GoalAngleCritic:
        enabled: true
        cost_weight: 3.0
        cost_power: 1
        threshold_to_consider: 0.5
      PathFollowCritic:
        enabled: true
        cost_weight: 5.0
        offset_from_furthest: 5
        threshold_to_consider: 1.4
      PreferForwardCritic:
        enabled: true
        cost_weight: 5.0
        cost_power: 1
        threshold_to_consider: 0.5
```

### Regulated Pure Pursuit

Simple, reliable controller excellent for tracked/skid-steer robots and corridors.

```yaml
controller_server:
  ros__parameters:
    controller_plugins: ["FollowPath"]
    FollowPath:
      plugin: "nav2_regulated_pure_pursuit_controller::RegulatedPurePursuitController"
      desired_linear_vel: 0.3
      lookahead_dist: 0.6
      min_lookahead_dist: 0.3
      max_lookahead_dist: 0.9
      lookahead_time: 1.5
      rotate_to_heading_angular_vel: 1.0
      transform_tolerance: 0.1
      use_velocity_scaled_lookahead_dist: true
      min_approach_linear_velocity: 0.05
      approach_velocity_scaling_dist: 0.6
      use_collision_detection: true
      max_allowed_time_to_collision_up_to_carrot: 1.0
      use_regulated_linear_velocity_scaling: true
      use_cost_regulated_linear_velocity_scaling: false
      regulated_linear_scaling_min_radius: 0.9
      regulated_linear_scaling_min_speed: 0.25
      allow_reversing: false
      max_angular_accel: 3.2
      max_robot_pose_search_dist: 10.0
```

---

## 6. When to Use Which Planner/Controller

| Scenario | Planner | Controller | Reasoning |
|----------|---------|------------|-----------|
| Indoor tracked robot (confined-space inspection) | Smac 2D | Regulated Pure Pursuit | Simple, reliable, works in tight spaces |
| Differential drive in office | NavFn | DWB | Well-documented, good default |
| Complex dynamic environment | Smac 2D | MPPI | Best obstacle avoidance behavior |
| Car-like robot (Ackermann) | Smac Hybrid-A* | Regulated Pure Pursuit | Respects turning radius |
| Confined space / tunnel navigation | Smac 2D | Regulated Pure Pursuit | Predictable, handles corridors well |
| Large outdoor area | Theta* | MPPI | Smooth paths, dynamic obstacle handling |
| Budget compute (Raspberry Pi) | NavFn | Regulated Pure Pursuit | Lowest CPU usage |

---

## 7. Recovery Behaviors

When navigation fails (controller can't follow path, robot is stuck), Nav2 tries
recovery behaviors before giving up. These are defined in the behavior tree and
executed by the `behavior_server`.

### Built-in recovery behaviors

| Behavior | What It Does | When It Helps |
|----------|-------------|---------------|
| **Spin** | Rotate in place 360 degrees | Clears local costmap by scanning all around |
| **BackUp** | Drive backward a short distance | Gets unstuck from tight spots |
| **Wait** | Pause for a duration | Lets dynamic obstacles move away |
| **ClearEntireCostmap** | Wipes and rebuilds local/global costmap | Fixes phantom obstacles |

```yaml
behavior_server:
  ros__parameters:
    costmap_topic: local_costmap/costmap_raw
    footprint_topic: local_costmap/published_footprint
    cycle_frequency: 10.0
    behavior_plugins: ["spin", "backup", "drive_on_heading", "wait",
                       "assisted_teleop"]
    spin:
      plugin: "nav2_behaviors/Spin"
    backup:
      plugin: "nav2_behaviors/BackUp"
    drive_on_heading:
      plugin: "nav2_behaviors/DriveOnHeading"
    wait:
      plugin: "nav2_behaviors/Wait"
    assisted_teleop:
      plugin: "nav2_behaviors/AssistedTeleop"
    global_frame: odom
    robot_base_frame: base_link
    transform_tolerance: 0.1
    simulate_ahead_time: 2.0
    max_rotational_vel: 1.0
    min_rotational_vel: 0.4
    rotational_acc_lim: 3.2
```

---

## 8. Lifecycle Management

Nav2 uses ROS 2 lifecycle nodes. This means nodes go through a startup sequence:
unconfigured --> inactive --> active. The lifecycle manager handles this.

```yaml
bt_navigator:
  ros__parameters:
    use_sim_time: false
    global_frame: map
    robot_base_frame: base_link
    odom_topic: /odom
    bt_loop_duration: 10
    default_server_timeout: 20
    navigators: ["navigate_to_pose", "navigate_through_poses"]
    navigate_to_pose:
      plugin: "nav2_bt_navigator/NavigateToPoseNavigator"
    navigate_through_poses:
      plugin: "nav2_bt_navigator/NavigateThroughPosesNavigator"
    # Path to custom BT XML (empty = use default)
    # default_nav_to_pose_bt_xml: ""
    # default_nav_through_poses_bt_xml: ""

lifecycle_manager:
  ros__parameters:
    use_sim_time: false
    autostart: true                    # Auto-activate all nodes on startup
    node_names:
      - "map_server"
      - "amcl"
      - "controller_server"
      - "planner_server"
      - "behavior_server"
      - "bt_navigator"
      - "velocity_smoother"
    bond_timeout: 4.0                  # Seconds before declaring a node dead
    attempt_respawn_reconnection: true
    bond_respawn_max_duration: 10.0
```

The lifecycle manager ensures all Nav2 nodes start in the correct order and
monitors their health, restarting them if they crash.

---

## 9. Navigation Actions

Nav2 provides three main ways to tell the robot where to go:

### NavigateToPose

Send the robot to a single goal pose.

```python
# Python example using nav2_simple_commander
from nav2_simple_commander.robot_navigator import BasicNavigator
from geometry_msgs.msg import PoseStamped

navigator = BasicNavigator()
navigator.waitUntilNav2Active()

goal = PoseStamped()
goal.header.frame_id = 'map'
goal.header.stamp = navigator.get_clock().now().to_msg()
goal.pose.position.x = 2.0
goal.pose.position.y = 1.0
goal.pose.orientation.w = 1.0

navigator.goToPose(goal)

while not navigator.isTaskComplete():
    feedback = navigator.getFeedback()
    # feedback.distance_remaining, feedback.estimated_time_remaining
```

### NavigateThroughPoses

Send the robot through a sequence of poses (it doesn't stop at intermediate poses).

```python
poses = [make_pose(1.0, 0.0), make_pose(2.0, 1.0), make_pose(3.0, 0.0)]
navigator.goThroughPoses(poses)
```

### FollowWaypoints

Send the robot to visit each waypoint, stopping briefly at each one. Useful for
inspection scenarios where you want to take a photo at each point.

```python
waypoints = [make_pose(1.0, 0.0), make_pose(2.0, 1.0), make_pose(3.0, 0.0)]
navigator.followWaypoints(waypoints)
```

**Which to use for inspection tasks:** `FollowWaypoints` is ideal because you typically
want the robot to stop at each inspection point to capture data.

---

## 10. Configuration Parameter Reference

These are the most commonly tuned parameters. Not exhaustive -- see Nav2 documentation for all.

### Speed and acceleration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_vel_x` | 0.26 | Maximum forward speed (m/s) |
| `max_vel_theta` | 1.0 | Maximum rotation speed (rad/s) |
| `min_vel_x` | 0.0 | Minimum forward speed |
| `acc_lim_x` | 2.5 | Forward acceleration limit (m/s^2) |
| `acc_lim_theta` | 3.2 | Rotational acceleration limit (rad/s^2) |

### Goal tolerance

| Parameter | Default | Description |
|-----------|---------|-------------|
| `xy_goal_tolerance` | 0.25 | Position tolerance at goal (meters) |
| `yaw_goal_tolerance` | 0.25 | Orientation tolerance at goal (radians) |
| `stateful` | true | Latch tolerance once reached |

### Costmap

| Parameter | Default | Description |
|-----------|---------|-------------|
| `resolution` | 0.05 | Cell size in meters |
| `inflation_radius` | 0.55 | Inflation distance (meters) |
| `cost_scaling_factor` | 10.0 | Cost decay steepness |
| `robot_radius` | 0.1 | Robot radius for circular footprint |
| `update_frequency` | 5.0 | Costmap update rate (Hz) |

### Controller

| Parameter | Default | Description |
|-----------|---------|-------------|
| `controller_frequency` | 20.0 | Velocity command rate (Hz) |
| `min_x_velocity_threshold` | 0.001 | Below this, consider stopped |
| `min_theta_velocity_threshold` | 0.001 | Below this, consider not rotating |

---

## 11. Complete Example: Nav2 Params for a Tracked Robot

This is a complete Nav2 parameters file for a tracked/skid-steer robot suitable for
confined-space inspection or indoor exploration.

```yaml
# File: config/nav2_params.yaml
# Robot: Tracked/skid-steer, ~30cm wide, LiDAR + optional depth camera
# Environment: Indoor / confined spaces (tunnels, narrow corridors)

amcl:
  ros__parameters:
    use_sim_time: false
    alpha1: 0.2                        # Rotation noise from rotation
    alpha2: 0.2                        # Rotation noise from translation
    alpha3: 0.2                        # Translation noise from translation
    alpha4: 0.2                        # Translation noise from rotation
    alpha5: 0.2                        # Translation noise (omnidirectional)
    base_frame_id: "base_link"
    beam_skip_distance: 0.5
    beam_skip_error_threshold: 0.9
    beam_skip_threshold: 0.3
    do_beams_skip: false
    global_frame_id: "map"
    lambda_short: 0.1
    laser_likelihood_max_dist: 2.0
    laser_max_range: 12.0
    laser_min_range: 0.1
    laser_model_type: "likelihood_field"
    max_beams: 60
    max_particles: 2000
    min_particles: 500
    odom_frame_id: "odom"
    pf_err: 0.05
    pf_z: 0.99
    recovery_alpha_fast: 0.1
    recovery_alpha_slow: 0.001
    resample_interval: 1
    robot_model_type: "nav2_amcl::DifferentialMotionModel"
    save_pose_rate: 0.5
    sigma_hit: 0.2
    tf_broadcast: true
    transform_tolerance: 1.0
    update_min_a: 0.2
    update_min_d: 0.25
    z_hit: 0.5
    z_max: 0.05
    z_rand: 0.5
    z_short: 0.05
    scan_topic: scan

bt_navigator:
  ros__parameters:
    use_sim_time: false
    global_frame: map
    robot_base_frame: base_link
    odom_topic: /odom
    bt_loop_duration: 10
    default_server_timeout: 20
    navigators: ["navigate_to_pose", "navigate_through_poses"]
    navigate_to_pose:
      plugin: "nav2_bt_navigator/NavigateToPoseNavigator"
    navigate_through_poses:
      plugin: "nav2_bt_navigator/NavigateThroughPosesNavigator"

planner_server:
  ros__parameters:
    planner_plugins: ["GridBased"]
    use_sim_time: false
    GridBased:
      plugin: "nav2_smac_planner/SmacPlanner2D"
      tolerance: 0.25
      max_iterations: 1000000
      allow_unknown: true
      max_on_approach_iterations: 1000
      cost_travel_multiplier: 2.0

controller_server:
  ros__parameters:
    use_sim_time: false
    controller_frequency: 20.0
    min_x_velocity_threshold: 0.001
    min_y_velocity_threshold: 0.5
    min_theta_velocity_threshold: 0.001
    progress_checker_plugins: ["progress_checker"]
    goal_checker_plugins: ["general_goal_checker"]
    controller_plugins: ["FollowPath"]
    progress_checker:
      plugin: "nav2_controller::SimpleProgressChecker"
      required_movement_radius: 0.5
      movement_time_allowance: 10.0
    general_goal_checker:
      plugin: "nav2_controller::SimpleGoalChecker"
      stateful: true
      xy_goal_tolerance: 0.10
      yaw_goal_tolerance: 0.15
    FollowPath:
      plugin: "nav2_regulated_pure_pursuit_controller::RegulatedPurePursuitController"
      desired_linear_vel: 0.25
      lookahead_dist: 0.6
      min_lookahead_dist: 0.3
      max_lookahead_dist: 0.9
      lookahead_time: 1.5
      rotate_to_heading_angular_vel: 0.8
      transform_tolerance: 0.1
      use_velocity_scaled_lookahead_dist: true
      min_approach_linear_velocity: 0.05
      approach_velocity_scaling_dist: 0.6
      use_collision_detection: true
      max_allowed_time_to_collision_up_to_carrot: 1.0
      use_regulated_linear_velocity_scaling: true
      use_cost_regulated_linear_velocity_scaling: false
      regulated_linear_scaling_min_radius: 0.9
      regulated_linear_scaling_min_speed: 0.15
      allow_reversing: false
      max_angular_accel: 2.5
      max_robot_pose_search_dist: 10.0

behavior_server:
  ros__parameters:
    costmap_topic: local_costmap/costmap_raw
    footprint_topic: local_costmap/published_footprint
    cycle_frequency: 10.0
    behavior_plugins: ["spin", "backup", "drive_on_heading", "wait"]
    spin:
      plugin: "nav2_behaviors/Spin"
    backup:
      plugin: "nav2_behaviors/BackUp"
    drive_on_heading:
      plugin: "nav2_behaviors/DriveOnHeading"
    wait:
      plugin: "nav2_behaviors/Wait"
    global_frame: odom
    robot_base_frame: base_link
    transform_tolerance: 0.1
    simulate_ahead_time: 2.0
    max_rotational_vel: 0.8
    min_rotational_vel: 0.3
    rotational_acc_lim: 2.5

velocity_smoother:
  ros__parameters:
    use_sim_time: false
    smoothing_frequency: 20.0
    scale_velocities: false
    feedback: "OPEN_LOOP"
    max_velocity: [0.25, 0.0, 0.8]
    min_velocity: [-0.25, 0.0, -0.8]
    max_accel: [2.0, 0.0, 2.5]
    max_decel: [-2.0, 0.0, -2.5]
    odom_topic: "odom"
    odom_duration: 0.1
    deadband_velocity: [0.0, 0.0, 0.0]

local_costmap:
  local_costmap:
    ros__parameters:
      update_frequency: 5.0
      publish_frequency: 2.0
      global_frame: odom
      robot_base_frame: base_link
      use_sim_time: false
      rolling_window: true
      width: 3
      height: 3
      resolution: 0.05
      robot_radius: 0.15
      plugins: ["obstacle_layer", "inflation_layer"]
      obstacle_layer:
        plugin: "nav2_costmap_2d::ObstacleLayer"
        enabled: true
        observation_sources: scan
        scan:
          topic: /scan
          max_obstacle_height: 2.0
          clearing: true
          marking: true
          data_type: "LaserScan"
          raytrace_max_range: 3.0
          raytrace_min_range: 0.0
          obstacle_max_range: 2.5
          obstacle_min_range: 0.0
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 5.0
        inflation_radius: 0.25

global_costmap:
  global_costmap:
    ros__parameters:
      update_frequency: 1.0
      publish_frequency: 1.0
      global_frame: map
      robot_base_frame: base_link
      use_sim_time: false
      robot_radius: 0.15
      resolution: 0.05
      track_unknown_space: true
      plugins: ["static_layer", "obstacle_layer", "inflation_layer"]
      static_layer:
        plugin: "nav2_costmap_2d::StaticLayer"
        map_subscribe_transactional: true
      obstacle_layer:
        plugin: "nav2_costmap_2d::ObstacleLayer"
        enabled: true
        observation_sources: scan
        scan:
          topic: /scan
          max_obstacle_height: 2.0
          clearing: true
          marking: true
          data_type: "LaserScan"
          raytrace_max_range: 5.0
          raytrace_min_range: 0.0
          obstacle_max_range: 4.5
          obstacle_min_range: 0.0
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 5.0
        inflation_radius: 0.25

map_server:
  ros__parameters:
    use_sim_time: false
    yaml_filename: ""                  # Set via launch argument

lifecycle_manager:
  ros__parameters:
    use_sim_time: false
    autostart: true
    node_names:
      - "map_server"
      - "amcl"
      - "controller_server"
      - "planner_server"
      - "behavior_server"
      - "bt_navigator"
      - "velocity_smoother"
    bond_timeout: 4.0
    attempt_respawn_reconnection: true
    bond_respawn_max_duration: 10.0
```
