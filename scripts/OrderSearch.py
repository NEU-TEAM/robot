#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import rospy
import time
from std_msgs.msg import String, Int32, Float32
from geometry_msgs.msg import PoseStamped, Point, Quaternion
from math import copysign

class OrderSearch:
    def __init__(self):
        self.location = ""
        self.left_arm = ""
        rospy.init_node('OrderSearch', anonymous=True)
        rospy.Subscriber('order_search', String, self.orderSearchCallBack)
        self.pub_android_remote_control = rospy.Publisher("android_remote_control", String, queue_size=1)
        self.pub_text_to_voice = rospy.Publisher('text_to_voice', String, queue_size=1)
        self.pub_text_to_text = rospy.Publisher('text_to_text', String, queue_size=1)

        self.pub_leftarm = rospy.Publisher('/call/leftarm', Int32, queue_size=2)
        # self.pub_navigation = rospy.Publisher('simple_navigation', Int32, queue_size=1)
        self.pub_location = rospy.Publisher('nav_location_goal', PoseStamped, queue_size=1)

        self.location_list = ['厨房','卧室','客厅']

        self.order_dict = {	
        					'bottle':	['给我拿瓶水','给我拿杯水','递我一瓶水','递我一杯水','拿瓶水','拿杯水'],
        					'location': ['去厨房','去卧室','去客厅','来厨房','来卧室','来客厅'],
        					'leftarm':	["递我", "放手",'给我','递我吧','放手吧','给我吧']
        				  }

    def orderSearch(self, data, dictionary):
        for (key, sentences) in dictionary.iteritems():
            for sentence in sentences:
                if data == sentence:
                	if key == 'bottle':
                		pass

                	if key == 'location':
                		for location in self.location_list:
                			if sentence.find(location) != -1:
                				self.location = location

                	if key == "leftarm":
                		pass

                	return key

    def orderSearchCallBack(self, msg):
    	text_to_voice = ''
    	print(len(msg.data))
        order = self.orderSearch(msg.data[:-3], self.order_dict)

        if order == 'bottle':
            text_to_voice = "好的，我这就去拿！"
            rospy.set_param("/task", 'bottle')
            pose_stamped = PoseStamped()
            pose_stamped.header.stamp = rospy.Time.now()
            pose_stamped.header.frame_id = "map"
            pose_stamped.pose.position.x = 5.0
            pose_stamped.pose.orientation.w = 1.0
            self.pub_location.publish(pose_stamped)

        elif order == "location":
			text_to_voice = "命令已收到，我这就去" + self.location + "！"
			pose_stamped = PoseStamped()
			pose_stamped.header.stamp = rospy.Time.now()
			pose_stamped.header.frame_id = "map"
			if self.location == '厨房':
				pose_stamped.pose.position.x = 0.0
				pose_stamped.pose.orientation.w = 1.0
			elif self.location == '卧室':
				pose_stamped.pose.position.x = 0.0
				pose_stamped.pose.orientation.w = 1.0
			else:
				pose_stamped.pose.position.x = 0.0
				pose_stamped.pose.orientation.w = 1.0
			self.pub_location.publish(pose_stamped)

        elif order == 'leftarm':
            text_to_voice = "您的杯子，请拿好！"
            self.pub_leftarm.publish(2)
            self.pub_leftarm.publish(1)


        # elif order == "休息":
        #     self.sayword="大宝要去休息了，有事您再叫我！"
        #     rospy.set_param("is_ready_to_serve",False)

        else:
            pass

        if text_to_voice != "":
            if rospy.has_param("is_remote_control"):
                self.pub_android_remote_control.publish(text_to_voice + "!")
                self.pub_text_to_voice.publish(text_to_voice)
                rospy.delete_param("is_remote_control")
            else:
                self.pub_text_to_voice.publish(text_to_voice + "!")
        else:
            self.pub_text_to_text.publish(msg.data)


if __name__ == "__main__":
    try:
        OrderSearch()
        rospy.spin()
    except rospy.ROSInterruptException:
        print("OrderSearch is over!")
