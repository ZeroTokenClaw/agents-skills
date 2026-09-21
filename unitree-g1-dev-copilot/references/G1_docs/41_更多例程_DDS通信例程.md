# 消息发布示例

Source: <https://support.unitree.com/home/zh/G1_developer/dds_communication_routine>

DDS 相关知识和通信接口说明，请查阅上文 [《DDS通信接口》](https://support.unitree.com/home/zh/G1_developer/dds_services_interface)
以下是 unitree\_sdk2 在DDS上做了一层封装后的消息发布/订阅示例。

## 消息发布示例

例程路径： `unitree_sdk2/example/helloworld/publisher.cpp`

```
#include <unitree/robot/channel/channel_publisher.hpp>
#include <unitree/common/time/time_tool.hpp>
#include "HelloWorldData.hpp"

#define TOPIC "TopicHelloWorld"

using namespace unitree::robot;
using namespace unitree::common;

int main(int argc, char **argv)
{
    if (argc < 2)
    {
      std::cout << "Usage: " << argv[0] << " networkInterface" << std::endl;
      exit(-1);
    }
    unitree::robot::ChannelFactory::Instance()->Init(0, argv[1]);
    //argv[1]由终端传入，为机器人连接的网卡名称

    /*
     * New ChannelPublisherPtr
     */
    ChannelPublisherPtr<HelloWorldData::Msg> publisher = ChannelPublisherPtr<HelloWorldData::Msg>(new ChannelPublisher<HelloWorldData::Msg>(TOPIC));

    /*
     * Init channel
     */
    publisher->InitChannel();

    while (true)
    {
        /*
         * Send message
         */
        HelloWorldData::Msg msg(unitree::common::GetCurrentTimeMillisecond(), "HelloWorld.");
        publisher->Write(msg);
        sleep(1);
    }

    return 0;
}
```

## 消息订阅示例

例程路径： `unitree_sdk2/example/helloworld/subscriber.cpp`

```
#include <unitree/robot/channel/channel_subscriber.hpp>
#include "HelloWorldData.hpp"

#define TOPIC "TopicHelloWorld"

using namespace unitree::robot;
using namespace unitree::common;

void Handler(const void* msg)
{
    const HelloWorldData::Msg* pm = (const HelloWorldData::Msg*)msg;

    std::cout << "userID:" << pm->userID() << ", message:" << pm->message() << std::endl;
}

int main()
{
    /*
     * Init with defalue domain 0.
     */
    ChannelFactory::Instance()->Init(0);

    /*
     * New ChannelSubscriberPtr
     */
    ChannelSubscriberPtr<HelloWorldData::Msg> subscriber = ChannelSubscriberPtr<HelloWorldData::Msg>(new ChannelSubscriber<HelloWorldData::Msg>(TOPIC));

    /*
     * Init channel
     */
    subscriber->InitChannel(std::bind(Handler, std::placeholders::_1), 1);

    sleep(5);

    /*
     * Close channel
     */
    subscriber->CloseChannel();

    std::cout << "reseted. sleep 3" << std::endl;

    sleep(3);

    /*
     * Init channel use last input parameter.
     */
    subscriber->InitChannel();

    /*
     * Loop wait message.
     */
    while (true)
    {
        sleep(10);
    }

    return 0;
}
```
