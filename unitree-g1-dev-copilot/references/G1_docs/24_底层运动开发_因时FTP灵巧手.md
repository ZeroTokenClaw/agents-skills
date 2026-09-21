# 灵巧手SDK介绍

Source: <https://support.unitree.com/home/zh/G1_developer/inspire_ftp_dexterity_hand>

# 灵巧手SDK介绍

G1可搭载 [Inspire Robotics](https://inspire-robots.com/product/frwz/) 的仿人五指灵巧手，该灵巧手具有6个自由度和12个运动关节，可以模拟人手实现复杂动作。并且其触觉版本集成了17个触觉传感器。

## 控制方式

因时机械手官方提供485串口的ModBusRTU和ModbusTCP两种通信方式。对于不带有触觉传感器的灵巧手，其只支持485通信。本SDK同时支持上述两种方式与灵巧手进行通信，将数据与控制指令转发为DDS形式。

G1提供一个USB转串口模块，用户可以将该USB插在G1开发计算单元(PC2)上进行485通讯控制灵巧手，此时端口通常为/dev/ttyUSB0。此时需要运行带有485后缀的程序。

1. 使用因时官方SDK控制

用户可以根据因时灵巧手官方通讯协议自行编写程序控制灵巧手。

2. 使用宇树灵巧手SDK控制

G1通信建立在DDS框架之上。为便于使用unitree\_sdk2进行控制灵巧手。宇树提供灵巧手收发的数据转为DDS消息的示例程序。

## SDK接口说明

用户向 `"rt/inspire_hand/ctrl/*"` 话题发送 `"inspire::inspire_hand_ctrl"` 消息控制灵巧手。
从 `"rt/inspire_hand/state/*"` 话题接受 `"inspire::inspire_hand_state"` 消息获取灵巧手状态。
从 `"rt/inspire_hand/touch/*"` 话题接受 `"inspire::inspire_hand_touch"` 消息获取触觉传感器数据。
其中`*`为话题后缀，默认为`r`，表示右手。

在使用485通信时，`"rt/inspire_hand/touch/*"`话题将不会发布。

rt/inspire\_hand/ctrl/\*

rt/inspire\_hand/state/\*

rt/inspire\_hand/touch/\*

user

G1

## IDL数据格式

采用数组格式的电机数据，内部包含双手12个电机数据。具体MotorCmd\_.idl和MotorState\_.idl的格式见 [底层服务接口](https://support.unitree.com/home/zh/G1_developer/basic_services_interface)

灵巧手数据格式基本同因时官方说明文档相同，详情查看`inspire_hand_sdk/hand_idl`中`.idl`文件。

```
//inspire_hand_ctrl.idl
module inspire
{
    struct inspire_hand_ctrl
    {
        sequence<int16,6>  pos_set;
        sequence<int16,6>  angle_set;
        sequence<int16,6>  force_set;
        sequence<int16,6>  speed_set;
        int8 mode;
    };
};

//inspire_hand_state.idl
module inspire
{
    struct inspire_hand_state
    {
        sequence<int16,6>  pos_act;
        sequence<int16,6>  angle_act;
        sequence<int16,6>  force_act;
        sequence<int16,6>  current;
        sequence<uint8,6>  err;
        sequence<uint8,6>  status;
        sequence<uint8,6>  temperature;
    };
};

//inspire_hand_touch.idl
module inspire
{
    struct inspire_hand_touch
    {
        sequence<int16,9>   fingerone_tip_touch;      // 小拇指指端触觉数据
        sequence<int16,96>  fingerone_top_touch;      // 小拇指指尖触觉数据
        sequence<int16,80>  fingerone_palm_touch;     // 小拇指指腹触觉数据
        sequence<int16,9>   fingertwo_tip_touch;      // 无名指指端触觉数据
        sequence<int16,96>  fingertwo_top_touch;      // 无名指指尖触觉数据
        sequence<int16,80>  fingertwo_palm_touch;     // 无名指指腹触觉数据
        sequence<int16,9>   fingerthree_tip_touch;    // 中指指端触觉数据
        sequence<int16,96>  fingerthree_top_touch;    // 中指指尖触觉数据
        sequence<int16,80>  fingerthree_palm_touch;   // 中指指腹触觉数据
        sequence<int16,9>   fingerfour_tip_touch;     // 食指指端触觉数据
        sequence<int16,96>  fingerfour_top_touch;     // 食指指尖触觉数据
        sequence<int16,80>  fingerfour_palm_touch;    // 食指指腹触觉数据
        sequence<int16,9>   fingerfive_tip_touch;     // 大拇指指端触觉数据
        sequence<int16,96>  fingerfive_top_touch;     // 大拇指尖触觉数据
        sequence<int16,9>   fingerfive_middle_touch;  // 大拇指指中触觉数据
        sequence<int16,96>  fingerfive_palm_touch;    // 大拇指指腹触觉数据
        sequence<int16,112> palm_touch;                // 掌心触觉数据
    };

};
```

note

控制消息增加了模式选项，控制指令的组合模式按二进制方式实现，从而实现指定指令执行。

```
mode 0：0000（无操作）
mode 1：0001（角度）
mode 2：0010（位置）
mode 3：0011（角度 + 位置）
mode 4：0100（力控）
mode 5：0101（角度 + 力控）
mode 6：0110（位置 + 力控）
mode 7：0111（角度 + 位置 + 力控）
mode 8：1000（速度）
mode 9：1001（角度 + 速度）
mode 10：1010（位置 + 速度）
mode 11：1011（角度 + 位置 + 速度）
mode 12：1100（力控 + 速度）
mode 13：1101（角度 + 力控 + 速度）
mode 14：1110（位置 + 力控 + 速度）
mode 15：1111（角度 + 位置 + 力控 + 速度）
```

* IDL中的关节顺序

|  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| Id | 0 | 1 | 2 | 3 | 4 | 5 |
| Joint | Hand | | | | | |
| pinky | ring | middle | index | thumb-bend | thumb-rotation |

---

## 安装

1. git clone SDK工作目录：

   ```
   git clone https://github.com/NaCl-1374/inspire_hand_ws.git
   ```
2. 更新子模块：

   ```
   git submodule init  # 初始化子模块
   git submodule update  # 更新子模块到最新版本
   ```
3. 安装[unitree\_sdk2\_python](https://github.com/unitreerobotics/unitree_sdk2_python)：

   ```
   cd unitree_sdk2_python
   pip install -e .
   ```

必须

参考: [unitree\_sdk2\_python](https://github.com/unitreerobotics/unitree_sdk2_python)，安装所需依赖，unitree\_sdk2\_python 测试通过后进行后续操作。

3. 安装inspire\_hand\_sdk

   ```
   cd inspire_hand_sdk
   pip install -e .
   ```

## 使用

### 灵巧手与环境配置

首先，对设备进行网络配置，灵巧手默认ip为：左手`192.168.123.210`,右手`192.168.123.211`,驱动运行设备网段需要与灵巧手处于同一网段。配置完成后执行`ping 192.168.123.210`、`ping 192.168.123.211`,检查通信是否正常。

若需要调整灵巧手IP及其他参数，可以执行下面使用示例中 **灵巧手配置面板** ，启动面板进行配置。
面板启动后会自动读取当前网络下设备的信息。修改面板上的参数后，需要点击`写入设置`将参数发送到灵巧手，此时参数并不会生效，若要生效，需要点击`保存设置`并重启设备。

对于使用485通信进行配置，其配置方式与TCP基本类似，可通过配置面板修改设备id,但由于485带宽有限，一条总线只支持一个设备以20Hz左右运行，所以一般仅需更改端口号。

note

在 Ubuntu 中，要让用户拥有串口权限，可以将该用户添加到 `dialout` 组。`dialout` 组具有对串口设备（如 `/dev/ttyS0` 和 `/dev/ttyUSB0`）的访问权限。以下是操作步骤：

1. **查看当前用户是否在 `dialout` 组**：

   ```
   groups $USER
   ```
2. **将用户添加到 `dialout` 组**（假设用户名是 `your_username`，将其替换为实际用户名）：

   ```
   sudo usermod -aG dialout your_username
   ```
3. **重新登录生效**：添加后需要重新登录或重启系统，以使权限生效。
4. **验证权限**：可以通过以下命令查看设备权限。

   ```
   ls -l /dev/ttyUSB0
   ```

完成后，用户应该能够正常访问串口设备。

note

若修改IP，则需要对相关文件中存在的以下代码进行修改，修改其`ip`选项为修改后的ip。推荐修改为和`unitree_sdk2`相同的`192.168.123.***`网段。

```
# inspire_hand_sdk/example/Vision_driver.py and inspire_hand_sdk/example/Headless_driver.py
handler=inspire_sdk.ModbusDataHandler(ip=inspire_hand_defaut.defaut_ip,LR='r',device_id=1)

# inspire_hand_sdk/example/init_set_inspire_hand.py
window = MainWindow(ip=defaut_ip)
```

其中的`LR`选项，为DDS消息后缀`*`的参数，可以根据设备进行定义。
在运行时注意修改DDS工作网卡选项，详情参考[G1 SDK 快速开发](https://support.unitree.com/home/zh/G1_developer/quick_development)对DDS进行配置

SDK主要通信接口定义如下：请按照说明进行配置

```
class ModbusDataHandler:
    def __init__(self, data=data_sheet, history_length=100, network=None, ip=None, port=6000, device_id=1, LR='r', use_serial=False, serial_port='/dev/ttyUSB0', baudrate=115200, states_structure=None, initDDS=True, max_retries=5, retry_delay=2):
        """_summary_
        Calling self.read() in a loop reads and returns the data, and publishes the DDS message at the same time
        Args:
            data (dict, optional): Tactile sensor register definition. Defaults to data_sheet.
            history_length (int, optional): Hand state history_length. Defaults to 100.
            network (str, optional): Name of the DDS NIC. Defaults to None.
            ip (str, optional): ModbusTcp IP. Defaults to None will use 192.1686.11.210.
            port (int, optional): ModbusTcp IP port. Defaults to 6000.
            device_id (int, optional): Hand ID. Defaults to 1.
            LR (str, optional): Topic suffix l or r. Defaults to 'r'.
            use_serial (bool, optional): Whether to use serial mode. Defaults to False.
            serial_port (str, optional): Serial port name. Defaults to '/dev/ttyUSB0'.
            baudrate (int, optional): Serial baud rate. Defaults to 115200.
            states_structure (list, optional): List of tuples for state registers. Each tuple should contain (attribute_name, start_address, length, data_type). If None ,will publish All Data
            initDDS (bool, optional): Run ChannelFactoryInitialize(0),only need run once in all program
            max_retries (int, optional): Number of retries for connecting to Modbus server. Defaults to 3.
            retry_delay (int, optional): Delay between retries in seconds. Defaults to 2.
        Raises:
            ConnectionError: raise when connection fails after max_retries
        """
```

### 使用示例

以下为几个常用示例的使用说明：

1. **DDS 发布控制指令**：

   运行以下脚本来发布控制指令，：

   ```
   python inspire_hand_sdk/example/dds_publish.py
   ```

控制指令不区分485或TCP。运行后灵巧手首先握拳，随后循环开合。

2. **DDS 订阅灵巧手状态和触觉传感器数据，并可视化**：

   运行以下脚本来订阅灵巧手的状态和传感器数据，并进行数据可视化：

   ```
   python inspire_hand_sdk/example/dds_subscribe.py
   ```
3. **灵巧手 DDS 驱动（无图模式）**：

   使用以下脚本进行无图模式的驱动操作：

   ```
   python inspire_hand_sdk/example/Headless_driver.py
   ```

   note

   其中带有485的程序，表示使用RS-485驱动，没有则表示使用TCP驱动。 `l/r/double`后缀，分别表示单独左右手和双手同时驱动。
4. **灵巧手 DDS 驱动（面板模式）**：

   通过以下脚本进入面板模式，控制灵巧手的 DDS 驱动：

   ```
   python inspire_hand_sdk/example/Vision_driver.py
   ```
5. **灵巧手配置面板**：

   运行以下脚本来使用灵巧手的配置面板：

   ```
   python inspire_hand_sdk/example/init_set_inspire_hand.py
   ```
6. **DDS 发布控制指令 C++**：

   运行以下命令编译运行示例程序：

   ```
   cd inspire_hand_sdk
   mkdir build && cd build
   cmake ..
   make
   ./hand_dds
   ```

---
