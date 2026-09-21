# Navigation Tuning Reference

## Table of Contents

1. [Inflation Radius](#1-inflation-radius)
2. [Robot Footprint Configuration](#2-robot-footprint-configuration)
3. [Controller Frequency](#3-controller-frequency)
4. [Obstacle Sources Configuration](#4-obstacle-sources-configuration)
5. [Tracked/Skid-Steer Robot Specific Tuning](#5-trackedskid-steer-robot-specific-tuning)
6. [Speed Limits and Acceleration](#6-speed-limits-and-acceleration)
7. [Goal Tolerance Settings](#7-goal-tolerance-settings)
8. [Oscillation Detection and Prevention](#8-oscillation-detection-and-prevention)
9. [Tuning Workflow: Systematic Approach](#9-tuning-workflow-systematic-approach)
10. [Common Tuning Mistakes](#10-common-tuning-mistakes)
11. [Parameter Recipes](#11-parameter-recipes)

---

## 1. Inflation Radius

The inflation radius is the single most impactful navigation parameter. It controls how
far from obstacles the costmap "danger zone" extends, which directly affects whether the
robot drives close to walls or stays far away.

### What it means

```
  Wall:   ████████████████████████████
          ░░░░░░░░░░░░░░░░░░░░░░░░░░  <-- inflation_radius (lethal to inscribed)
          ░░░░░░░░░░░░░░░░░░░░░░░░░░  <-- cost drops off with distance
          ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒  <-- declining cost zone
                                        <-- free space (cost = 0)
```

- Inside `robot_radius` distance: **LETHAL** -- robot will collide
- Between `robot_radius` and `inflation_radius`: **INSCRIBED to declining cost**
- Beyond `inflation_radius`: **FREE** -- zero cost

### How to set it

| Environment | inflation_radius | cost_scaling_factor | Why |
|-------------|-----------------|---------------------|-----|
| Open office/warehouse | 0.4 - 0.6 m | 3.0 - 5.0 | Keep distance from obstacles |
| Narrow hallways | 0.2 - 0.3 m | 5.0 - 8.0 | Need to fit through doorways |
| Tunnels/confined spaces | 0.10 - 0.20 m | 8.0 - 15.0 | Very tight, must get close to walls |
| Outdoor / open field | 0.5 - 1.0 m | 2.0 - 3.0 | Lots of room, stay safe |

**Rule of thumb for inflation_radius:**
- Minimum: `robot_radius + 0.02` (bare minimum safety margin)
- Comfortable: `robot_radius + 0.10` (10cm safety buffer)
- Conservative: `robot_radius * 2.0` (double the robot size)

**Rule of thumb for cost_scaling_factor:**
- Low (1.0-3.0): Cost drops slowly. Robot stays far from obstacles. Good for open spaces.
- Medium (3.0-5.0): Balanced. Good default.
- High (5.0-15.0): Cost drops fast. Robot drives closer to obstacles. Needed for tight spaces.

### Testing inflation settings

```bash
# View the costmap in RViz:
# 1. Add a "Map" display
# 2. Set topic to /local_costmap/costmap
# 3. Set color scheme to "costmap"
# 4. Look at the colored zones around obstacles

# The gradient around obstacles shows your inflation:
# Red/purple = lethal/inscribed (robot would collide)
# Yellow/green = declining cost (robot avoids but can pass)
# Gray = free space
```

---

## 2. Robot Footprint Configuration

The robot footprint tells Nav2 the physical shape of your robot for collision checking.

### Circular footprint (simpler)

```yaml
robot_radius: 0.15    # meters -- radius of the smallest circle enclosing the robot
```

Use when your robot is roughly circular or when you want simpler computation.

### Polygon footprint (more accurate)

```yaml
# Specify corners of the robot footprint as [x, y] pairs
# Origin is the center of the robot (base_link)
# X is forward, Y is left
footprint: "[[0.20, 0.15], [0.20, -0.15], [-0.15, -0.15], [-0.15, 0.15]]"
```

This defines a rectangle 35cm long (20cm front + 15cm back) and 30cm wide.

### When to use which

| Robot Shape | Use | Why |
|-------------|-----|-----|
| Round robot | `robot_radius` | Exact match, faster computation |
| Square/rectangular tracked robot | `footprint` polygon | More accurate collision checking |
| Asymmetric robot (sensor boom, arm) | `footprint` polygon | Must account for all protrusions |
| Quick prototyping | `robot_radius` | Simpler, fewer things to get wrong |

### Measuring your footprint

```
        Front of robot
            ^ X
            |
     +------+------+
     |      |      |
     |   (origin)  | <-- base_link is here
     |      |      |
     +------+------+
            |
         Y <-+
```

Measure from the center of the robot (where `base_link` is) to each corner. Forward is +X,
left is +Y. Express in meters.

---

## 3. Controller Frequency

The controller frequency determines how often the controller computes and sends velocity
commands. Think of it as the "frame rate" of your robot's driving.

```yaml
controller_server:
  ros__parameters:
    controller_frequency: 20.0    # Hz
```

| Frequency | Effect | Use When |
|-----------|--------|----------|
| 5 Hz | Jerky motion, slow reaction to obstacles | Very low CPU (Raspberry Pi 3) |
| 10 Hz | Acceptable for slow robots | Low CPU budget |
| 20 Hz | Smooth motion, good default | Most robots |
| 50 Hz | Very smooth, fast obstacle reaction | Fast robots (>1 m/s) |
| 100 Hz | Diminishing returns, high CPU | Racing robots, aggressive maneuvers |

Higher frequency means smoother motion and faster reaction to obstacles, but costs more CPU.
20 Hz is sufficient for most robots; increase only for fast-moving platforms.

**Critical rule:** Controller frequency must be significantly higher than the robot's
speed divided by the resolution of obstacles you need to avoid. A robot at 0.3 m/s
with 20 Hz controller checks obstacles every 1.5 cm -- plenty of resolution.

---

## 4. Obstacle Sources Configuration

Obstacle sources tell the costmap where to get real-time obstacle information.

### LiDAR source

```yaml
obstacle_layer:
  observation_sources: scan
  scan:
    topic: /scan                      # Your LiDAR topic
    data_type: "LaserScan"
    marking: true                     # Add obstacles to costmap
    clearing: true                    # Clear obstacles by raycasting
    max_obstacle_height: 2.0          # Max height to consider
    min_obstacle_height: 0.0          # Min height (filter ground)
    obstacle_max_range: 4.0           # Only trust readings within this range
    obstacle_min_range: 0.0           # Ignore readings closer than this
    raytrace_max_range: 5.0           # Clear obstacles by raycasting up to this
    raytrace_min_range: 0.0           # Don't raytrace closer than this
    inf_is_valid: false               # Treat inf readings as max range (false = ignore)
```

### Depth camera source

```yaml
obstacle_layer:
  observation_sources: scan depth_camera
  depth_camera:
    topic: /depth_camera/points       # PointCloud2 from depth camera
    data_type: "PointCloud2"
    marking: true
    clearing: true
    max_obstacle_height: 1.5          # Above robot height
    min_obstacle_height: 0.05         # Filter ground plane
    obstacle_max_range: 3.0
    raytrace_max_range: 4.0
```

### Multiple sensors

You can combine multiple sensors. The costmap merges all of them:

```yaml
obstacle_layer:
  observation_sources: front_scan rear_scan depth
  front_scan:
    topic: /front_lidar/scan
    # ... config ...
  rear_scan:
    topic: /rear_lidar/scan
    # ... config ...
  depth:
    topic: /depth_camera/points
    # ... config ...
```

### Tuning obstacle sources

| Problem | Parameter | Change |
|---------|-----------|--------|
| Phantom obstacles that persist | `clearing: true` | Ensure clearing is enabled |
| Obstacles not appearing | `marking: true` | Ensure marking is enabled |
| Ground plane shows as obstacle | `min_obstacle_height` | Increase (e.g., 0.05-0.10m) |
| Ceiling shows as obstacle | `max_obstacle_height` | Decrease to robot height |
| Noisy far-range readings | `obstacle_max_range` | Decrease to reliable sensor range |
| Costmap doesn't clear behind robot | `raytrace_max_range` | Increase to sensor max range |
| Too many points overwhelming costmap | `obstacle_max_range` | Decrease range |

---

## 5. Tracked/Skid-Steer Robot Specific Tuning

Tracked and skid-steer robots have unique challenges because they don't follow
ideal differential-drive kinematics. Wheels slip during turns, causing odometry errors
and unexpected motion.

### Key challenges

| Challenge | Impact | Mitigation |
|-----------|--------|------------|
| Wheel slip during rotation | Odometry over-reports rotation | Fuse IMU with wheel odom via `robot_localization` |
| Non-instantaneous rotation | Robot skids during turn-in-place | Set `min_vel_x: 0.0`, allow stopped rotation |
| Higher friction on hard floors | Robot struggles to rotate | Increase `max_vel_theta`, reduce rotation commands |
| Asymmetric slip (one track grips more) | Robot curves instead of going straight | Calibrate left/right track separately |

### robot_localization EKF for tracked robots

Essential for tracked robots -- fuse wheel odometry with an IMU to compensate for slip:

```yaml
# File: config/ekf.yaml
ekf_filter_node:
  ros__parameters:
    use_sim_time: false
    frequency: 50.0
    two_d_mode: true                   # Constrain to 2D ground plane
    publish_tf: true
    odom_frame: odom
    base_link_frame: base_link
    world_frame: odom

    # Wheel odometry
    odom0: /wheel_odom                 # Raw wheel odometry
    odom0_config: [true,  true,  false,  # x, y, z position
                   false, false, true,   # roll, pitch, yaw
                   true,  true,  false,  # vx, vy, vz
                   false, false, true,   # vroll, vpitch, vyaw
                   false, false, false]  # ax, ay, az
    odom0_differential: false

    # IMU (trust rotation more than wheels)
    imu0: /imu/data
    imu0_config: [false, false, false,   # Don't use IMU for position
                  true,  true,  true,    # Use IMU for orientation
                  false, false, false,   # Don't use for velocity
                  true,  true,  true,    # Use angular velocity
                  true,  true,  true]    # Use linear acceleration
    imu0_differential: false
    imu0_remove_gravitational_acceleration: true

    # Process noise -- increase for tracked robots (more slip)
    process_noise_covariance: [
      0.05, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0.05, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0.06, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0.03, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0.03, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0.06, 0, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0.025, 0, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0.025, 0, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0.04, 0, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0.01, 0, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.01, 0, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.02, 0, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.01, 0, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.01, 0,
      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.015
    ]
```

### Controller tuning for tracked robots

```yaml
# Regulated Pure Pursuit -- recommended for tracked robots
FollowPath:
  plugin: "nav2_regulated_pure_pursuit_controller::RegulatedPurePursuitController"
  desired_linear_vel: 0.25            # Conservative speed (tracks slip at high speed)
  lookahead_dist: 0.6                 # Look ahead 0.6m
  min_lookahead_dist: 0.3
  max_lookahead_dist: 0.9
  lookahead_time: 1.5
  rotate_to_heading_angular_vel: 0.6  # Slower rotation (tracks are imprecise)
  use_velocity_scaled_lookahead_dist: true
  min_approach_linear_velocity: 0.05
  use_regulated_linear_velocity_scaling: true
  regulated_linear_scaling_min_radius: 0.9  # Slow down on tight curves
  regulated_linear_scaling_min_speed: 0.15
  allow_reversing: false              # Disable unless you need it
  max_angular_accel: 2.0              # Lower than default (track inertia)
```

---

## 6. Speed Limits and Acceleration

### Setting speed limits

```yaml
# Maximum velocities
max_vel_x: 0.3          # m/s forward  (start conservative, increase later)
min_vel_x: -0.1         # m/s backward (negative = reverse)
max_vel_y: 0.0          # m/s lateral  (0 for differential/tracked)
max_vel_theta: 1.0       # rad/s rotation

# Acceleration limits
acc_lim_x: 2.0          # m/s^2 forward acceleration
acc_lim_theta: 2.5       # rad/s^2 rotational acceleration
decel_lim_x: -2.0       # m/s^2 braking (negative)
decel_lim_theta: -2.5    # rad/s^2 rotational braking
```

### Speed limit guidelines

| Robot Type | max_vel_x | max_vel_theta | Why |
|------------|-----------|---------------|-----|
| Confined-space inspection | 0.15 - 0.25 | 0.5 - 0.8 | Very confined, need precision |
| Indoor exploration | 0.3 - 0.5 | 1.0 - 1.5 | Moderate speed, stay safe |
| Warehouse robot | 0.5 - 1.0 | 1.5 - 2.0 | Open spaces, need throughput |
| Outdoor robot | 1.0 - 3.0 | 2.0 - 3.0 | Open terrain |

### Velocity smoother

The velocity smoother prevents jerky motion by limiting the rate of velocity change:

```yaml
velocity_smoother:
  ros__parameters:
    smoothing_frequency: 20.0
    scale_velocities: false
    feedback: "OPEN_LOOP"             # or "CLOSED_LOOP" if using odom feedback
    max_velocity: [0.3, 0.0, 1.0]    # [vx, vy, vtheta]
    min_velocity: [-0.1, 0.0, -1.0]
    max_accel: [2.0, 0.0, 2.5]       # [ax, ay, atheta]
    max_decel: [-2.0, 0.0, -2.5]
    odom_topic: "odom"
    odom_duration: 0.1
    deadband_velocity: [0.01, 0.01, 0.01]  # Ignore commands below this
```

---

## 7. Goal Tolerance Settings

Goal tolerance determines how close the robot needs to get to a goal before declaring success.

```yaml
general_goal_checker:
  plugin: "nav2_controller::SimpleGoalChecker"
  stateful: true                       # Once within tolerance, stay "reached" even if it drifts
  xy_goal_tolerance: 0.10             # meters from goal position
  yaw_goal_tolerance: 0.15            # radians from goal orientation (~8.6 degrees)
```

### Tolerance guidelines

| Scenario | xy_tolerance | yaw_tolerance | Why |
|----------|-------------|---------------|-----|
| Inspection (camera positioning) | 0.05 - 0.10 | 0.10 - 0.15 | Need precise camera aiming |
| General navigation | 0.15 - 0.25 | 0.20 - 0.30 | Don't need precision |
| Docking/charging | 0.02 - 0.05 | 0.05 - 0.10 | Must align precisely |
| Outdoor waypoints | 0.30 - 0.50 | 0.40 - 0.50 | GPS-level accuracy is fine |

### The `stateful` flag

When `stateful: true`, once the robot enters the tolerance zone, the goal is considered
reached even if the robot drifts back out slightly (e.g., due to deceleration overshoot).
This prevents the robot from oscillating at the goal.

**Always set `stateful: true`** unless you have a specific reason not to.

---

## 8. Oscillation Detection and Prevention

Oscillation is when the robot repeatedly switches direction, rocking back and forth
without making progress. It's one of the most common navigation problems.

### Causes of oscillation

| Cause | Symptom | Fix |
|-------|---------|-----|
| Goal tolerance too tight | Robot overshoots, corrects, overshoots again | Increase `xy_goal_tolerance` and `yaw_goal_tolerance` |
| Controller gains too high | Robot over-corrects on every cycle | Reduce path alignment/goal alignment scales |
| Speed too high for controller frequency | Robot can't react in time | Reduce `max_vel_x` or increase `controller_frequency` |
| Inflation pushing robot both ways | Robot in a corridor pinched by inflation from both walls | Reduce `inflation_radius` |
| Competing critics in DWB | PathAlign and GoalAlign pulling in opposite directions | Balance critic scales |

### Progress checker

The progress checker detects when the robot is stuck and triggers recovery:

```yaml
progress_checker:
  plugin: "nav2_controller::SimpleProgressChecker"
  required_movement_radius: 0.5       # Must move this far...
  movement_time_allowance: 10.0       # ...within this many seconds
```

If the robot doesn't move `required_movement_radius` meters within
`movement_time_allowance` seconds, it's considered stuck and recovery triggers.

### Anti-oscillation in DWB

```yaml
# DWB oscillation critic
critics: ["RotateToGoal", "Oscillation", "BaseObstacle", "GoalAlign",
          "PathAlign", "PathDist", "GoalDist"]
Oscillation.scale: 1.0                # Penalize direction changes
```

### Anti-oscillation in Regulated Pure Pursuit

Regulated Pure Pursuit is naturally less prone to oscillation because it uses a
lookahead point, which smooths out the control signal. If you're having oscillation
issues with DWB, switching to Regulated Pure Pursuit often fixes it.

---

## 9. Tuning Workflow: Systematic Approach

Do not tune parameters randomly. Follow this systematic workflow.

### Phase 1: Static setup (robot not moving)

1. **Verify TF tree**
   ```bash
   ros2 run tf2_tools view_frames
   # Must have: map -> odom -> base_link -> laser_frame
   ```

2. **Verify sensor data**
   ```bash
   ros2 topic hz /scan          # LiDAR publishing?
   ros2 topic hz /odom          # Odometry publishing?
   ros2 topic hz /imu/data      # IMU publishing (if used)?
   ```

3. **Check costmap in RViz**
   - Add Map display for `/local_costmap/costmap`
   - Robot should be in free space (not inside an obstacle)
   - Obstacles should match reality

### Phase 2: Basic motion (slow speed)

4. **Set conservative speeds**
   ```yaml
   max_vel_x: 0.15
   max_vel_theta: 0.5
   ```

5. **Set generous tolerances**
   ```yaml
   xy_goal_tolerance: 0.25
   yaw_goal_tolerance: 0.30
   ```

6. **Send a simple goal** -- navigate 1-2 meters in open space
   - Does it plan a path? If not: check inflation, costmap
   - Does it follow the path? If not: check controller, cmd_vel topic
   - Does it reach the goal? If not: check tolerances

### Phase 3: Obstacle avoidance

7. **Place an obstacle in the path** and navigate around it
   - Does the costmap show the obstacle? If not: check obstacle sources
   - Does the planner route around it? If not: check inflation, planner
   - Does the controller avoid it? If not: check local costmap

### Phase 4: Recovery behavior

8. **Intentionally get the robot stuck** (narrow doorway, blocked path)
   - Does recovery trigger? If not: check progress_checker settings
   - Does recovery succeed? If not: tune recovery behaviors

### Phase 5: Speed increase

9. **Gradually increase speed**
   ```yaml
   # Increase by 0.05-0.1 m/s at a time
   max_vel_x: 0.20  # then 0.25, then 0.30...
   ```
   - At each speed, verify obstacle avoidance still works
   - If robot starts oscillating: back off speed or tune controller

### Phase 6: Fine-tuning

10. **Adjust inflation for your environment**
    - Too conservative (robot won't go through doors): reduce inflation_radius
    - Too aggressive (robot hits walls): increase inflation_radius

11. **Adjust goal tolerance for your use case**
    - Inspection: tighten to 0.05-0.10m
    - General navigation: keep at 0.15-0.25m

---

## 10. Common Tuning Mistakes

| Mistake | Consequence | Correct Approach |
|---------|------------|------------------|
| Setting speeds too high initially | Robot crashes, hard to debug | Start at 0.15 m/s, increase gradually |
| Inflation radius too large | Robot can't fit through any doorway | Start at robot_radius + 0.05, increase if needed |
| Inflation radius too small | Robot grazes or hits obstacles | Must be >= robot_radius |
| Controller frequency too low | Robot can't react to obstacles | Use 20 Hz minimum |
| Ignoring odometry quality | Navigation works in sim, fails on real robot | Calibrate odometry, fuse with IMU |
| Tuning too many params at once | No idea what helped or hurt | Change ONE parameter at a time |
| Copying params from a different robot | Parameters don't match your hardware | Start from defaults, tune systematically |
| Not checking TF tree first | Hours wasted on "broken" navigation that's really a TF issue | ALWAYS verify TF first |
| Using voxel layer without need | Wastes CPU, adds complexity | Use obstacle_layer for 2D LiDAR |
| Setting `track_unknown_space: false` | Planner routes through unmapped areas into walls | Keep `true` unless you know your map is complete |

---

## 11. Parameter Recipes

### Recipe 1: Indoor tracked robot (confined-space inspection PoC)

```yaml
# Conservative, reliable, for confined spaces
robot_radius: 0.15
inflation_radius: 0.20
cost_scaling_factor: 8.0
max_vel_x: 0.20
max_vel_theta: 0.6
controller_frequency: 20.0
xy_goal_tolerance: 0.08
yaw_goal_tolerance: 0.12
# Planner: Smac 2D
# Controller: Regulated Pure Pursuit
```

### Recipe 2: Differential drive indoor robot

```yaml
# Balanced for office/warehouse environment
robot_radius: 0.18
inflation_radius: 0.35
cost_scaling_factor: 4.0
max_vel_x: 0.40
max_vel_theta: 1.2
controller_frequency: 20.0
xy_goal_tolerance: 0.15
yaw_goal_tolerance: 0.20
# Planner: NavFn (A*)
# Controller: DWB
```

### Recipe 3: Fast outdoor robot

```yaml
# For open terrain with few obstacles
robot_radius: 0.25
inflation_radius: 0.60
cost_scaling_factor: 3.0
max_vel_x: 1.0
max_vel_theta: 2.0
controller_frequency: 50.0
xy_goal_tolerance: 0.30
yaw_goal_tolerance: 0.30
# Planner: Theta*
# Controller: MPPI
```

### Recipe 4: Confined space / tunnel navigation

```yaml
# Absolute minimum inflation, slow and steady
robot_radius: 0.12
inflation_radius: 0.14
cost_scaling_factor: 15.0
max_vel_x: 0.15
max_vel_theta: 0.4
controller_frequency: 20.0
xy_goal_tolerance: 0.05
yaw_goal_tolerance: 0.10
# Planner: Smac 2D
# Controller: Regulated Pure Pursuit
# See confined-spaces.md for full config
```

### Recipe 5: Simulation / Gazebo testing

```yaml
# Slightly looser than real robot (sim has perfect odometry)
robot_radius: 0.15
inflation_radius: 0.30
cost_scaling_factor: 5.0
max_vel_x: 0.50
max_vel_theta: 1.5
controller_frequency: 20.0
xy_goal_tolerance: 0.15
yaw_goal_tolerance: 0.20
use_sim_time: true    # IMPORTANT: use sim time in Gazebo
# Any planner/controller combo works well in sim
```
