#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import rospy
from std_msgs.msg import String


class FeedbackOfTask:
    def __init__(self):
        rospy.init_node('feedback_of_task', anonymous=True)
        rospy.Subscriber('/task_status', String, self.feedback_of_task_callback)

    @staticmethod
    def feedback_of_task_callback(msg):
        if msg.data == "Goal_succeeded" and rospy.has_param("/task"):
            rospy.set_param("/comm/param/control/target/is_set", True)
            rospy.set_param("/comm/param/control/target/label", "bottle")
            rospy.delete_param("/task")


if __name__ == "__main__":
    try:
        FeedbackOfTask()
        rospy.spin()
    except rospy.ROSInterruptException:
        print("feedback_of_task is over!")
