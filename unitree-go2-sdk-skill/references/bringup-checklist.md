# GO2 Bringup Checklist

Use this checklist when the task is about first connection, re-bringup, or "why is the robot not visible from ROS 2?".

## Assumptions

- GO2 EDU on the same network segment as the workstation or onboard computer
- ROS 2 Humble on Ubuntu 22.04
- `unitree_sdk2` and `unitree_ros2` are the reference stacks

## Ordered Checks

1. Confirm power, battery level, estop availability, and physical clearance.
2. Confirm the workstation talks to the robot over the intended interface.
3. Source the ROS 2 Humble environment and the workspace that contains the bridge or driver.
4. Confirm the DDS implementation and interface selection expected by the current stack.
5. Start the GO2 bridge or ROS 2 bringup in the smallest viable configuration.
6. Verify that state topics are live before checking command topics.
7. Record exactly which node publishes state, odometry, IMU, and command interfaces.

## What Good Looks Like

- State topics appear consistently and remain stable
- TF frames are coherent enough for downstream localization
- A single command owner is identified for motion tests
- No motion test starts before state visibility and estop readiness

## Common Failure Patterns

- ROS environment sourced, but the wrong workspace overlays the intended one
- DDS is running, but the robot and workstation are effectively on different discovery islands
- Multiple launch files expose multiple candidate command topics with unclear ownership
- The user starts tuning Nav2 before the state pipeline is trustworthy

## References

- Official Unitree ROS 2 integration: `unitree_ros2`
- Official Unitree SDK2 transport layer: `unitree_sdk2`
