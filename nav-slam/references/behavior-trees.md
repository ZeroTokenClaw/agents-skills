# Behavior Trees Reference

## Table of Contents

1. [What Are Behavior Trees](#1-what-are-behavior-trees)
2. [Nav2 BT XML Format](#2-nav2-bt-xml-format)
3. [Built-in BT Nodes in Nav2](#3-built-in-bt-nodes-in-nav2)
4. [Creating Custom BT Nodes](#4-creating-custom-bt-nodes)
5. [BT Patterns](#5-bt-patterns)
6. [Default NavigateToPose BT Walkthrough](#6-default-navigatetopose-bt-walkthrough)
7. [Modifying Default BTs](#7-modifying-default-bts)
8. [Adding Waypoint Inspection Behavior](#8-adding-waypoint-inspection-behavior)
9. [Error Handling in BTs](#9-error-handling-in-bts)
10. [Complete Example: Navigate-Inspect-Continue BT](#10-complete-example-navigate-inspect-continue-bt)

---

## 1. What Are Behavior Trees

**For software developers:** A behavior tree (BT) is like a structured decision-making
flowchart that runs every tick (typically 10Hz). Think of it as a composable alternative
to deeply nested if/else chains or complex state machines.

Each node returns one of three states: SUCCESS, FAILURE, or RUNNING (still processing).
Parent nodes use these results to decide whether to continue, try alternatives, or abort.

### The three node types

**Action nodes** (leaves) -- Do actual work:
- Perform a concrete operation (e.g., compute a path, follow a path, take a photo)
- Return SUCCESS when done, FAILURE if error, RUNNING while working
- Examples: ComputePathToPose, FollowPath, Spin, BackUp

**Condition nodes** (leaves) -- Check something:
- Like an if statement
- Return SUCCESS (true) or FAILURE (false) instantly, never RUNNING
- Examples: IsPathValid, IsBatteryLow, GoalReached

**Control nodes** (branches) -- Decide flow:
- Like control structures (if/else, try/catch, loops)
- **Sequence**: Run children left-to-right, stop on first FAILURE (like `&&`)
- **Fallback**: Run children left-to-right, stop on first SUCCESS (like `||`)
- **Decorator**: Wraps and modifies one child's behavior (e.g., rate limiting, retries)

### Visual representation

```
             [Fallback]                  "Try plan A, if it fails try plan B"
              /      \
       [Sequence]   [Sequence]
        /    \        /    \
   Navigate  Done  Recover  Navigate
   To Goal          |       To Goal
                    Spin
```

Reading this tree: "Try to navigate to goal. If that fails, spin to recover, then
try navigating again."

---

## 2. Nav2 BT XML Format

Nav2 behavior trees are defined in XML files. The format is based on BehaviorTree.CPP v4.

### Basic structure

```xml
<root BTCPP_format="4">
  <BehaviorTree ID="MainTree">
    <!-- Your tree here -->
    <Sequence name="navigate">
      <Action ID="ComputePathToPose" goal="{goal}" path="{path}"
              planner_id="GridBased"/>
      <Action ID="FollowPath" path="{path}" controller_id="FollowPath"/>
    </Sequence>
  </BehaviorTree>
</root>
```

### Key concepts

**Blackboard variables** -- Variables shared between nodes, referenced with `{curly_braces}`:
```xml
<!-- Write to blackboard -->
<Action ID="ComputePathToPose" goal="{goal}" path="{path}"/>
<!-- Read from blackboard -->
<Action ID="FollowPath" path="{path}"/>
```

**Node IDs** -- Reference registered BT node plugins:
```xml
<Action ID="ComputePathToPose"/>   <!-- Nav2 built-in action -->
<Condition ID="IsPathValid"/>       <!-- Nav2 built-in condition -->
<Control ID="PipelineSequence"/>    <!-- Nav2 built-in control -->
```

---

## 3. Built-in BT Nodes in Nav2

### Action nodes

| Node ID | Purpose | Key Ports |
|---------|---------|-----------|
| `ComputePathToPose` | Plan a path from current pose to goal | `goal`, `path`, `planner_id` |
| `ComputePathThroughPoses` | Plan through multiple poses | `goals`, `path`, `planner_id` |
| `FollowPath` | Send path to controller to follow | `path`, `controller_id` |
| `Spin` | Rotate in place | `spin_dist` (radians) |
| `BackUp` | Drive backward | `backup_dist`, `backup_speed` |
| `Wait` | Pause execution | `wait_duration` (seconds) |
| `DriveOnHeading` | Drive straight on current heading | `dist_to_travel`, `speed` |
| `ClearEntireCostmap` | Clear a costmap | `service_name` |
| `NavigateToPose` | Full navigate action (used in subtrees) | `goal`, `behavior_tree` |
| `TruncatePath` | Shorten a path | `input_path`, `output_path`, `distance` |
| `RemovePassedGoals` | Remove goals robot has passed | `input_goals`, `output_goals` |

### Condition nodes

| Node ID | Purpose | Returns SUCCESS when |
|---------|---------|---------------------|
| `IsPathValid` | Check if current path is still valid | Path is collision-free |
| `GoalReached` | Check if robot is at the goal | Within tolerance of goal |
| `IsBatteryLow` | Check battery level | Battery below threshold |
| `IsStuck` | Check if robot is stuck | Robot hasn't moved recently |
| `TransformAvailable` | Check if a TF transform is available | Transform exists |
| `GlobalUpdatedGoal` | Check if goal has been updated | New goal received |
| `GoalUpdated` | Check if the tracked goal changed | Goal differs from previous |
| `IsBatteryCharging` | Check charging status | Battery is charging |

### Control/Decorator nodes

| Node ID | Type | Purpose |
|---------|------|---------|
| `PipelineSequence` | Control | Like Sequence but ticks all children, not just current |
| `RecoveryNode` | Control | Tries child, if fails runs recovery, retries N times |
| `RoundRobin` | Control | Cycles through children on each tick |
| `RateController` | Decorator | Limits child tick rate |
| `DistanceController` | Decorator | Only ticks child after robot moves N meters |
| `SpeedController` | Decorator | Adjusts tick rate based on robot speed |
| `GoalUpdater` | Decorator | Updates goal from topic |
| `SingleTrigger` | Decorator | Only ticks child once, then returns cached result |
| `PathLongerOnApproach` | Decorator | Checks if replanned path is much longer |

---

## 4. Creating Custom BT Nodes

When the built-in nodes don't cover your needs (e.g., "take a photo at each waypoint"),
you create custom BT node plugins.

### C++ custom action node

```cpp
// File: src/take_photo_bt_node.cpp
#include <behaviortree_cpp/action_node.h>
#include <rclcpp/rclcpp.hpp>
#include <std_srvs/srv/trigger.hpp>

class TakePhoto : public BT::SyncActionNode
{
public:
  TakePhoto(const std::string& name, const BT::NodeConfig& config)
    : BT::SyncActionNode(name, config)
  {
    node_ = rclcpp::Node::make_shared("take_photo_bt_node");
    client_ = node_->create_client<std_srvs::srv::Trigger>("/camera/take_photo");
  }

  static BT::PortsList providedPorts()
  {
    return {
      BT::InputPort<std::string>("photo_id", "Identifier for this photo"),
      BT::OutputPort<bool>("photo_taken", "Whether photo was taken successfully")
    };
  }

  BT::NodeStatus tick() override
  {
    auto request = std::make_shared<std_srvs::srv::Trigger::Request>();
    auto future = client_->async_send_request(request);

    if (rclcpp::spin_until_future_complete(node_, future, std::chrono::seconds(5))
        == rclcpp::FutureReturnCode::SUCCESS)
    {
      auto result = future.get();
      setOutput("photo_taken", result->success);
      return result->success ? BT::NodeStatus::SUCCESS : BT::NodeStatus::FAILURE;
    }

    RCLCPP_ERROR(node_->get_logger(), "Photo service timed out");
    return BT::NodeStatus::FAILURE;
  }

private:
  rclcpp::Node::SharedPtr node_;
  rclcpp::Client<std_srvs::srv::Trigger>::SharedPtr client_;
};

// Register the node as a BT plugin
#include <behaviortree_cpp/bt_factory.h>
BT_REGISTER_NODES(factory)
{
  factory.registerNodeType<TakePhoto>("TakePhoto");
}
```

### Register in Nav2 params

```yaml
bt_navigator:
  ros__parameters:
    plugin_lib_names:
      - nav2_compute_path_to_pose_action_bt_node
      - nav2_follow_path_action_bt_node
      - nav2_spin_action_bt_node
      - nav2_back_up_action_bt_node
      - nav2_wait_action_bt_node
      - nav2_clear_costmap_service_bt_node
      - nav2_is_stuck_condition_bt_node
      - nav2_goal_reached_condition_bt_node
      - nav2_is_path_valid_condition_bt_node
      - nav2_pipeline_sequence_bt_node
      - nav2_recovery_node_bt_node
      - nav2_rate_controller_bt_node
      - nav2_distance_controller_bt_node
      - my_custom_bt_nodes                  # Your plugin library
```

### Python alternative (for prototyping)

For experiments and prototyping, you can use `py_trees` instead of C++ BT nodes.
It's slower but much faster to iterate on:

```bash
pip install py_trees py_trees_ros
```

---

## 5. BT Patterns

### Sequence (AND logic)

All children must succeed. Stops on first failure.

```xml
<Sequence name="go_and_inspect">
  <Action ID="ComputePathToPose" goal="{goal}" path="{path}"/>
  <Action ID="FollowPath" path="{path}"/>
  <Action ID="TakePhoto" photo_id="inspection_1"/>
</Sequence>
```

If any child fails, the sequence stops.

### Fallback (OR logic)

Try children until one succeeds. Stops on first success.

```xml
<Fallback name="try_navigation_strategies">
  <Action ID="ComputePathToPose" goal="{goal}" path="{path}" planner_id="GridBased"/>
  <Action ID="ComputePathToPose" goal="{goal}" path="{path}" planner_id="ThetaStar"/>
  <Action ID="ReportNavigationFailure"/>
</Fallback>
```

Tries each child in order until one succeeds.

### RecoveryNode

Built-in Nav2 pattern: try an action, if it fails, run recovery, retry up to N times.

```xml
<RecoveryNode number_of_retries="3" name="navigate_with_recovery">
  <!-- Try this first -->
  <Sequence>
    <Action ID="ComputePathToPose" goal="{goal}" path="{path}"/>
    <Action ID="FollowPath" path="{path}"/>
  </Sequence>
  <!-- If it fails, do this recovery -->
  <Sequence>
    <Action ID="ClearEntireCostmap" name="clear_local"
            service_name="/local_costmap/clear_entirely_local_costmap"/>
    <Action ID="Spin" spin_dist="1.57"/>
  </Sequence>
</RecoveryNode>
```

### PipelineSequence

Like Sequence but keeps ticking all previous children even while later ones run.
Critical for replanning while following a path:

```xml
<PipelineSequence name="navigate_with_replanning">
  <!-- This keeps re-running even while FollowPath is RUNNING -->
  <RateController hz="1.0">
    <Action ID="ComputePathToPose" goal="{goal}" path="{path}"/>
  </RateController>
  <!-- This follows the continuously updated path -->
  <Action ID="FollowPath" path="{path}"/>
</PipelineSequence>
```

This keeps replanning the path at the specified rate while the controller simultaneously
follows the latest computed path.

### Decorator: RateController

Limit how often a child is ticked:

```xml
<RateController hz="0.5">  <!-- Replan every 2 seconds -->
  <Action ID="ComputePathToPose" goal="{goal}" path="{path}"/>
</RateController>
```

### Decorator: DistanceController

Only tick child after robot moves a certain distance:

```xml
<DistanceController distance="1.0">  <!-- Replan every 1 meter -->
  <Action ID="ComputePathToPose" goal="{goal}" path="{path}"/>
</DistanceController>
```

---

## 6. Default NavigateToPose BT Walkthrough

The default Nav2 behavior tree for `NavigateToPose` follows this logic:

```
NavigateRecovery (RecoveryNode, 6 retries)
├── NavigateWithReplanning (PipelineSequence)
│   ├── RateController (1 Hz)
│   │   └── ComputePathToPose  --> Continuously replan
│   └── FollowPath             --> Follow the latest path
│
└── RecoveryActions (Sequence) --> If navigation fails:
    ├── ClearEntireCostmap (global)
    ├── ClearEntireCostmap (local)
    ├── Spin (1.57 rad)
    └── Wait (5 seconds)
```

**In plain English:**
1. Plan a path and start following it
2. Every second, recompute the path (in case obstacles appeared)
3. If the controller fails (can't follow path), try recovery:
   a. Clear both costmaps (remove phantom obstacles)
   b. Spin in place (scan surroundings to rebuild costmap)
   c. Wait 5 seconds (let dynamic obstacles move away)
4. Retry navigation up to 6 times
5. If all retries fail, report FAILURE to the caller

---

## 7. Modifying Default BTs

### Using a custom BT file

```yaml
bt_navigator:
  ros__parameters:
    default_nav_to_pose_bt_xml: "/path/to/my_custom_bt.xml"
```

### Common modifications

**Increase recovery retries for confined spaces:**

```xml
<RecoveryNode number_of_retries="10" name="navigate_recovery">
  <!-- ... -->
</RecoveryNode>
```

**Add backup as a recovery behavior:**

```xml
<Sequence name="recovery_sequence">
  <Action ID="ClearEntireCostmap" name="clear_local"
          service_name="/local_costmap/clear_entirely_local_costmap"/>
  <Action ID="BackUp" backup_dist="0.3" backup_speed="0.1"/>
  <Action ID="Spin" spin_dist="1.57"/>
  <Action ID="Wait" wait_duration="3"/>
</Sequence>
```

**Replan more frequently in dynamic environments:**

```xml
<RateController hz="2.0">  <!-- 2 Hz instead of default 1 Hz -->
  <Action ID="ComputePathToPose" goal="{goal}" path="{path}"/>
</RateController>
```

**Skip spin recovery in narrow passages (robot can't spin):**

```xml
<Sequence name="confined_space_recovery">
  <Action ID="ClearEntireCostmap" name="clear_local"
          service_name="/local_costmap/clear_entirely_local_costmap"/>
  <Action ID="BackUp" backup_dist="0.5" backup_speed="0.1"/>
  <Action ID="Wait" wait_duration="2"/>
</Sequence>
```

---

## 8. Adding Waypoint Inspection Behavior

For inspection tasks, you typically want the robot to:
1. Navigate to inspection point
2. Stop and stabilize
3. Capture data (photo, video, sensor reading)
4. Move to next point

### Using Nav2's WaypointFollower with task executors

Nav2 has a built-in waypoint follower with "task executor" plugins that run at each waypoint:

```yaml
waypoint_follower:
  ros__parameters:
    loop_rate: 20
    stop_on_failure: false
    waypoint_task_executor_plugin: "wait_at_waypoint"
    wait_at_waypoint:
      plugin: "nav2_waypoint_follower::WaitAtWaypoint"
      enabled: true
      waypoint_pause_duration: 2000    # milliseconds to pause at each waypoint
```

### Custom task executor (for taking photos)

```cpp
// File: src/photo_at_waypoint.cpp
#include <nav2_waypoint_follower/plugins/wait_at_waypoint.hpp>

class PhotoAtWaypoint : public nav2_core::WaypointTaskExecutor
{
public:
  void initialize(
    const rclcpp_lifecycle::LifecycleNode::WeakPtr& parent,
    const std::string& plugin_name) override
  {
    auto node = parent.lock();
    camera_client_ = node->create_client<std_srvs::srv::Trigger>("/camera/capture");
    RCLCPP_INFO(node->get_logger(), "PhotoAtWaypoint initialized");
  }

  bool processAtWaypoint(
    const geometry_msgs::msg::PoseStamped& curr_pose,
    const int& curr_waypoint_index) override
  {
    RCLCPP_INFO(logger_, "Taking photo at waypoint %d", curr_waypoint_index);

    auto request = std::make_shared<std_srvs::srv::Trigger::Request>();
    auto future = camera_client_->async_send_request(request);
    // Wait for photo capture
    rclcpp::spin_until_future_complete(node_, future, std::chrono::seconds(10));

    return future.get()->success;
  }

private:
  rclcpp::Client<std_srvs::srv::Trigger>::SharedPtr camera_client_;
};
```

---

## 9. Error Handling in BTs

### Timeout handling

```xml
<!-- Abort navigation if it takes too long -->
<Timeout msec="60000" name="navigation_timeout">
  <Sequence>
    <Action ID="ComputePathToPose" goal="{goal}" path="{path}"/>
    <Action ID="FollowPath" path="{path}"/>
  </Sequence>
</Timeout>
```

### Monitoring battery during navigation

```xml
<Fallback name="main_with_battery_check">
  <Sequence>
    <Condition ID="IsBatteryLow" battery_threshold="20.0"/>
    <Action ID="NavigateToPose" goal="{charging_station}"/>
  </Sequence>
  <Sequence>
    <Action ID="ComputePathToPose" goal="{goal}" path="{path}"/>
    <Action ID="FollowPath" path="{path}"/>
  </Sequence>
</Fallback>
```

### Graceful degradation

```xml
<Fallback name="navigate_with_fallbacks">
  <!-- Try primary planner -->
  <Sequence>
    <Action ID="ComputePathToPose" goal="{goal}" path="{path}" planner_id="SmacPlanner"/>
    <Action ID="FollowPath" path="{path}" controller_id="RegulatedPurePursuit"/>
  </Sequence>
  <!-- Fall back to simpler planner if primary fails -->
  <Sequence>
    <Action ID="ComputePathToPose" goal="{goal}" path="{path}" planner_id="NavFn"/>
    <Action ID="FollowPath" path="{path}" controller_id="RegulatedPurePursuit"/>
  </Sequence>
  <!-- Last resort: just try to get closer -->
  <Action ID="DriveOnHeading" dist_to_travel="0.5" speed="0.1"/>
</Fallback>
```

---

## 10. Complete Example: Navigate-Inspect-Continue BT

This behavior tree implements a full inspection workflow:
1. Navigate to each inspection waypoint
2. Wait for robot to stabilize
3. Take a photo/scan
4. If photo fails, retry once
5. Move to the next waypoint
6. If navigation fails, try recovery then skip to next waypoint

```xml
<root BTCPP_format="4">
  <BehaviorTree ID="InspectionTree">
    <!-- Main inspection loop -->
    <Sequence name="inspection_mission">
      <!-- For each waypoint in the mission -->
      <ForEach name="iterate_waypoints"
               input="{waypoints}" output="{current_goal}"
               iterator="{waypoint_index}">

        <!-- Try to inspect this waypoint, with recovery -->
        <RecoveryNode number_of_retries="3" name="waypoint_recovery">

          <!-- Navigate and inspect -->
          <Sequence name="navigate_and_inspect">

            <!-- Navigate to waypoint with replanning -->
            <RecoveryNode number_of_retries="5" name="navigate_recovery">
              <PipelineSequence name="navigate_with_replanning">
                <RateController hz="1.0">
                  <Action ID="ComputePathToPose"
                          goal="{current_goal}" path="{path}"
                          planner_id="GridBased"/>
                </RateController>
                <Action ID="FollowPath" path="{path}"
                        controller_id="FollowPath"/>
              </PipelineSequence>

              <!-- Navigation recovery: backup (no spin in confined spaces) -->
              <Sequence name="nav_recovery_actions">
                <Action ID="ClearEntireCostmap" name="clear_local"
                        service_name="/local_costmap/clear_entirely_local_costmap"/>
                <Action ID="BackUp" backup_dist="0.3" backup_speed="0.1"/>
                <Action ID="Wait" wait_duration="2"/>
              </Sequence>
            </RecoveryNode>

            <!-- Wait for robot to stabilize -->
            <Action ID="Wait" wait_duration="1"/>

            <!-- Take inspection photo (with retry) -->
            <RecoveryNode number_of_retries="2" name="photo_recovery">
              <Action ID="TakePhoto" photo_id="{waypoint_index}"/>
              <Action ID="Wait" wait_duration="1"/>
            </RecoveryNode>

          </Sequence>

          <!-- If navigate+inspect fails completely, try clearing costmap -->
          <Sequence name="waypoint_recovery_actions">
            <Action ID="ClearEntireCostmap" name="clear_global"
                    service_name="/global_costmap/clear_entirely_global_costmap"/>
            <Action ID="ClearEntireCostmap" name="clear_local"
                    service_name="/local_costmap/clear_entirely_local_costmap"/>
            <Action ID="Wait" wait_duration="3"/>
          </Sequence>

        </RecoveryNode>
      </ForEach>
    </Sequence>
  </BehaviorTree>
</root>
```

### How to use this BT

1. Save as `config/inspection_bt.xml`
2. Configure in Nav2 params:
   ```yaml
   bt_navigator:
     ros__parameters:
       default_nav_to_pose_bt_xml: "config/inspection_bt.xml"
       plugin_lib_names:
         - nav2_compute_path_to_pose_action_bt_node
         - nav2_follow_path_action_bt_node
         - nav2_back_up_action_bt_node
         - nav2_wait_action_bt_node
         - nav2_clear_costmap_service_bt_node
         - nav2_pipeline_sequence_bt_node
         - nav2_recovery_node_bt_node
         - nav2_rate_controller_bt_node
         - my_inspection_bt_nodes    # Your custom TakePhoto node
   ```
3. Populate the `{waypoints}` blackboard variable from your mission planner

### Debugging BTs

```bash
# Install Groot2 (BT visualization tool)
# https://www.behaviortree.dev/groot

# Enable BT logging in Nav2
bt_navigator:
  ros__parameters:
    enable_groot_monitoring: true
    groot_zmq_publisher_port: 1666
    groot_zmq_server_port: 1667
```

Groot2 connects to the running BT and shows real-time node status -- which nodes are
running, which succeeded, which failed. Invaluable for debugging complex behaviors.
