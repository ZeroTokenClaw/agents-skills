# Confined Spaces Navigation Reference

## Table of Contents

1. [Narrow Passage Navigation Challenges](#1-narrow-passage-navigation-challenges)
2. [Costmap Configuration for Tight Spaces](#2-costmap-configuration-for-tight-spaces)
3. [Corridor-Following Algorithms](#3-corridor-following-algorithms)
4. [Junction Detection and Decision-Making](#4-junction-detection-and-decision-making)
5. [Inspection Pattern Planning](#5-inspection-pattern-planning)
6. [Waypoint Generation for Environment Graphs](#6-waypoint-generation-for-environment-graphs)
7. [Dealing with Limited Sensor FoV in Confined Spaces](#7-dealing-with-limited-sensor-fov-in-confined-spaces)
8. [Recovery Strategies in Confined Spaces](#8-recovery-strategies-in-confined-spaces)
9. [Integration with Inspection Workflow](#9-integration-with-inspection-workflow)
10. [Complete Example: Nav2 Config for Confined-Space Navigation](#10-complete-example-nav2-config-for-confined-space-navigation)

---

## 1. Narrow Passage Navigation Challenges

Navigating tunnels, narrow corridors, and confined spaces is fundamentally different from
navigating open environments. Standard Nav2 defaults will not work -- they're tuned for
offices and warehouses, not narrow passages (e.g., tunnels, mines, utility corridors).

### What makes confined spaces hard

| Challenge | Why It's Hard | Impact on Navigation |
|-----------|--------------|---------------------|
| Very tight clearance | Robot is 60-80% of passage width | Inflation must be minimal |
| Uniform appearance | All walls look the same to sensors | SLAM struggles with loop closure |
| No room to rotate | Can't spin 360 for recovery | Standard recovery behaviors fail |
| Limited sensor FoV | Walls very close, sensors can't see far | Costmap has small useful range |
| Curved passages | Constant curvature, no straight segments | Path following must be smooth |
| Junctions | T-intersections, Y-branches | Need systematic exploration strategy |
| Dead ends | Hit a wall, must reverse out | Need reliable reverse navigation |
| Water/debris | Partial passage blockage | Dynamic obstacles in tight spaces |
| GPS denied | No global reference signal | Must rely entirely on SLAM + odometry |

### Key principle: everything gets tighter

In open environments, you have margin for error. In confined spaces, every parameter matters:
- Inflation that's 5cm too wide means the planner can't find any path
- Speed that's 10% too fast means you hit a wall on a curve
- Odometry that drifts 2% means you're lost after 50 meters

---

## 2. Costmap Configuration for Tight Spaces

The costmap configuration is the most critical piece for confined space navigation.

### Inflation: as small as possible

```yaml
# Global costmap -- for path planning through the environment
global_costmap:
  global_costmap:
    ros__parameters:
      robot_radius: 0.12
      resolution: 0.025                # 2.5cm cells (finer than normal)
      update_frequency: 2.0
      publish_frequency: 1.0
      global_frame: map
      robot_base_frame: base_link
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
          raytrace_max_range: 3.0
          raytrace_min_range: 0.0
          obstacle_max_range: 2.5
          obstacle_min_range: 0.0
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 15.0      # VERY steep dropoff
        inflation_radius: 0.14         # Just barely more than robot_radius

# Local costmap -- small rolling window for obstacle avoidance
local_costmap:
  local_costmap:
    ros__parameters:
      robot_radius: 0.12
      resolution: 0.025               # Match global costmap resolution
      update_frequency: 10.0          # Fast updates for close obstacles
      publish_frequency: 5.0
      global_frame: odom
      robot_base_frame: base_link
      rolling_window: true
      width: 2                         # 2m x 2m (passages are small)
      height: 2
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
          raytrace_max_range: 2.0      # Short range (close walls)
          raytrace_min_range: 0.0
          obstacle_max_range: 1.5
          obstacle_min_range: 0.0
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 15.0
        inflation_radius: 0.14
```

### Why `cost_scaling_factor` matters here

With `cost_scaling_factor: 15.0`, the cost drops off very steeply:
- At robot_radius: LETHAL (collision)
- At robot_radius + 1cm: cost drops to ~50%
- At robot_radius + 2cm: cost drops to ~10%
- At inflation_radius: cost is near zero

This lets the planner find paths through narrow passages because the "penalty zone"
is very thin. With a normal `cost_scaling_factor: 3.0`, the cost would spread out
and the planner would think the whole corridor is dangerous.

---

## 3. Corridor-Following Algorithms

### Wall following

Wall following is a simple, robust strategy for corridor and tunnel navigation: keep a
fixed distance from one wall and follow it.

**Implementation approach using Nav2:**

Rather than implementing wall following from scratch, use Nav2's costmap and controller
with modified parameters that naturally center the robot:

```yaml
# The inflation layer with symmetric costs naturally centers the robot
# between two walls. High cost_scaling_factor ensures the "center channel"
# is clearly the lowest-cost path.
inflation_layer:
  cost_scaling_factor: 15.0
  inflation_radius: 0.14
```

For explicit wall following (e.g., in partially obstructed passages), you can create a
custom controller plugin or a simple ROS 2 node:

```python
# Simplified wall-following concept using LiDAR
# This is a ROS 2 node that publishes cmd_vel based on wall distance

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import numpy as np

class WallFollower(Node):
    def __init__(self):
        super().__init__('wall_follower')
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.scan_sub = self.create_subscription(LaserScan, '/scan', self.scan_cb, 10)
        self.target_wall_distance = 0.20  # meters from wall
        self.forward_speed = 0.15         # m/s

    def scan_cb(self, msg):
        ranges = np.array(msg.ranges)
        angles = np.linspace(msg.angle_min, msg.angle_max, len(ranges))

        # Get distances to left and right walls
        right_mask = (angles > -1.57) & (angles < -0.78)  # -90 to -45 degrees
        left_mask = (angles > 0.78) & (angles < 1.57)     # 45 to 90 degrees
        front_mask = (angles > -0.39) & (angles < 0.39)   # -22 to 22 degrees

        right_dist = np.nanmean(ranges[right_mask]) if np.any(right_mask) else 1.0
        left_dist = np.nanmean(ranges[left_mask]) if np.any(left_mask) else 1.0
        front_dist = np.nanmin(ranges[front_mask]) if np.any(front_mask) else 1.0

        cmd = Twist()

        # If obstacle ahead, rotate toward more open side
        if front_dist < 0.3:
            cmd.linear.x = 0.0
            cmd.angular.z = 0.5 if left_dist > right_dist else -0.5
        else:
            cmd.linear.x = self.forward_speed
            # Steer to center between walls
            error = left_dist - right_dist
            cmd.angular.z = 0.5 * error  # P-controller for centering

        self.cmd_pub.publish(cmd)
```

### Corridor centering

Nav2's inflation layer naturally centers the robot between walls when `cost_scaling_factor`
is high. The cost landscape creates a "valley" in the center of corridors.

For better centering, use the `KeepOut` filter or add a custom costmap layer that
adds extra cost near walls.

---

## 4. Junction Detection and Decision-Making

When the robot reaches a junction (T-intersection, Y-branch) in a waypoint network, it
needs to decide which way to go.

### Detecting junctions from LiDAR data

A junction appears in LiDAR as a sudden increase in range in one or more directions
(the passage opens up):

```python
def detect_junction(scan_msg, passage_radius=0.15):
    """Detect if the robot is at a junction based on LiDAR scan."""
    ranges = np.array(scan_msg.ranges)
    angles = np.linspace(scan_msg.angle_min, scan_msg.angle_max, len(ranges))

    # Normal corridor: most readings are close (within 2x passage radius)
    # Junction: some readings are much further (opening to another passage)
    normal_range = passage_radius * 2.5
    far_readings = ranges > normal_range

    if np.sum(far_readings) < 5:
        return None  # Not a junction

    # Find clusters of far readings (each cluster = an opening)
    openings = []
    in_opening = False
    start_angle = 0

    for i, is_far in enumerate(far_readings):
        if is_far and not in_opening:
            in_opening = True
            start_angle = angles[i]
        elif not is_far and in_opening:
            in_opening = False
            end_angle = angles[i]
            center_angle = (start_angle + end_angle) / 2
            openings.append(center_angle)

    return openings  # List of angles where passages branch off
```

### Decision strategy at junctions

| Strategy | How It Works | Best For |
|----------|-------------|----------|
| **Right-hand rule** | Always take the rightmost opening | Simple, guarantees coverage in connected environments |
| **Left-hand rule** | Always take the leftmost opening | Same guarantee, different path |
| **Closest to heading** | Take the opening closest to current heading | Follows the "main" corridor |
| **Priority queue** | Mark all openings, visit by priority | Systematic coverage of large environments |
| **Frontier-based** | Visit unexplored openings first | Efficient exploration |

For systematic inspection, a **priority queue** approach is recommended:
1. At each junction, record all openings
2. Enter the most promising one (e.g., straight ahead)
3. When that branch is complete, backtrack to the junction
4. Take the next unexplored opening
5. Repeat until all branches are explored

---

## 5. Inspection Pattern Planning

### Coverage patterns

| Pattern | Use Case | How It Works |
|---------|----------|-------------|
| **Linear traverse** | Straight corridor sections | Drive forward at constant speed, inspect walls |
| **Stop-and-inspect** | Specific defect locations | Navigate to point, stop, capture data, move on |
| **Spiral** | Large chambers (junctions, open areas) | Spiral outward from center to cover all surfaces |
| **Lawn mower** | Wide rectangular spaces | Back-and-forth parallel passes |
| **Section-based** | Long corridors | Divide into sections, inspect each methodically |

### Stop-and-inspect pattern

The most common pattern for inspection tasks. Space inspection points evenly:

```python
def generate_inspection_waypoints(segment_start, segment_end, spacing=1.0):
    """Generate evenly spaced inspection waypoints along a corridor segment."""
    import numpy as np
    from geometry_msgs.msg import PoseStamped

    start = np.array([segment_start.x, segment_start.y])
    end = np.array([segment_end.x, segment_end.y])
    direction = end - start
    length = np.linalg.norm(direction)
    direction_normalized = direction / length

    num_points = int(length / spacing) + 1
    waypoints = []

    for i in range(num_points):
        point = start + direction_normalized * (i * spacing)
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.pose.position.x = float(point[0])
        pose.pose.position.y = float(point[1])
        # Orient along corridor direction
        angle = np.arctan2(direction[1], direction[0])
        pose.pose.orientation.z = np.sin(angle / 2)
        pose.pose.orientation.w = np.cos(angle / 2)
        waypoints.append(pose)

    return waypoints
```

---

## 6. Waypoint Generation for Environment Graphs

### Representing environments as graphs

A confined-space environment is naturally a graph: corridors are edges, junctions/waypoints
are nodes. This applies to tunnel networks, warehouse aisles, mine shafts, and similar
environments.

```python
import networkx as nx

# Build environment graph
network = nx.Graph()

# Add waypoint nodes with their coordinates
network.add_node('WP001', pos=(0.0, 0.0))
network.add_node('WP002', pos=(50.0, 0.0))
network.add_node('WP003', pos=(50.0, 30.0))
network.add_node('WP004', pos=(0.0, 30.0))

# Add corridor edges with their properties
network.add_edge('WP001', 'WP002', length=50.0, width=0.30, surface='concrete')
network.add_edge('WP002', 'WP003', length=30.0, width=0.30, surface='concrete')
network.add_edge('WP003', 'WP004', length=50.0, width=0.25, surface='metal')
network.add_edge('WP004', 'WP001', length=30.0, width=0.25, surface='metal')

# Generate inspection tour (visit all edges)
# This is the "Chinese Postman Problem" -- visit every edge at least once
tour = nx.eulerian_circuit(network, source='WP001')
```

### Converting network tour to Nav2 waypoints

```python
def network_tour_to_waypoints(network, tour, inspection_spacing=1.0):
    """Convert a network tour into Nav2 waypoints."""
    all_waypoints = []

    for edge_start, edge_end in tour:
        start_pos = network.nodes[edge_start]['pos']
        end_pos = network.nodes[edge_end]['pos']

        # Generate inspection waypoints along this corridor segment
        segment_waypoints = generate_inspection_waypoints(
            start_pos, end_pos, spacing=inspection_spacing
        )
        all_waypoints.extend(segment_waypoints)

    return all_waypoints
```

---

## 7. Dealing with Limited Sensor FoV in Confined Spaces

### Problem: walls are too close

In a 300mm-wide passage with a 240mm robot, the walls are only 30mm from the sensors.
Most LiDARs have a minimum range of 100-200mm, meaning readings from very close
walls may be invalid.

### Solutions

| Solution | How | Trade-off |
|----------|-----|-----------|
| Use LiDAR with short min range | RPLiDAR A1 (0.15m min), LD19 (0.12m min) | Limited options, may still be too far |
| Use ultrasonic sensors | HC-SR04 (2cm min range) | Low resolution, slow update rate |
| Use infrared distance sensors | Sharp GP2Y0A21YK0F (10cm-80cm) | Simple, reliable for wall distance |
| Combine LiDAR + short-range sensors | LiDAR for mapping, IR/ultrasonic for close walls | More complex, but robust |
| Reduce costmap resolution | 1-2cm cells to capture small clearances | Higher CPU, more memory |

### Sensor mounting for narrow passages

```
     Top of passage
    ╭────────────────╮
    │   ← LiDAR →   │    LiDAR: mounted low, scans horizontal plane
    │                │    Gives wall distances for costmap
    │    [Robot]     │
    │   ← IR  IR →  │    IR sensors: left/right, very close range
    │                │    Backup for wall distance when LiDAR min range
    ╰────────────────╯    is too long
     Bottom of passage
```

### Costmap configuration for limited FoV

```yaml
obstacle_layer:
  observation_sources: scan ir_left ir_right
  scan:
    topic: /scan
    data_type: "LaserScan"
    marking: true
    clearing: true
    obstacle_min_range: 0.12          # LiDAR minimum range
    obstacle_max_range: 2.0
    raytrace_max_range: 2.5
  ir_left:
    topic: /ir_left/range
    data_type: "Range"
    marking: true
    clearing: false                    # IR doesn't clear (narrow FoV)
    obstacle_max_range: 0.30
    obstacle_min_range: 0.02
  ir_right:
    topic: /ir_right/range
    data_type: "Range"
    marking: true
    clearing: false
    obstacle_max_range: 0.30
    obstacle_min_range: 0.02
```

---

## 8. Recovery Strategies in Confined Spaces

Standard Nav2 recovery behaviors (spin, backup, wait) don't all work in confined spaces:

| Standard Recovery | Works in Confined Space? | Alternative |
|-------------------|---------------|-------------|
| **Spin** | NO -- can't rotate 360 | Skip or use partial rotation (45-90 deg) |
| **BackUp** | YES -- essential | Keep, increase backup distance |
| **Wait** | SOMETIMES -- no dynamic obstacles | Keep for brief pauses |
| **ClearCostmap** | YES -- phantom obstacles common | Keep, increase frequency |

### Custom confined-space recovery behavior tree

```xml
<RecoveryNode number_of_retries="5" name="confined_space_navigation_recovery">
  <!-- Try navigation -->
  <PipelineSequence name="navigate">
    <RateController hz="2.0">
      <Action ID="ComputePathToPose" goal="{goal}" path="{path}"/>
    </RateController>
    <Action ID="FollowPath" path="{path}"/>
  </PipelineSequence>

  <!-- Confined-space recovery sequence -->
  <Sequence name="confined_space_recovery">
    <!-- Step 1: Clear costmaps (phantom obstacles from environmental noise, etc.) -->
    <Action ID="ClearEntireCostmap" name="clear_local"
            service_name="/local_costmap/clear_entirely_local_costmap"/>

    <!-- Step 2: Wait briefly (let dust settle, debris move) -->
    <Action ID="Wait" wait_duration="2"/>

    <!-- Step 3: Back up (the most useful recovery in confined spaces) -->
    <Action ID="BackUp" backup_dist="0.3" backup_speed="0.08"/>

    <!-- Step 4: Clear costmap again after backup -->
    <Action ID="ClearEntireCostmap" name="clear_local_2"
            service_name="/local_costmap/clear_entirely_local_costmap"/>

    <!-- Step 5: Small rotation to rescan (not full spin) -->
    <Action ID="Spin" spin_dist="0.78"/>  <!-- 45 degrees only -->
  </Sequence>
</RecoveryNode>
```

### Reverse navigation (exiting a dead end)

When the robot hits a dead end, it needs to reverse all the way back to the last junction.
This requires either:

1. **Allow reversing in controller:**
   ```yaml
   FollowPath:
     allow_reversing: true
     min_vel_x: -0.15     # Allow reverse at 0.15 m/s
   ```

2. **Store breadcrumbs and navigate back:**
   ```python
   # Record poses as the robot drives forward
   # When dead end detected, reverse the list and navigate back
   breadcrumbs = []  # List of PoseStamped

   def on_pose_update(pose_msg):
       breadcrumbs.append(pose_msg)

   def reverse_to_junction():
       reversed_path = list(reversed(breadcrumbs))
       # Flip orientations 180 degrees for reverse navigation
       for pose in reversed_path:
           q = pose.pose.orientation
           # Rotate quaternion 180 degrees around Z
           pose.pose.orientation.z = -q.z  # Simplified; use proper quaternion math
           pose.pose.orientation.w = -q.w
       navigator.goThroughPoses(reversed_path)
   ```

---

## 9. Integration with Inspection Workflow

### Complete inspection pipeline

```
Mission Planning          Robot Navigation           Data Collection
+----------------+       +------------------+       +------------------+
| 1. Load env    |       | 3. SLAM mapping  |       | 5. Photo/video   |
|    graph       |------>|    (first visit)  |       |    at waypoints  |
|                |       |                  |       |                  |
| 2. Generate    |       | 4. Nav2 waypoint |------>| 6. Defect        |
|    waypoints   |       |    following     |       |    detection     |
|                |       |                  |       |                  |
|                |       |                  |       | 7. Report        |
|                |       |                  |       |    generation    |
+----------------+       +------------------+       +------------------+
```

### ROS 2 node architecture for an inspection system

```
mission_planner (Python)
├── Publishes: /inspection/waypoints (PoseArray)
├── Subscribes: /inspection/status (InspectionStatus)
└── Service: /inspection/start, /inspection/pause, /inspection/abort

nav2_waypoint_follower (C++)
├── Action: /follow_waypoints
├── Uses: Nav2 stack for navigation
└── Calls: waypoint_task_executor at each waypoint

inspection_data_collector (Python)
├── Subscribes: /camera/image_raw
├── Subscribes: /scan
├── Service: /camera/capture
└── Publishes: /inspection/status

defect_detector (Python)
├── Subscribes: /camera/image_raw
├── Uses: Computer vision / ML model
└── Publishes: /inspection/defects
```

### Launch file structure

```python
# File: launch/inspection.launch.py
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Robot hardware drivers
        IncludeLaunchDescription('my_robot_bringup/robot.launch.py'),

        # SLAM or localization
        IncludeLaunchDescription('slam_toolbox/online_async_launch.py',
            launch_arguments={'slam_params_file': 'config/slam_params.yaml'}.items()),

        # Nav2 navigation stack
        IncludeLaunchDescription('nav2_bringup/bringup_launch.py',
            launch_arguments={
                'params_file': 'config/nav2_confined_space_params.yaml',
                'map': '',  # Empty for SLAM mode; set path for localization
            }.items()),

        # Sensor fusion (EKF)
        Node(package='robot_localization', executable='ekf_node',
             parameters=['config/ekf.yaml']),

        # Mission planner
        Node(package='inspection', executable='mission_planner',
             parameters=['config/inspection_mission.yaml']),

        # Data collector
        Node(package='inspection', executable='data_collector',
             parameters=[{'save_path': '/data/inspections/'}]),
    ])
```

---

## 10. Complete Example: Nav2 Config for Confined Space Navigation

This is a complete Nav2 configuration optimized for confined space navigation.
Copy this as your starting point and tune from here.

```yaml
# File: config/nav2_confined_space_params.yaml
# Optimized for: Tracked robot in 300-600mm wide confined passages
# Robot: ~240mm wide, 2D LiDAR, optional depth camera

amcl:
  ros__parameters:
    use_sim_time: false
    alpha1: 0.3                        # Higher noise (tracked robot slip)
    alpha2: 0.3
    alpha3: 0.3
    alpha4: 0.3
    alpha5: 0.3
    base_frame_id: "base_link"
    global_frame_id: "map"
    laser_likelihood_max_dist: 2.0
    laser_max_range: 4.0               # Short range for confined spaces
    laser_min_range: 0.1
    laser_model_type: "likelihood_field"
    max_beams: 60
    max_particles: 3000                # More particles (featureless environment)
    min_particles: 1000
    odom_frame_id: "odom"
    recovery_alpha_fast: 0.1
    recovery_alpha_slow: 0.001
    resample_interval: 1
    robot_model_type: "nav2_amcl::DifferentialMotionModel"
    tf_broadcast: true
    transform_tolerance: 1.0
    update_min_a: 0.15                 # Update more often in tight spaces
    update_min_d: 0.15
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
    # Uncomment to use custom confined space navigation BT:
    # default_nav_to_pose_bt_xml: "config/confined_space_navigation_bt.xml"

planner_server:
  ros__parameters:
    use_sim_time: false
    planner_plugins: ["GridBased"]
    GridBased:
      plugin: "nav2_smac_planner/SmacPlanner2D"
      tolerance: 0.15                  # Tight tolerance for confined spaces
      max_iterations: 1000000
      allow_unknown: false             # Don't plan through unknown in confined spaces
      max_on_approach_iterations: 1000
      cost_travel_multiplier: 3.0      # Strongly prefer center of corridor

controller_server:
  ros__parameters:
    use_sim_time: false
    controller_frequency: 20.0
    min_x_velocity_threshold: 0.001
    min_y_velocity_threshold: 0.5
    min_theta_velocity_threshold: 0.001
    progress_checker_plugins: ["progress_checker"]
    goal_checker_plugins: ["precise_goal_checker"]
    controller_plugins: ["FollowPath"]
    progress_checker:
      plugin: "nav2_controller::SimpleProgressChecker"
      required_movement_radius: 0.3    # Smaller radius (slow movement in tight spaces)
      movement_time_allowance: 15.0    # More time (slow speeds)
    precise_goal_checker:
      plugin: "nav2_controller::SimpleGoalChecker"
      stateful: true
      xy_goal_tolerance: 0.05         # 5cm precision for inspection points
      yaw_goal_tolerance: 0.10        # ~6 degrees for camera alignment
    FollowPath:
      plugin: "nav2_regulated_pure_pursuit_controller::RegulatedPurePursuitController"
      desired_linear_vel: 0.15        # Slow and steady in confined spaces
      lookahead_dist: 0.4             # Short lookahead (can't see far)
      min_lookahead_dist: 0.2
      max_lookahead_dist: 0.6
      lookahead_time: 1.5
      rotate_to_heading_angular_vel: 0.4   # Slow rotation (tight space)
      transform_tolerance: 0.1
      use_velocity_scaled_lookahead_dist: true
      min_approach_linear_velocity: 0.03
      approach_velocity_scaling_dist: 0.4
      use_collision_detection: true
      max_allowed_time_to_collision_up_to_carrot: 1.0
      use_regulated_linear_velocity_scaling: true
      use_cost_regulated_linear_velocity_scaling: true   # Slow down near walls
      regulated_linear_scaling_min_radius: 0.5
      regulated_linear_scaling_min_speed: 0.08
      allow_reversing: true            # IMPORTANT: need to back out of dead ends
      max_angular_accel: 1.5           # Gentle rotation
      max_robot_pose_search_dist: 5.0

behavior_server:
  ros__parameters:
    costmap_topic: local_costmap/costmap_raw
    footprint_topic: local_costmap/published_footprint
    cycle_frequency: 10.0
    behavior_plugins: ["backup", "drive_on_heading", "wait"]
    # Note: NO spin behavior (can't spin in confined spaces)
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
    max_rotational_vel: 0.4
    min_rotational_vel: 0.2
    rotational_acc_lim: 1.5

velocity_smoother:
  ros__parameters:
    use_sim_time: false
    smoothing_frequency: 20.0
    scale_velocities: false
    feedback: "OPEN_LOOP"
    max_velocity: [0.15, 0.0, 0.4]
    min_velocity: [-0.15, 0.0, -0.4]
    max_accel: [1.0, 0.0, 1.5]
    max_decel: [-1.0, 0.0, -1.5]
    odom_topic: "odom"
    odom_duration: 0.1
    deadband_velocity: [0.005, 0.005, 0.01]

local_costmap:
  local_costmap:
    ros__parameters:
      update_frequency: 10.0
      publish_frequency: 5.0
      global_frame: odom
      robot_base_frame: base_link
      use_sim_time: false
      rolling_window: true
      width: 2
      height: 2
      resolution: 0.025                # 2.5cm cells (fine for confined spaces)
      robot_radius: 0.12
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
          raytrace_max_range: 2.0
          raytrace_min_range: 0.0
          obstacle_max_range: 1.5
          obstacle_min_range: 0.0
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 15.0
        inflation_radius: 0.14

global_costmap:
  global_costmap:
    ros__parameters:
      update_frequency: 2.0
      publish_frequency: 1.0
      global_frame: map
      robot_base_frame: base_link
      use_sim_time: false
      robot_radius: 0.12
      resolution: 0.025
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
          raytrace_max_range: 3.0
          raytrace_min_range: 0.0
          obstacle_max_range: 2.5
          obstacle_min_range: 0.0
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 15.0
        inflation_radius: 0.14

map_server:
  ros__parameters:
    use_sim_time: false
    yaml_filename: ""

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
