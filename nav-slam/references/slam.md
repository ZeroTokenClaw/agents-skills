# SLAM Reference

## Table of Contents

1. [What is SLAM](#1-what-is-slam)
2. [slam_toolbox Overview and Installation](#2-slam_toolbox-overview-and-installation)
3. [Online vs Async SLAM Modes](#3-online-vs-async-slam-modes)
4. [Configuration Parameters That Matter](#4-configuration-parameters-that-matter)
5. [Loop Closure](#5-loop-closure)
6. [Map Saving and Loading](#6-map-saving-and-loading)
7. [Map Quality Assessment](#7-map-quality-assessment)
8. [LiDAR-based vs Visual SLAM](#8-lidar-based-vs-visual-slam)
9. [Common SLAM Failures and Fixes](#9-common-slam-failures-and-fixes)
10. [Complete Example: slam_toolbox Config](#10-complete-example-slam_toolbox-config)

---

## 1. What is SLAM

**For software developers:** Imagine you're blindfolded in an unknown building with only a
laser tape measure. You need to simultaneously build a floor plan (the **map**) while tracking
where you are on that floor plan (your **location**). That's the chicken-and-egg problem SLAM
solves: you need a map to know where you are, and you need to know where you are to build a map.

**How it works at a high level:**

1. The robot takes a LiDAR scan (360-degree distance measurements)
2. It compares this scan to previous scans using **scan matching** (finding how the robot moved)
3. It stitches scans together into a growing map (an **occupancy grid**)
4. When it recognizes a place it has been before, it performs **loop closure** (correcting accumulated drift)

**The output:** An occupancy grid map -- a grayscale image where:
- White pixels = free space (the robot can go here)
- Black pixels = occupied (walls, obstacles)
- Gray pixels = unknown (not yet scanned)

---

## 2. slam_toolbox Overview and Installation

`slam_toolbox` is the standard SLAM package for ROS 2. It replaced `gmapping` and
`cartographer` as the recommended 2D SLAM solution.

### Installation

```bash
sudo apt install ros-${ROS_DISTRO}-slam-toolbox
```

### What slam_toolbox provides

- **Online synchronous SLAM** -- processes every scan, highest quality but slower
- **Online asynchronous SLAM** -- skips scans if processing is slow, good for real-time use
- **Localization mode** -- uses an existing map, just localizes (replaces AMCL for some use cases)
- **Lifelong mapping** -- continues updating a map over multiple sessions
- **Map serialization** -- saves/loads maps in its own format (plus standard PGM/YAML export)

### Required inputs

| Topic | Type | Description |
|-------|------|-------------|
| `/scan` | `sensor_msgs/LaserScan` | LiDAR data |
| `/tf` | Transform: `odom` --> `base_link` | Odometry transform |

### Published outputs

| Topic/TF | Type | Description |
|-----------|------|-------------|
| `/map` | `nav_msgs/OccupancyGrid` | The built map |
| TF: `map` --> `odom` | Transform | Corrects odometry drift |

---

## 3. Online vs Async SLAM Modes

### Online Asynchronous (recommended for most use cases)

```bash
ros2 launch slam_toolbox online_async_launch.py
```

- Processes scans in the background
- Won't block if scan processing takes longer than the scan rate
- Best for real-time robot operation
- Slight quality trade-off vs synchronous

### Online Synchronous

```bash
ros2 launch slam_toolbox online_sync_launch.py
```

- Processes every single scan
- Can slow down if CPU can't keep up
- Best quality maps
- Use when mapping offline or with a powerful computer

### When to use which

| Scenario | Mode | Why |
|----------|------|-----|
| Real-time mapping while driving | **Async** | Can't afford to slow down the robot |
| Careful mapping of a new environment | **Sync** | Want the best possible map quality |
| First inspection of a new environment | **Async** | Robot needs real-time responsiveness |
| Post-processing a rosbag recording | **Sync** | No real-time constraint, maximize quality |
| Localization on existing map | **Localization mode** | Don't need to build a new map |

### Localization mode

When you already have a map and just need to track the robot's position:

```bash
ros2 launch slam_toolbox localization_launch.py \
  map_file_name:=/path/to/your_map.posegraph
```

This is an alternative to AMCL. It uses scan matching instead of particle filters, which can
be more robust in featureless environments (like long straight corridors or tunnels).

---

## 4. Configuration Parameters That Matter

Most slam_toolbox parameters can be left at defaults. These are the ones you'll actually need to tune.

### Scan matching parameters

```yaml
slam_toolbox:
  ros__parameters:
    # How far the robot must move before processing a new scan
    minimum_travel_distance: 0.5      # meters (reduce for small/confined environments)
    minimum_travel_heading: 0.5       # radians (reduce for environments with lots of turns)

    # Scan matching quality
    resolution: 0.05                  # Map resolution in meters/pixel (0.05 = 5cm)
    max_laser_range: 12.0             # Max range to use from LiDAR (clip noisy far readings)

    # Search window for scan matching
    angle_variance_penalty: 1.0       # Penalize large rotation corrections
    distance_variance_penalty: 0.5    # Penalize large translation corrections
    fine_search_angle_offset: 0.00349 # Fine search angular range (radians)
    coarse_search_angle_offset: 0.349 # Coarse search angular range (radians)
    coarse_angle_resolution: 0.0349   # Coarse search step size
```

### When to change defaults

| Problem | Parameter to change | Direction |
|---------|-------------------|-----------|
| Map is blurry/low resolution | `resolution` | Decrease (e.g., 0.03) |
| Map building misses areas | `minimum_travel_distance` | Decrease (e.g., 0.2) |
| Map has duplicate walls | Scan matching failing | Decrease `max_laser_range`, check odometry |
| Too much CPU usage | `minimum_travel_distance` | Increase |
| Confined space/tunnel: not enough scans | `minimum_travel_distance` | Decrease to 0.1-0.2 |
| Large open area: scan matching fails | `max_laser_range` | Match your LiDAR's reliable range |

---

## 5. Loop Closure

### What is loop closure?

When the robot returns to a previously visited location, SLAM recognizes "I've been here before"
and corrects all the accumulated drift in the map. Without loop closure, maps of large
environments would be increasingly distorted.

**Why it matters:** Each scan adds a small position error. After hundreds of scans, the
cumulative error becomes significant. Loop closure detects that the current position matches
a previously visited location, then uses pose graph optimization to redistribute the error
across all poses, correcting the entire map.

### How slam_toolbox handles loop closure

1. **Scan matching** detects when current scan matches a previous location
2. **Pose graph optimization** adjusts all poses to minimize total error
3. The map is regenerated from corrected poses

### Loop closure parameters

```yaml
slam_toolbox:
  ros__parameters:
    # Loop closure search
    loop_search_maximum_distance: 3.0   # How far to search for loop closures (meters)
    do_loop_closing: true               # Enable/disable loop closure

    # Loop closure thresholds
    loop_match_minimum_chain_size: 10   # Minimum number of scans in a chain to consider
    loop_match_maximum_variance_coarse: 3.0   # Coarse match quality threshold
```

### Tips for good loop closures

- **Drive in loops** -- return to previously mapped areas from different directions
- **Avoid featureless corridors** -- long straight hallways look the same everywhere
- **Go slowly at revisited areas** -- give the scan matcher time to recognize the location
- **In confined spaces (tunnels, narrow corridors):** Loop closures are rare because you
  often can't loop back. Focus on good odometry and reduce `minimum_travel_distance` instead

---

## 6. Map Saving and Loading

### Saving maps

slam_toolbox has two map formats:

**1. Standard OccupancyGrid (PGM + YAML) -- for Nav2**

```bash
# Save using map_saver_cli (standard Nav2 tool)
ros2 run nav2_map_server map_saver_cli -f ~/maps/my_environment
# Creates: my_environment.pgm and my_environment.yaml
```

**2. Pose graph serialization -- for slam_toolbox**

```bash
# Save via service call (preserves full SLAM state for continued mapping)
ros2 service call /slam_toolbox/serialize_map slam_toolbox/srv/SerializePoseGraph \
  "{filename: '/home/user/maps/my_environment'}"
# Creates: my_environment.posegraph and my_environment.data
```

The pose graph format preserves the full SLAM state, allowing you to continue mapping later
or use slam_toolbox's localization mode. The PGM/YAML format is what Nav2's map_server uses.

**Save both** -- use PGM/YAML for navigation and pose graph for future SLAM sessions.

### Loading maps

**For navigation (Nav2):**

```yaml
# In your Nav2 params or launch file
map_server:
  ros__parameters:
    yaml_filename: "/home/user/maps/my_environment.yaml"
```

**For continued SLAM or localization:**

```bash
ros2 launch slam_toolbox localization_launch.py \
  map_file_name:=/home/user/maps/my_environment.posegraph
```

### map_server configuration

```yaml
map_server:
  ros__parameters:
    yaml_filename: ""                  # Set via launch argument
    topic_name: "map"
    frame_id: "map"
```

---

## 7. Map Quality Assessment

### How to tell if your map is good

**Visual inspection in RViz:**

| What to look for | Good | Bad |
|------------------|------|-----|
| Wall straightness | Walls are straight lines | Walls are wavy or doubled |
| Corner sharpness | Corners are clean 90-degree angles | Corners are rounded or split |
| Consistency | Revisited areas look identical | Revisited areas show ghosting/doubling |
| Coverage | All accessible areas are mapped | Gray (unknown) areas where you drove |
| Alignment | Features line up across the map | Features offset from each other |

**Quantitative checks:**

```bash
# Check map metadata
ros2 topic echo /map --once | head -20
# Look at: resolution, width, height, origin

# Check map update rate
ros2 topic hz /map
# Should be updating if SLAM is running
```

### Common map quality issues

| Issue | Appearance | Cause | Fix |
|-------|-----------|-------|-----|
| Double walls | Two parallel lines where one wall exists | Odometry drift without loop closure | Drive slower, ensure loop closures, calibrate odometry |
| Warped/bent walls | Straight walls appear curved | Cumulative odometry error | Better odometry calibration, more loop closures |
| Holes in walls | Gaps in walls that should be solid | LiDAR missed readings (glass, black surfaces) | Accept it -- some materials are invisible to LiDAR |
| Fuzzy/thick walls | Walls appear thick and blurry | Robot moving too fast during mapping | Drive slower, reduce `resolution` value |
| Ghost obstacles | Obstacles that don't exist in reality | Dynamic objects during mapping (people) | Re-map without moving objects, or edit map manually |
| Incomplete coverage | Large gray areas | Didn't drive everywhere | Drive through all areas, check LiDAR range coverage |

### Manually editing maps

The PGM file is just a grayscale image. You can edit it in GIMP or any image editor:
- Paint white (254) to mark free space
- Paint black (0) to mark obstacles
- Paint gray (205) to mark unknown
- Keep the same dimensions and don't change the YAML metadata

This is useful for removing ghost obstacles or adding walls for areas you can't scan.

---

## 8. LiDAR-based vs Visual SLAM

| Feature | LiDAR SLAM (slam_toolbox) | Visual SLAM (ORB-SLAM3, RTAB-Map) |
|---------|--------------------------|-----------------------------------|
| Sensor | 2D/3D LiDAR | Mono/stereo camera, RGB-D |
| Map type | 2D occupancy grid | 3D point cloud or octomap |
| Accuracy | Excellent for 2D | Good, but sensitive to lighting |
| Cost | LiDAR is expensive ($100-$2000+) | Cameras are cheap ($30-$200) |
| Robustness | Works in darkness, dust, smoke | Fails in low light, texture-less areas |
| CPU usage | Low-medium | High (feature extraction) |
| Best for | Indoor navigation, tunnels, confined spaces | 3D reconstruction, outdoor, AR |
| ROS 2 maturity | Excellent (slam_toolbox) | Good (RTAB-Map), moderate (ORB-SLAM3) |

**Recommendation for confined-space inspection:** Use LiDAR-based SLAM (slam_toolbox).
Tunnels, narrow corridors, and similar environments are often dark, dusty, and have
consistent geometry that works well with LiDAR. Camera-based SLAM would struggle with
lighting conditions and repetitive textures.

**Hybrid approach:** Use LiDAR for SLAM and navigation, cameras for visual inspection
(defect detection, condition assessment). Don't try to use the same sensor for both.

---

## 9. Common SLAM Failures and Fixes

| Failure | Symptoms | Cause | Fix |
|---------|----------|-------|-----|
| Map tearing | Map splits into disconnected pieces | Lost scan matching | Drive slower, reduce `minimum_travel_distance` |
| Map rotation | Entire map slowly rotates | IMU not fused, pure wheel odometry rotational error | Add IMU to odometry via `robot_localization` |
| No map generated | `/map` topic not publishing | TF tree broken, no `/scan` data | Check `ros2 topic list`, verify TF with `view_frames` |
| Map freezes | Map stops updating | slam_toolbox node crashed or scan matching diverged | Check node status, restart SLAM |
| Infinite corridors | Long hallways keep extending (never close) | Featureless environment, no loop closure triggers | Add distinctive features, or accept linear drift |
| Duplicate rooms | Same room appears twice in map | Failed loop closure | Increase `loop_search_maximum_distance`, drive overlap areas |
| Jittery map | Map constantly shifts/jitters | Noisy odometry or LiDAR data | Filter odometry with EKF, check LiDAR mounting stability |
| Map origin jumps | Map suddenly shifts position | Loop closure correcting large error | This is actually correct behavior -- the correction is working |

### Debugging workflow

```bash
# 1. Check if LiDAR data is coming in
ros2 topic hz /scan
# Should be 10-30 Hz

# 2. Check if odometry is publishing
ros2 topic hz /odom
# Should be 20-100 Hz

# 3. Check TF tree
ros2 run tf2_tools view_frames
# Look for: map -> odom -> base_link -> laser_frame chain

# 4. Check slam_toolbox status
ros2 topic echo /slam_toolbox/feedback --once

# 5. Visualize in RViz
# Add: Map, LaserScan, TF, RobotModel displays
# Look for: scan alignment with map edges
```

---

## 10. Complete Example: slam_toolbox Config for Indoor Environment

This is a complete, production-ready slam_toolbox configuration for a tracked robot
doing indoor/confined-space inspection with a 2D LiDAR.

```yaml
# File: config/slam_toolbox_params.yaml
slam_toolbox:
  ros__parameters:
    # ---- Plugin selection ----
    solver_plugin: solver_plugins::CeresSolver
    ceres_linear_solver: SPARSE_NORMAL_CHOLESKY
    ceres_preconditioner: SCHUR_JACOBI
    ceres_trust_strategy: LEVENBERG_MARQUARDT
    ceres_dogleg_type: TRADITIONAL_DOGLEG
    ceres_loss_function: None

    # ---- Map parameters ----
    resolution: 0.05                    # 5cm per pixel -- good for indoor
    max_laser_range: 8.0                # Clip LiDAR range (reduce for confined spaces to 3-4m)
    minimum_time_interval: 0.5          # Minimum seconds between processing scans
    transform_timeout: 0.2              # TF lookup timeout
    tf_buffer_duration: 30.0            # TF buffer length in seconds
    stack_size_to_use: 40000000         # 40MB stack for solver (increase if crashing)

    # ---- Scan processing ----
    minimum_travel_distance: 0.3        # Process scan after moving 0.3m (reduce for confined spaces)
    minimum_travel_heading: 0.3         # Process scan after rotating 0.3 rad (~17 deg)
    scan_buffer_size: 10                # Number of scans to buffer
    scan_buffer_maximum_scan_distance: 10.0   # Max distance between buffered scans
    link_match_minimum_response_fine: 0.1     # Fine matching quality threshold
    link_scan_maximum_distance: 1.5           # Max distance between linked scans

    # ---- Loop closure ----
    do_loop_closing: true
    loop_search_maximum_distance: 3.0   # Search radius for loop closures
    loop_match_minimum_chain_size: 10
    loop_match_maximum_variance_coarse: 3.0
    loop_match_minimum_response_coarse: 0.35
    loop_match_minimum_response_fine: 0.45

    # ---- Correlation search (scan matching) ----
    correlation_search_space_dimension: 0.5
    correlation_search_space_resolution: 0.01
    correlation_search_space_smear_deviation: 0.1

    # ---- Fine search ----
    fine_search_angle_offset: 0.00349   # ~0.2 degrees
    coarse_search_angle_offset: 0.349   # ~20 degrees
    coarse_angle_resolution: 0.0349     # ~2 degrees

    # ---- Penalty parameters ----
    angle_variance_penalty: 1.0
    distance_variance_penalty: 0.5

    # ---- Mode ----
    mode: mapping                       # Options: mapping, localization

    # ---- Frame IDs ----
    odom_frame: odom
    map_frame: map
    base_frame: base_link
    scan_topic: /scan

    # ---- Map update ----
    map_update_interval: 5.0            # Seconds between map publications
    enable_interactive_mode: true       # Allow interactive corrections in RViz

    # ---- Lifelong mapping (advanced) ----
    use_scan_matching: true
    use_scan_barycenter: true
    transform_publish_period: 0.02      # 50 Hz transform publication

    # ---- Debug ----
    debug_logging: false
    throttle_scans: 1                   # Process every Nth scan (1 = all)
```

### Launching with this config

```bash
ros2 launch slam_toolbox online_async_launch.py \
  slam_params_file:=config/slam_toolbox_params.yaml
```

### Adapting for confined environments (tunnels, narrow corridors, mines)

For confined spaces, modify these parameters:

```yaml
# Confined-space overrides
resolution: 0.03                      # Higher resolution for small features
max_laser_range: 4.0                  # Confined spaces are small, clip far readings
minimum_travel_distance: 0.1          # More frequent scans in tight spaces
minimum_travel_heading: 0.15          # More frequent scans on turns
loop_search_maximum_distance: 2.0     # Smaller search radius (passages are narrow)
correlation_search_space_dimension: 0.3  # Smaller search space (less room to drift)
```

For complete confined-space navigation configuration --> see `confined-spaces.md`.
