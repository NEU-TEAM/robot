#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import rospy
from std_msgs.msg import String


class RemoteControl:
    def __init__(self):
        rospy.init_node('RemoteControl', anonymous=True)
        rospy.Subscriber('pc_remote_control', String, self.remoteControlCallBack)
        self.pub_order_search = rospy.Publisher("order_search", String, queue_size=1)

    def remoteControlCallBack(self, msg):
        if rospy.get_param("is_ready_to_play"):
            rospy.set_param("is_ready_to_interrupt", True)
        rospy.set_param("is_remote_control", True)
        self.pub_order_search.publish(msg.data)


if __name__ == "__main__":
    try:
        RemoteControl()
        rospy.spin()
    except rospy.ROSInterruptException:
        print("RemoteControl is over!")
