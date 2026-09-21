# G1 joint tables

Canonical order from the official joint motor sequence page (support.unitree.com G1 developer docs). The array is `unitree_hg::msg::dds_::LowCmd_.motor_cmd` (35 slots; body joints occupy 0-28; `rt/arm_sdk` uses slot 29 as the blend weight). `mode_pr` selects ankle naming: 0 = pitch/roll (PR), 1 = A/B.

Mode ids: the support site labels the tables below with legacy `mode_machine` values, while the up-to-date model files in unitree_ros `g1_description` use ids 4/5/6/10-18 (for example `g1_23dof_mode_10` and `g1_29dof_mode_11` to `18`), and 9 is current as `g1_dual_arm`. The joint order is the stable part; read `mode_machine` from the robot and match the model file to it.

## 23-DOF variant (legacy mode_machine 1)

| Index | mode_pr == 0 | mode_pr == 1 |
| --- | --- | --- |
| 0 | L_LEG_HIP_PITCH | L_LEG_HIP_PITCH |
| 1 | L_LEG_HIP_ROLL | L_LEG_HIP_ROLL |
| 2 | L_LEG_HIP_YAW | L_LEG_HIP_YAW |
| 3 | L_LEG_KNEE | L_LEG_KNEE |
| 4 | L_LEG_ANKLE_PITCH | L_LEG_ANKLE_B |
| 5 | L_LEG_ANKLE_ROLL | L_LEG_ANKLE_A |
| 6 | R_LEG_HIP_PITCH | R_LEG_HIP_PITCH |
| 7 | R_LEG_HIP_ROLL | R_LEG_HIP_ROLL |
| 8 | R_LEG_HIP_YAW | R_LEG_HIP_YAW |
| 9 | R_LEG_KNEE | R_LEG_KNEE |
| 10 | R_LEG_ANKLE_PITCH | R_LEG_ANKLE_B |
| 11 | R_LEG_ANKLE_ROLL | R_LEG_ANKLE_A |
| 12 | WAIST_YAW | WAIST_YAW |
| 13 | (empty) | (empty) |
| 14 | (empty) | (empty) |
| 15 | L_SHOULDER_PITCH | L_SHOULDER_PITCH |
| 16 | L_SHOULDER_ROLL | L_SHOULDER_ROLL |
| 17 | L_SHOULDER_YAW | L_SHOULDER_YAW |
| 18 | L_ELBOW | L_ELBOW |
| 19 | L_WRIST_ROLL | L_WRIST_ROLL |
| 20 | (empty) | (empty) |
| 21 | (empty) | (empty) |
| 22 | R_SHOULDER_PITCH | R_SHOULDER_PITCH |
| 23 | R_SHOULDER_ROLL | R_SHOULDER_ROLL |
| 24 | R_SHOULDER_YAW | R_SHOULDER_YAW |
| 25 | R_ELBOW | R_ELBOW |
| 26 | R_WRIST_ROLL | R_WRIST_ROLL |
| 27 | (empty) | (empty) |
| 28 | (empty) | (empty) |

## 29-DOF variant (legacy mode_machine 2)

| Index | mode_pr == 0 | mode_pr == 1 |
| --- | --- | --- |
| 0 | L_LEG_HIP_PITCH | L_LEG_HIP_PITCH |
| 1 | L_LEG_HIP_ROLL | L_LEG_HIP_ROLL |
| 2 | L_LEG_HIP_YAW | L_LEG_HIP_YAW |
| 3 | L_LEG_KNEE | L_LEG_KNEE |
| 4 | L_LEG_ANKLE_PITCH | L_LEG_ANKLE_B |
| 5 | L_LEG_ANKLE_ROLL | L_LEG_ANKLE_A |
| 6 | R_LEG_HIP_PITCH | R_LEG_HIP_PITCH |
| 7 | R_LEG_HIP_ROLL | R_LEG_HIP_ROLL |
| 8 | R_LEG_HIP_YAW | R_LEG_HIP_YAW |
| 9 | R_LEG_KNEE | R_LEG_KNEE |
| 10 | R_LEG_ANKLE_PITCH | R_LEG_ANKLE_B |
| 11 | R_LEG_ANKLE_ROLL | R_LEG_ANKLE_A |
| 12 | WAIST_YAW | WAIST_YAW |
| 13 | WAIST_ROLL | WAIST_A |
| 14 | WAIST_PITCH | WAIST_B |
| 15 | L_SHOULDER_PITCH | L_SHOULDER_PITCH |
| 16 | L_SHOULDER_ROLL | L_SHOULDER_ROLL |
| 17 | L_SHOULDER_YAW | L_SHOULDER_YAW |
| 18 | L_ELBOW | L_ELBOW |
| 19 | L_WRIST_ROLL | L_WRIST_ROLL |
| 20 | L_WRIST_PITCH | L_WRIST_PITCH |
| 21 | L_WRIST_YAW | L_WRIST_YAW |
| 22 | R_SHOULDER_PITCH | R_SHOULDER_PITCH |
| 23 | R_SHOULDER_ROLL | R_SHOULDER_ROLL |
| 24 | R_SHOULDER_YAW | R_SHOULDER_YAW |
| 25 | R_ELBOW | R_ELBOW |
| 26 | R_WRIST_ROLL | R_WRIST_ROLL |
| 27 | R_WRIST_PITCH | R_WRIST_PITCH |
| 28 | R_WRIST_YAW | R_WRIST_YAW |

## 14-DOF upper body (`g1_dual_arm`, mode_machine 9)

Only indices 15-28 are populated; 0-14 are empty.

## Joint position limits (radians, official specs page)

| Index | Joint | Limit (rad) |
| --- | --- | --- |
| 0 | L_LEG_HIP_PITCH | -2.5307 ~ 2.8798 |
| 1 | L_LEG_HIP_ROLL | -0.5236 ~ 2.9671 |
| 2 | L_LEG_HIP_YAW | -2.7576 ~ 2.7576 |
| 3 | L_LEG_KNEE | -0.087267 ~ 2.8798 |
| 4 | L_LEG_ANKLE_PITCH | -0.87267 ~ 0.5236 |
| 5 | L_LEG_ANKLE_ROLL | -0.2618 ~ 0.2618 |
| 6 | R_LEG_HIP_PITCH | -2.5307 ~ 2.8798 |
| 7 | R_LEG_HIP_ROLL | -2.9671 ~ 0.5236 |
| 8 | R_LEG_HIP_YAW | -2.7576 ~ 2.7576 |
| 9 | R_LEG_KNEE | -0.087267 ~ 2.8798 |
| 10 | R_LEG_ANKLE_PITCH | -0.87267 ~ 0.5236 |
| 11 | R_LEG_ANKLE_ROLL | -0.2618 ~ 0.2618 |
| 12 | WAIST_YAW | -2.618 ~ 2.618 |
| 13 | WAIST_ROLL | -0.52 ~ 0.52 |
| 14 | WAIST_PITCH | -0.52 ~ 0.52 |
| 15 | L_SHOULDER_PITCH | -3.0892 ~ 2.6704 |
| 16 | L_SHOULDER_ROLL | -1.5882 ~ 2.2515 |
| 17 | L_SHOULDER_YAW | -2.618 ~ 2.618 |
| 18 | L_ELBOW | -1.0472 ~ 2.0944 |
| 19 | L_WRIST_ROLL | -1.972222054 ~ 1.972222054 |
| 20 | L_WRIST_PITCH | -1.614429558 ~ 1.614429558 |
| 21 | L_WRIST_YAW | -1.614429558 ~ 1.614429558 |
| 22 | R_SHOULDER_PITCH | -3.0892 ~ 2.6704 |
| 23 | R_SHOULDER_ROLL | -2.2515 ~ 1.5882 |
| 24 | R_SHOULDER_YAW | -2.618 ~ 2.618 |
| 25 | R_ELBOW | -1.0472 ~ 2.0944 |
| 26 | R_WRIST_ROLL | -1.972222054 ~ 1.972222054 |
| 27 | R_WRIST_PITCH | -1.614429558 ~ 1.614429558 |
| 28 | R_WRIST_YAW | -1.614429558 ~ 1.614429558 |

## Dex3-1 hand (HandCmd_.motor_cmd / HandState_.motor_state)

| Hand index | Joint |
| --- | --- |
| 0 | thumb_0 |
| 1 | thumb_1 |
| 2 | thumb_2 |
| 3 | middle_0 |
| 4 | middle_1 |
| 5 | index_0 |
| 6 | index_1 |

Sources: [joint_motor_sequence](https://support.unitree.com/home/en/G1_developer/joint_motor_sequence) and [about_G1](https://support.unitree.com/home/en/G1_developer/about_G1) on the official support site; fetch them for current values.
