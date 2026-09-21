# GO2 Control Surfaces

Use this file when the task is about "which interface should we use?" or when motion commands, odometry, or bridge boundaries are confusing.

## Layers

1. Unitree SDK2 transport and robot-native interfaces
2. ROS 2 bridge or wrapper nodes that expose state and commands
3. Navigation stack components such as SLAM, localization, and Nav2

## Ownership Rule

Only one layer should own motion at a time.

- Low-level bringup or command validation: let the SDK or bridge own motion.
- Navigation validation: let the navigation stack own motion.
- Diagnostics: observe state everywhere, but keep actuation ownership singular.

## Data Contracts To Identify

- Robot state and health
- IMU and joint state
- Odometry source and frame chain
- Laser or point-cloud source used by mapping and planning
- Command input expected by the motion layer

## Questions To Answer Before Movement

1. Which node currently owns motion commands?
2. What state topic proves the robot is alive and stationary?
3. Which odometry output is trusted by the navigation stack?
4. What should be disabled when Nav2 takes control?

## Anti-Patterns

- Publishing ad hoc velocity tests while Nav2 or another controller is still active
- Accepting multiple odometry sources without a stated fusion owner
- Tuning planners before clarifying frame and command ownership
