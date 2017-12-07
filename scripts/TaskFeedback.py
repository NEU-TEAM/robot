#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import rospy
from std_msgs.msg import Int8


param_task = '/voice/param/task'

topic_base_task_status = '/comm/voice/ctrl/task_status'


class TaskFeedback:
    def __init__(self):
        rospy.init_node('TaskFeedback', anonymous=True)
        rospy.Subscriber(topic_base_task_status, Int8, self.task_feedback_callback)

    @staticmethod
    def task_feedback_callback(msg):
        task = rospy.get_param(param_task)
        if msg.data == 1 and task == 'bottle':
            rospy.set_param("/comm/param/control/target/is_set", True)
            rospy.set_param("/comm/param/control/target/label", "bottle")
            rospy.delete_param(param_task)


if __name__ == "__main__":
    try:
        TaskFeedback()
        rospy.spin()
    except rospy.ROSInterruptException:
        print("TaskFeedback is over!")
