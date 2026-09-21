# RPC例程

Source: <https://support.unitree.com/home/zh/G1_developer/rpc_routine>

# RPC例程

本例程通过高层运控的 RPC 接口，实现了机器人的模式切换，以及站立，运动等的控制。

note

ai\_sport >= 8.2.0.0版本为LOCO\_SERVICE\_NAME = "sport";
低于该版本 LOCO\_SERVICE\_NAME = "loco"。

程序源代码可以位于 `unitree_sdk2/example/g1/high_level/g1_loco_client_example.cpp` ，也可通过 [此处](https://github.com/unitreerobotics/unitree_sdk2) 访问。运行方式与[《快速开发》](https://support.unitree.com/home/zh/G1_developer/quick_development)类似，但无需进入调试模式。

# 例程解析

## 主要逻辑

通过在启动的时候指定启动参数，可以实现不同的控制效果。

## 参数说明

| 参数 | 说明 | 赋值示例 |
| --- | --- | --- |
| `--network_interface` | 指定通信的网卡名 | `enp3s0` |
| `--get_fsm_id` | 获取机器人上层控制器的状态机id | / |
| `--get_fsm_mode` | 获取机器人上层控制器的状态机模式 | / |
| `--get_phase` | 获取机器人的相位 | / |
| `--set_fsm_id` | 设置状态机的id | 1 |
| `--set_velocity` | 设置运动速度[vx vy omega duration(可选)] | "0.5 0 0 1" |
| `--damp` | 进入阻尼模式 | / |
| `--start` | 进入主运控 | / |
| `--squat` | 蹲下 | / |
| `--sit` | 落座 | / |
| `--stand_up` | 站立 | / |
| `--zero_torque` | 零力矩模式 | / |
| `--stop_move` | 停止运动 | / |
| `--balance_stand` | 平衡站立 | / |
| `--continous_gait` | 连续步态 | true |
| `--switch_move_mode` | 切换运动模式 | true |
| `--move` | 以一定的速度运动[vx vy omega] | "0.5 0 0" |
| `--set_speed_mode` | 设置走跑运控下的最高速度 | 0/1/2/3 |

## 启动示例

在xxx方向以0.5m/s0.5m/s0.5m/s的速度运动1s1s1s

```
./g1_loco_client --network_interface=enp3s0 --set_velocity="0.5 0 0 1"
```

## 代码解析

### 解析参数

如果参数带有值，格式为`--${key}=${value}` 或者`--${key}="${value}"`；

如果参数没有值，格式为`--${key}`

```
std::map<std::string, std::string> args = {{"network_interface", "lo"}};

  std::map<std::string, std::string> values;
  for (int i = 1; i < argc; ++i) {
    std::string arg = argv[i];
    if (arg.substr(0, 2) == "--") {
      size_t pos = arg.find("=");
      std::string key, value;
      if (pos != std::string::npos) {
        key = arg.substr(2, pos - 2);
        value = arg.substr(pos + 1);

        if (value.front() == '"' && value.back() == '"') {
          value = value.substr(1, value.length() - 2);
        }
      } else {
        key = arg.substr(2);
        value = "";
      }
      if (args.find(key) != args.end()) {
        args[key] = value;
      } else {
        args.insert({{key, value}});
      }
    }
  }
```

### 初始化dds通信实例

```
unitree::robot::ChannelFactory::Instance()->Init(0, args["network_interface"]);
```

### 初始化上层控制的客户端

```
unitree::robot::g1::LocoClient client;

  client.Init();
  client.SetTimeout(10.f);
```

### 响应命令

逐个解析命令行参数，并通过调用相应的API实现对机器人的上层控制。

```
for (const auto &arg_pair : args) {
    std::cout << "Processing command: [" << arg_pair.first << "] with param: ["
              << arg_pair.second << "] ..." << std::endl;
    if (arg_pair.first == "network_interface") {
      continue;
    }

    if (arg_pair.first == "get_fsm_id") {
      int fsm_id;
      client.GetFsmId(fsm_id);
      std::cout << "current fsm_id: " << fsm_id << std::endl;
    }

    if (arg_pair.first == "get_fsm_mode") {
      int fsm_mode;
      client.GetFsmMode(fsm_mode);
      std::cout << "current fsm_mode: " << fsm_mode << std::endl;
    }

    if (arg_pair.first == "get_balance_mode") {
      int balance_mode;
      client.GetBalanceMode(balance_mode);
      std::cout << "current balance_mode: " << balance_mode << std::endl;
    }

    if (arg_pair.first == "get_swing_height") {
      float swing_height;
      client.GetSwingHeight(swing_height);
      std::cout << "current swing_height: " << swing_height << std::endl;
    }

    if (arg_pair.first == "get_stand_height") {
      float stand_height;
      client.GetStandHeight(stand_height);
      std::cout << "current stand_height: " << stand_height << std::endl;
    }

    if (arg_pair.first == "get_phase") {
      std::vector<float> phase;
      client.GetPhase(phase);
      std::cout << "current phase: (";
      for (const auto &p : phase) {
        std::cout << p << ", ";
      }
      std::cout << ")" << std::endl;
    }

    if (arg_pair.first == "set_fsm_id") {
      int fsm_id = std::stoi(arg_pair.second);
      client.SetFsmId(fsm_id);
      std::cout << "set fsm_id to " << fsm_id << std::endl;
    }

    if (arg_pair.first == "set_balance_mode") {
      int balance_mode = std::stoi(arg_pair.second);
      client.SetBalanceMode(balance_mode);
      std::cout << "set balance_mode to " << balance_mode << std::endl;
    }

    if (arg_pair.first == "set_swing_height") {
      float swing_height = std::stof(arg_pair.second);
      client.SetSwingHeight(swing_height);
      std::cout << "set swing_height to " << swing_height << std::endl;
    }

    if (arg_pair.first == "set_stand_height") {
      float stand_height = std::stof(arg_pair.second);
      client.SetStandHeight(stand_height);
      std::cout << "set stand_height to " << stand_height << std::endl;
    }

    if (arg_pair.first == "set_velocity") {
      std::vector<float> param = stringToFloatVector(arg_pair.second);
      auto param_size = param.size();
      float vx, vy, omega, duration;
      if (param_size == 3) {
        vx = param.at(0);
        vy = param.at(1);
        omega = param.at(2);
        duration = 1.f;
      } else if (param_size == 4) {
        vx = param.at(0);
        vy = param.at(1);
        omega = param.at(2);
        duration = param.at(3);
      } else {
        std::cerr << "Invalid param size for method SetVelocity: " << param_size
                  << std::endl;
        return 1;
      }

      client.SetVelocity(vx, vy, omega, duration);
      std::cout << "set velocity to " << arg_pair.second << std::endl;
    }

    if (arg_pair.first == "damp") {
      client.Damp();
    }

    if (arg_pair.first == "start") {
      client.Start();
    }

    if (arg_pair.first == "squat") {
      client.Squat();
    }

    if (arg_pair.first == "sit") {
      client.Sit();
    }

    if (arg_pair.first == "stand_up") {
      client.StandUp();
    }

    if (arg_pair.first == "zero_torque") {
      client.ZeroTorque();
    }

    if (arg_pair.first == "stop_move") {
      client.StopMove();
    }

    if (arg_pair.first == "high_stand") {
      client.HighStand();
    }

    if (arg_pair.first == "low_stand") {
      client.LowStand();
    }

    if (arg_pair.first == "balance_stand") {
      client.BalanceStand();
    }

    if (arg_pair.first == "continous_gait") {
      bool flag;
      if (arg_pair.second == "true") {
        flag = true;
      } else if (arg_pair.second == "false") {
        flag = false;
      } else {
        std::cerr << "invalid argument: " << arg_pair.second << std::endl;
        return 1;
      }
      client.ContinuousGait(flag);
    }

    if (arg_pair.first == "switch_move_mode") {
      bool flag;
      if (arg_pair.second == "true") {
        flag = true;
      } else if (arg_pair.second == "false") {
        flag = false;
      } else {
        std::cerr << "invalid argument: " << arg_pair.second << std::endl;
        return 1;
      }
      client.SwitchMoveMode(flag);
    }

    if (arg_pair.first == "move") {
      std::vector<float> param = stringToFloatVector(arg_pair.second);
      auto param_size = param.size();
      float vx, vy, omega;
      if (param_size == 3) {
        vx = param.at(0);
        vy = param.at(1);
        omega = param.at(2);
      } else {
        std::cerr << "Invalid param size for method SetVelocity: " << param_size
                  << std::endl;
        return 1;
      }
      client.Move(vx, vy, omega);
    }
  }
```
