#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import rospy
from std_msgs.msg import String


class RemoteControl:
    def __init__(self):
        rospy.init_node('remote_control', anonymous=True)
        rospy.Subscriber('pc_remote_control', String, self.remote_control_callback)
        self.pub_command_text = rospy.Publisher("order_text", String, queue_size=5)

    def remote_control_callback(self, msg):
        if rospy.get_param("is_ready_to_play"):
            rospy.set_param("is_ready_to_interrupt", True)
        rospy.set_param("is_remote_control", True)
        self.pub_command_text.publish(msg.data)


if __name__ == "__main__":
    try:
        RemoteControl()
        rospy.spin()
    except rospy.ROSInterruptException:
        print("remote_control is over!")
