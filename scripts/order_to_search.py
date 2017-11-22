#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import rospy
import time
from std_msgs.msg import String, Int32, Float32
from geometry_msgs.msg import PoseStamped, Point, Quaternion
from math import copysign

word_to_say = ""


class OrderSearch:
    def __init__(self):
        # self.name = ""
        self.location = ""
        self.left_arm = ""
        rospy.init_node('order_to_search', anonymous=True)
        self.pub_text_to_voice = rospy.Publisher('text_to_voice', String, queue_size=5)
        self.pub_android_remote_control = rospy.Publisher("android_remote_control", String, queue_size=5)
        self.pub_request = rospy.Publisher('request_text', String, queue_size=5)
        self.pub_release = rospy.Publisher("/call/open", Int32, queue_size=1)
        self.pub_reset = rospy.Publisher("/call/down", Int32, queue_size=1)
        self.pub_left_arm = rospy.Publisher('/call/leftarm', Int32, queue_size=1)
        # self.pub_navigation = rospy.Publisher('simple_navigation', Int32, queue_size=1)
        self.pub_location = rospy.Publisher('nav_location_goal', PoseStamped, queue_size=1)
        # self.pub_hello = rospy.Publisher('/call/hello', Int32, queue_size=1)
        # self.pub_bye = rospy.Publisher('/call/bye', Int32, queue_size=1)
        # self.pub_grasp = rospy.Publisher('/call/grasp', Int32, queue_size=1)
        # self.pub_release = rospy.Publisher('gripper_pos', Float32, queue_size=1)
        # self.pub_down = rospy.Publisher('call/down', Int32, queue_size=1)
        rospy.Subscriber('order_text', String, self.speech_command_callback)

        self.command_dictionary = {"杯子": ["杯子", "被子", "水杯", "那杯水", "杯水", "瓶子", "水瓶", "那瓶水", "瓶水"],
                                   "地点": ["厨房", "卧室", "客厅"],
                                   "给我": ["递我", "放手"],
                                   "leftarm": ["张开", "闭合", "复位", "前移", "后移", "左移", "右移"],
                                   # "谢谢":["谢谢"],
                                   # "故事":["故事"],
                                   # "笑话":["笑话"],
                                   # "天气":["天气"],
                                   # "欢迎":["领导来看你了", "领导来看你", "领导来了"],
                                   # "欢送":["领导走了", "领导要走了", "领导走", "领导要走"],
                                   # "hello":["hello"],
                                   # "grasp":["grasp"],
                                   # "back":["back"],
                                   # "release":["release"],
                                   # "休息":["休息", "睡觉","退下","再见"],
                                   # "功能":["功能","作用","能力","特长","做些什么"]
                                   }

    def search_order(self, data, dictionary):
        for (key, value) in dictionary.iteritems():
            for word in value:
                if data.find(word) > -1:
                    # if(key == "杯子"):
                    #     self.PoseStamped = PoseStamped(Point(5.0,0.0,0.0), Quaternion(0.0,0.0,0.0,1.0))
                    if key == "地点":
                        self.location = word
                    if key == "leftarm":
                        self.left_arm = word
                        if self.left_arm == "张开":
                            self.pub_left_arm.publish(2)
                        elif self.left_arm == "前移":
                            self.pub_left_arm.publish(3)
                        elif self.left_arm == "后移":
                            self.pub_left_arm.publish(4)
                        elif self.left_arm == "左移":
                            self.pub_left_arm.publish(5)
                        elif self.left_arm == "右移":
                            self.pub_left_arm.publish(6)
                        else:
                            self.pub_left_arm.publish(1)
                    # if(self.location == "厨房"):
                    #         self.pub_navigation.publish(1)
                    #     elif(self.location == "卧室"):
                    #         self.pub_navigation.publish(2)
                    #     else:
                    #         self.pub_navigation.publish(3)
                    return key

    def speech_command_callback(self, msg):
        order = self.search_order(msg.data, self.command_dictionary)

        if order == "杯子":
            global word_to_say
            word_to_say = "好的，我这就去拿！"
            rospy.set_param("/task", True)
            # rospy.set_param("/comm/param/control/target/is_set",True)
            # rospy.set_param("/comm/param/control/target/label","bottle")
            pose_stamped = PoseStamped()
            pose_stamped.header.stamp = rospy.Time.now()
            pose_stamped.header.frame_id = "map"
            pose_stamped.pose.position.x = 5.0
            pose_stamped.pose.orientation.w = 1.0
            self.pub_location.publish(pose_stamped)

        # elif order == "功能":      
        #     self.sayword="我是家庭服务机器人，很高兴为您服务！我可以为您拿杯水，我也可以为您讲故事！"

        elif order == "地点":
            pose_stamped = PoseStamped()
            pose_stamped.header.stamp = rospy.Time.now()
            pose_stamped.header.frame_id = "map"
            pose_stamped.pose.position.x = 0.0
            pose_stamped.pose.orientation.w = 1.0
            self.pub_location.publish(pose_stamped)
            word_to_say = "命令已收到，我这就去" + self.location + "！"

        elif order == "给我":
            word_to_say = "请拿好！"
            if rospy.has_param("is_remote_control"):
                self.pub_android_remote_control.publish(word_to_say + "!")
                self.pub_text_to_voice.publish(word_to_say)
                self.pub_left_arm.publish(2)
                time.sleep(1)
                self.pub_left_arm.publish(1)
                rospy.delete_param("is_remote_control")
            else:
                self.pub_text_to_voice.publish(word_to_say + "!")
                self.pub_left_arm.publish(2)
                time.sleep(1)
                self.pub_left_arm.publish(1)

                # elif command == "谢谢":
                #     self.sayword="不用客气,这是我应该做的！"

                # elif command == "故事":
                # 	self.sayword="一只山羊初次见到一只美丽的斑豹时，它对斑豹身上漂亮的斑纹极为喜爱，羡慕不已。于是，山羊便兴高采烈地走到斑豹面前，禁不住喜悦之情去抚摸斑豹身上美妙的斑纹。　　斑豹却对送上门来的猎物毫不留情，它凶残而又津津有味地吞食了这只可怜的山羊。　　这只山羊临死时悲叹道：“我真愚蠢，我原以为凡是美丽的东西都是善良可爱的，结果却因爱美之心葬送了自己宝贵的生命。”　　有些美丽的东西也是致命的陷阱。"

                # elif command == "笑话":
                #     self.sayword="乐队指挥，血流满面的回到家，老婆看到后心疼问：“你这是咋了？”指挥家说：“被卖油条的打了。”老婆说：“凭什么呀？”指挥家：“卖油条的说我偷了他炸油条的筷子，还拿出来显摆。”"

                # elif command == "天气":
                # 	pass
                # self.sayword="沈阳:周五 9月15日,晴 北风,最低气温7度，最高气温22度。"

        # elif command == "欢迎":      
        #     self.sayword="是吗？我这就去迎接！"
        #     self.PoseStamped = PoseStamped(Point(1.5,0.0,0.0), Quaternion(0.0,0.0,0.0,1.0))
        #     self.pub_location.publish(self.PoseStamped)

        # elif command == "欢送":      
        #     self.pub_bye.publish(0)
        #     self.sayword="相见时难别亦难，大宝代表东北大学祝您生活愉快，工作顺利,再见！"
        #     time.sleep(5)

        # elif command == "hello":      
        #     self.pub_hello.publish(0)
        #     self.sayword="各位领导，你们好,我是来自东北大学的家庭服务机器人大宝，很高兴为您服务！"
        #     time.sleep(5)

        # elif command == "grasp":
        # 	self.sayword="。"
        # 	self.pub_grasp.publish(0)

        # elif command == "back":
        # 	self.sayword="yeah，我拿到了，这就往回返！"
        # 	self.PoseStamped = PoseStamped(Point(1.5,0.0,0.0), Quaternion(0.0,0.0,0.0,1.0))
        # 	self.pub_location.publish(self.PoseStamped)

        # elif command == "release":
        # 	self.sayword="您的水，请拿好！"
        # 	self.pub_release.publish(0.78)
        # 	self.pub_down.publish(0)

        # elif order == "休息":
        #     self.sayword="大宝要去休息了，有事您再叫我！"
        #     rospy.set_param("is_ready_to_serve",False)

        else:
            pass

        if word_to_say != "":
            if rospy.has_param("is_remote_control"):
                self.pub_android_remote_control.publish(word_to_say + "!")
                self.pub_text_to_voice.publish(word_to_say)
                rospy.delete_param("is_remote_control")
            else:
                self.pub_text_to_voice.publish(word_to_say + "!")
        else:
            self.pub_request.publish(msg.data)


if __name__ == "__main__":
    try:
        OrderSearch()
        rospy.spin()
    except rospy.ROSInterruptException:
        print("order_to_search is over!")
