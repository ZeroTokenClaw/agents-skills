# SLAM 导航服务接口

Source: <https://support.unitree.com/home/zh/G1_developer/slam_navigation_services_interface>

# SLAM 导航服务接口

## 一、介绍

SLAM与导航服务的接口基于unitree sdk2进行接口调用，使用前请保证与机器人在`同一局域网网段下`，并通过App确认G1的`unitree_slam`和`lidar_driver`服务开启。在使用接口调用时，请勿同时使用APP上的导航功能。客户端通过配置不同的api-id、订阅不同的话题数据，即可实现基础的SLAM与导航功能。

slam输出的点云与定位信息的坐标系原点为`Mid360-IMU坐标系的原点`，X轴正方向为机器人`正前方`，Z轴正方向为`竖直向上`，Mid360坐标系详情请查看LIDAR服务接口。

适用场景与范围：`X轴/Y轴小于45m`且`特征丰富`的`静态室内平地`场景。(大范围地图计算资源占用较多，为了不影响基础运控服务，请`勿超过`建议范围！！！)，剧烈动作可能导致定位丢失，请在使用该接口时`避免机器人剧烈运动`！

该部分功能适用于`教育科研`行业，不建议用于行业应用，行业应用请联系销售！

`注意`：在使用前请检查雷达原始点云和imu数据是否异常，且头部正常`竖直向上`固定`无松动`。若在静止状态下，雷达照射同一静止竖平面时，`前后点云数据帧出现明显分层`或`IMU线速度和加速度值明显异常`，请联系销售进行雷达维修。
原始点云数据话题名为：rt/utlidar/cloud\_livox\_mid360
原始IMU数据话题名为：rt/utlidar/imu\_livox\_mid360
![](https://doc-cdn.unitree.com/static/2025/7/23/ea38cdd7418e4b81852c819a55e7aa2e_1164x1000.jpg)

## 二、NX开发板网络配置

NX开发板的IP地址默认为`192.168.123.164`，用户可通过网线直连的方式接入到该局域网内，本服务使用的雷达IP地址为：`192.168.123.120`，在使用前请确定雷达IP地址正确。网络检查步骤如下：

**1**. 用户PC通过网线直连G1内部交换机后，将本机地址IP修改为`192.168.123.XXX`（XXX设置值请勿与已有IP冲突）。
![](https://doc-cdn.unitree.com/static/2024/12/18/e052b184d76444eab724e851136ec4a6_924x637.png)

**2**.打开终端，分别输入如下指令检查通信是否连接成功。

```
ssh unitree@192.168.123.164 # G1 进入NX开发板，初始密码为：123

ping 192.168.123.120 #雷达IP

ping 192.168.123.161 #运控PC IP
```

## 三、服务数据说明

服务名称与版本：SERVICE\_NAME = "slam\_operate"、VERSION = "1.0.0.1"
当前已开放接口api-id:1801开始建图、1802结束建图、1804初始化位姿、1102位姿导航、1201暂停导航、1202恢复导航、1901关闭slam。服务请求参数与反馈数据格式`均为Json`，具体参数如下：
1.开始建图

```
api id: 1801

输入参数：
{
  "data": {
      "slam_type": "indoor" #固定值
    }
}

反馈响应：
{
    "succeed":true, #是否实行执行成功
    "errorCode":0,  #错误码，0为正常
    "info":"",      #描述信息
    "data":{}       #其余数据
}
```

2.结束建图

```
api id: 1802

输入参数：
{
  "data": {
      "address": "/home/unitree/test.pcd" #pcd保存地址
    }
}

反馈响应：
{
    "succeed":true, #是否实行执行成功
    "errorCode":0,  #错误码，0为正常
    "info":"",      #描述信息
    "data":{}       #其余数据
}
```

`注意`：
为防止多个pcd地图文件数据占用过多的磁盘空间，建议文件名统一为`test1.pcd ~ test10.pcd`，覆盖式保存地图pcd数据。

3.初始化位姿

```
api id: 1804

输入参数：
{
  "data": {
        "x": 0.0, #初始化平移信息
        "y": 0.0,
        "z": 0.0,
        "q_x": 0.0, #初始化旋转信息
        "q_y": 0.0,
        "q_z": 0.0,
        "q_w": 1.0,
        "address": "/home/unitree/test.pcd" #pcd加载地址
    }
}

反馈响应：
{
    "succeed":true, #是否实行执行成功
    "errorCode":0,  #错误码，0为正常
    "info":"",      #描述信息
    "data":{}       #其余数据
}
```

4.位姿导航

```
api id: 1102

输入参数：
{
  "data": {
       "targetPose": {
          "x": 2.0,    #目标位姿信息
          "y": 0.0,
          "z": 0.0,
          "q_x": 0.0,
          "q_y": 0.0,
          "q_z": 0.0,
          "q_w": 1.0
        },
        "mode":1      #固定值
    }
}

反馈响应：
{
    "succeed":true, #是否实行执行成功
    "errorCode":0,  #错误码，0为正常
    "info":"",      #描述信息
    "data":{}       #其余数据
}
```

`注意`：
目标点与当前位置之间的距离不超过`10m`，机器人会沿直线行走，受雷达视角限制，障碍物高度不要低于`50cm`
5.暂停导航

```
api id: 1201

输入参数：
{
  "data": {
    }
}

反馈响应：
{
    "succeed":true, #是否实行执行成功
    "errorCode":0,  #错误码，0为正常
    "info":"",      #描述信息
    "data":{}       #其余数据
}
```

6.恢复导航

```
api id: 1202

输入参数：
{
  "data": {
    }
}

反馈响应：
{
    "succeed":true, #是否实行执行成功
    "errorCode":0,  #错误码，0为正常
    "info":"",      #描述信息
    "data":{}       #其余数据
}
```

7.关闭slam

```
api id: 1901

输入参数：
{
  "data": {
    }
}

反馈响应：
{
    "succeed":true, #是否实行执行成功
    "errorCode":0,  #错误码，0为正常
    "info":"",      #描述信息
    "data":{}       #其余数据
}
```

## 四、话题数据说明

1.建图实时点云数据话题：rt/unitree/slam\_mapping/points 数据类型：sensor\_msgs::msg::dds\_::PointCloud2\_

2.建图实时里程计数据话题：rt/unitree/slam\_mapping/odom 数据类型：nav\_msgs::msg::dds\_::Odometry\_

3.定位实时点云数据话题：rt/unitree/slam\_relocation/points 数据类型：sensor\_msgs::msg::dds\_::PointCloud2\_

4.定位实时里程计数据话题：rt/unitree/slam\_relocation/odom 数据类型：nav\_msgs::msg::dds\_::Odometry\_

5.实时广播类信息话题：rt/slam\_info 数据类型:std\_msgs::msg::dds\_::String\_

6.执行情况信息反馈话题：rt/slam\_key\_info 数据类型:std\_msgs::msg::dds\_::String\_

7.全局地图点云数据话题(仅在开始定位后发送一次，用户可通过订阅该话题获取地图数据)：rt/unitree/slam\_relocation/global\_map 数据类型：sensor\_msgs::msg::dds\_::PointCloud2\_

其中，实时广播类信息和执行情况反馈信息中的数据均为Json格式，可通过不同的字段判断和获取，具体如下：
①实时广播类信息类型(rt/slam\_info)：基础状态信息

```
{
    "type": "robot_data",  #数据类型
    "errorCode":0,         #错误码，0为正常
    "sec": 123456789,      #时间戳
    "nanosec": 987654321,
    "info":XXX,            #描述信息
    "data":{
        "motorTemp": [30.5,30.5,...],   #电机温度(单位°C)
        "motorError": [0,0,0,...],      #电机错误码
        "batteryAmp": 1000.5,           #实时电池电流值(单位mA)
        "batteryPower":10.0,            #实时电池百分比电量(单位%)
        "batteryTemp":30.5,             #实时电池温度值(单位°C)
        "batteryVol":1000.5,            #实时电池电压值(单位mV)
        "sportMode":-1,                 #运动模式,暂无
        "gaitType":-1,                  #步态，暂无
        "cpuTemp":30.5,                 #CPU核心平均温度(单位°C)
        "cpuUsage":30.5,                #CPU核心占用率(单位%)
        "cpuMemory":30.5,               #CPU内存使用率(单位%)
        "cpuFrequency":100.5            #CPU平均核心频率(单位MHz)
    }
}
```

②实时广播类信息类型(rt/slam\_info)：定位信息

```
{
    "type": "pos_info",  #数据类型 pos_info(定位过程)/mapping_info(建图过程)
    "errorCode":0,       #错误码，0为正常
    "sec": 123456789,    #时间戳
    "nanosec": 987654321,
    "info":XXX,          #描述信息
    "data":
      {
        "currentPose": { #当前位姿
          "x": 1.5,
          "y": 1.5,
          "z": 1.5,
          "q_x": 0.0,
          "q_y": 0.0,
          "q_z": 0.0,
          "q_w": 1.0
          },
         "pcdName": "test"                    #当前定位使用的地图名
         "address": "/home/unitree/test.pcd"  #当前定位使用的地图地址
      }
}
```

③实时广播类信息类型(rt/slam\_info)：控制信息

```
{
   "type": "ctrl_info", #数据类型
    "errorCode":0,      #错误码，0为正常
    "sec": 123456789,   #时间戳
    "nanosec": 987654321,
    "info":"XXX",       #描述信息
    "data":
    {
      "targetNodeName": 9999,
      "is_arrived": false,
      "startPose": {
        "x": 1.1,
        "y": 1.2,
        "z": 1.3,
        "roll": 0.0,
        "pitch": 0.0,
        "yaw": 1.2
      },
      "targetPose": {
        "x": 1.1,
        "y": 1.2,
        "z": 1.3,
        "roll": 0.0,
        "pitch": 0.0,
        "yaw": 1.2
      },
      "stateMachine": {
        "state":"follow",      # 当前状态机
        "isOpenPlan":false,
        "isBack":false,
        "isClimbStairs":false,
        "isRotate":false,
        "isPause":false,       # 是否时暂停控制状态
        "ctrName":"pid",       # 当前控制器
        "vx": 1.1,
        "vy": 1.2,
        "vyaw": 1.3
      },
      "obsInfo":{
        "state":false,         # 有无遇到障碍
        "time":0,              # 遇到障碍的时间 单位 s
      },
      "progress": {
        "used_time": 12.3,
        "last_time": 23.3,
        "completion_percentage": 0.12
      }
    }
}
```

④执行情况反馈信息(rt/slam\_key\_info)：单次任务执行反馈

```
{
   "type": "task_result",     #数据类型
    "errorCode":0,            #错误码，0为正常
    "sec": 123456789,         #时间戳
    "nanosec": 987654321,
    "info":"XXX",             #描述信息
    "data":
    {
      "targetNodeName": 9999, #任务目标点
      "is_arrived": false     #是否完成执行
    }
}
```

## 五、按键例程demo功能测试

准备工作：
(1)在NX或个人PC中安装unitree sdk2，下载地址：
[unitree\_sdk2](https://github.com/unitreerobotics/unitree_sdk2)

(2)下载并编译例程，下载地址：
[unitree\_slam\_example](https://oss-global-cdn.unitree.com/static/dd442abf94ec44f599095cb15c3e298b.zip)

```
#编译测试例程
cd /youFileAddress
mkdir build
cd build
cmake ..
make

./keyDemo eth0  #网卡名称
```

![](https://doc-cdn.unitree.com/static/2025/7/23/fceae5dce3634125b6eb87e4a84acc48_609x344.png)
