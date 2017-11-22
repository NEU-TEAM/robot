// #include "ros/ros.h"
// #include "std_msgs/String.h"

// #include "/mengjia/inc/api/mraa.hpp"

// #include <stdlib.h>
// #include <stdio.h>
// #include <unistd.h>
// #include <time.h>
// #include <string.h>
// #include <unistd.h>
// #include <iostream>

// mraa::Uart * dev;
// bool is_ready_to_serve = false;

// void Init_uart(void)
// {
//     try 
//     {
//         dev = new mraa::Uart("/dev/ttyUSB0");
//     } 
//     catch (std::exception& e) 
//     {
//         std::cout << "Error while setting up raw UART" << std::endl;
//         std::terminate();
//     }
//     if (dev->setBaudRate(115200) != mraa::SUCCESS) 
//     {
//         std::cout << "Error setting parity on UART" << std::endl;
//     }
//     if (dev->setMode(8, mraa::UART_PARITY_NONE, 1) != mraa::SUCCESS) 
//     {
//         std::cout << "Error setting parity on UART" << std::endl;
//     }   
//     if (dev->setFlowcontrol(false, false) != mraa::SUCCESS) 
//     {
//         std::cout << "Error setting flow control UART" << std::endl;
//     }
//     dev->writeStr("RESET\n");
// }

// int main(int argc,char** argv)
// {
//     ros::init(argc,argv,"wakeup");
//     ros::NodeHandle n;
//     ros::Rate rate(10);
//     ros::Publisher pub = n.advertise<std_msgs::String>("text_to_voice",10);
//     std_msgs::String wakeup;
//     wakeup.data = "家庭服务机器人已唤醒，请问您：有何吩咐？";
//     Init_uart();
//     ros::param::set("is_ready_to_serve",false);
//     using namespace std;
//     string s;
//     int i;
//     while(ros::ok())
//     {
//     	ros::param::get("/is_ready_to_serve", is_ready_to_serve);
//         if(dev->dataAvailable() && !is_ready_to_serve)
//         {
//             pub.publish(wakeup);
//             ros::param::set("is_ready_to_serve",true);
//         }
//         rate.sleep();
//     }
//     return 0;
// }


#include <iostream>
#include <mraa.hpp>
#include "ros/ros.h"
#include "std_msgs/String.h"
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <time.h>
#include <string.h>
#include <unistd.h>

std::string wakeup_word;
mraa::Uart *dev=NULL;
 void Init_uart(void)
{
    try {
        dev = new mraa::Uart("/dev/ttyUSB0");
        } 
    catch (std::exception& e) 
    {
        std::cout << "Error while setting up raw UART" << std::endl;
        std::terminate();
    }
    if (dev->setBaudRate(115200) != mraa::SUCCESS) 
    {
        std::cout << "Error setting parity on UART" << std::endl;
    }
    if (dev->setMode(8, mraa::UART_PARITY_NONE, 1) != mraa::SUCCESS) 
    {
        std::cout << "Error setting parity on UART" << std::endl;
    }   
     if (dev->setFlowcontrol(false, false) != mraa::SUCCESS) 
     {
        std::cout << "Error setting flow control UART" << std::endl;
     }
    dev->writeStr("RESET\n");
}

void random_response_sleep()
{
        srand((unsigned)time(NULL));
        int X=1;
        int Y=5;       
        int key = rand()%(Y-X+1)+X;
        switch(key)
            {
        case 1:
            wakeup_word = "很高兴见到您!";
            break;
        case 2:
            wakeup_word = "请问有何吩咐?";
            break;
        case 3:
            wakeup_word = "亲，有什么可以帮助您的吗?";
            break;
        case 4:
            wakeup_word = "很高兴为您服务!";
            break;
        case 5:
            wakeup_word = "嗯哪，我在呢";
            break;
        default:
            wakeup_word =  "您好!";
            break;
          } 
}

int main(int argc,char** argv)
{
    int i;
    std_msgs::String msg_wakeup_angle;
    std_msgs::String msg_wakeup_response;
    ros::init(argc,argv,"wakeup_to_serve");
    ros::NodeHandle n;
    ros::Rate loop(10);
    ros::Publisher pub_wakeup_angle=n.advertise<std_msgs::String>("/voice/wakeup_angle",10);
    ros::Publisher pub_wakeup_response= n.advertise<std_msgs::String>("/voice/wakeup_response",10);
    Init_uart();
    ros::param::set("/voice/xfy_ready_sign",true);//讯飞板初始化成功
     while(ros::ok())
     {
         if(dev->dataAvailable())
         {
             std::string s;
             while(dev->dataAvailable())
             {
                 s+=dev->readStr(1);
              }
             i=s.find("WAKE UP!angle:");
 //            std::cout<<"uart Init OK"<<std::endl;
             if(ros::param::has("/voice/xfy_ready_sign"))
             {
                ros::param::set("/voice/xfy_ready_reminder",true);//初始化成功反馈信号，播放提示音，见playmusic.cpp
                ros::param::del("/voice/xfy_ready_sign");
             }
             if(i!=std::string::npos)
             {
                 std::stringstream ss;
                 ss <<s.substr(i+14,3);//获取唤醒角度
                 msg_wakeup_angle.data = ss.str();
                 //std::cout<<"wakeup angle:"<<ss.str()<<std::endl;
                 pub_wakeup_angle.publish(msg_wakeup_angle);//发布唤醒角度
                 random_response_sleep();//随机选取暖场词
                 msg_wakeup_response.data=wakeup_word;
                 ros::param::set("/is_ready_to_serve",true);//唤醒信号作为语音打断信号
                 if(!ros::param::has("/voice/wakeup"))//判断当前是否处于唤醒状态。未唤醒时发布唤醒信号；已经唤醒时不发布唤醒信号，当成语音打断。
                 {
                        pub_wakeup_response.publish(msg_wakeup_response);//发布唤醒信号给speaker节点
                 }
//                dev->writeStr("BEAM 2\n");
 //                dev->writeStr("RESET\n");
             }
         }
         if(ros::param::has("/voice/voice_sleep"))//检测是否有“休眠命令”
                dev->writeStr("RESET\n");//设置休眠
            
         ros::spinOnce();
         loop.sleep();
      }

}