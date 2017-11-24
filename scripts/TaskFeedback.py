#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import rospy
from std_msgs.msg import String


class TaskFeedback:
    def __init__(self):
        rospy.init_node('TaskFeedback', anonymous=True)
        rospy.Subscriber('/ctrl/voice//task_status', String, self.task_feedback_callback)

    @staticmethod
    def task_feedback_callback(msg):
    	task = rospy.get_param('/task')
        if msg.data == "Goal_succeeded" and task == 'bottle':
            rospy.set_param("/comm/param/control/target/is_set", True)
            rospy.set_param("/comm/param/control/target/label", "bottle")
            rospy.delete_param("/task")


if __name__ == "__main__":
    try:
        TaskFeedback()
        rospy.spin()
    except rospy.ROSInterruptException:
        print("TaskFeedback is over!")
