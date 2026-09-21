# GO2 Safety Preflight

Run this checklist before any real-robot movement.

## Minimum Gating

1. Confirm estop access and who can press it.
2. Confirm a clear test area and expected stop distance.
3. Confirm the robot is standing in a stable, known mode.
4. Confirm the operator knows which process currently owns motion.
5. Confirm state and odometry are live enough to observe the result.

## Indoor First

- Start with conservative speeds and short paths.
- Prefer straight-line and small-angle checks before autonomous goals.
- Be careful with spin and backup recoveries because quadruped behavior differs from wheeled robots.

## Outdoor Later

- Re-check traction, terrain, and line of sight.
- Do not assume indoor localization or obstacle parameters transfer cleanly outdoors.
- Increase sensing and route-validation discipline before increasing mission length.

## Stop Conditions

Stop immediately if:

- Command ownership is unclear
- The odometry or state pipeline is stale
- The robot mode changes unexpectedly
- The planner requests behavior that exceeds the test envelope
