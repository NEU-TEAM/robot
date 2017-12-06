#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import rospy
from std_msgs.msg import String, Int8
from geometry_msgs.msg import PoseStamped


class OrderSearch:
    def __init__(self):
        self.location = ""
        self.left_arm = ""
        rospy.init_node('OrderSearch', anonymous=True)
        rospy.Subscriber('/ctrl/voice/order_search', String, self.order_search_callback)
        self.pub_android_remote_control = rospy.Publisher("android_remote_control", String, queue_size=1)
        self.pub_text_to_voice = rospy.Publisher('/ctrl/voice/text_to_voice', String, queue_size=1)
        self.pub_text_to_text = rospy.Publisher('/ctrl/voice/text_to_text', String, queue_size=1)

        self.pub_left_arm = rospy.Publisher('/ctrl/voice/arm/left', Int8, queue_size=2)
        # self.pub_navigation = rospy.Publisher('simple_navigation', Int32, queue_size=1)
        self.pub_location = rospy.Publisher('/ctrl/voice/nav_location_goal', PoseStamped, queue_size=1)

        self.location_list = ['厨房', '卧室', '客厅']

        self.order_dict = {
            'fetch':   ['给我拿瓶水', '给我拿杯水', '递我一瓶水', '递我一杯水', '拿瓶水', '拿杯水'],
            'move': ['去厨房', '去卧室', '去客厅', '来厨房', '来卧室', '来客厅'],
            'deliver': ['递我', '放手', '给我', '递我吧', '放手吧', '给我吧'],
            'place':    ['放桌子上', '放桌上', '放那', '放那吧']
        }

    def order_search(self, data, dictionary):
        for (key, sentences) in dictionary.iteritems():
            for sentence in sentences:
                if data == sentence:
                    if key == 'fetch':
                        pass

                    if key == 'move':
                        for location in self.location_list:
                            if sentence.find(location) != -1:
                                self.location = location

                    if key == 'deliver':
                        pass

                    if key == 'place':
                        pass

                    return key

    def order_search_callback(self, msg):
        text_to_voice = ''
        order = self.order_search(msg.data[:-3], self.order_dict)

        if order == 'fetch':
            text_to_voice = "好的，我这就去拿！"
            # Change the task param format from /task to /voice/param/ctrl/task
            rospy.set_param("/task", 'bottle')
            pose_stamped = PoseStamped()
            pose_stamped.header.stamp = rospy.Time.now()
            pose_stamped.header.frame_id = "map"
            pose_stamped.pose.position.x = 5.0
            pose_stamped.pose.orientation.w = 1.0
            self.pub_location.publish(pose_stamped)

        elif order == "move":
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

        elif order == 'deliver':
            text_to_voice = "您的水，请拿好！"
            self.pub_left_arm.publish(2)
            self.pub_left_arm.publish(1)

        elif order == 'place':
            pass

        else:
            pass

        if text_to_voice != "":
            print(text_to_voice)
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
