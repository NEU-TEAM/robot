#!/usr/bin/env python
#-*- coding: UTF-8 -*- 

import rospy
import actionlib
from std_msgs.msg import Int32
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal

class SimpleNavigation:

    def __init__(self):
        rospy.init_node('SimpleNavigation', anonymous=True) 
        self.navigation_client = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        self.goal = MoveBaseGoal()
        self.goal.target_pose.header.frame_id = "map"
        self.goal.target_pose.header.stamp = rospy.Time.now()
        rospy.Subscriber('simple_navigation', Int32, self.simple_navigation_callback)


    def simple_navigation_callback(self, msg):
    	destination = msg.data
    	if(destination == 1):
            self.goal.target_pose.pose.position.x = 1.8522837162
            self.goal.target_pose.pose.position.y = -1.59520244598
            self.goal.target_pose.pose.orientation.w = 1.0

    	elif(destination == 2):
            self.goal.target_pose.pose.position.x = 0.765163183212
            self.goal.target_pose.pose.position.y = -5.37232589722
            self.goal.target_pose.pose.orientation.w = 1.0

    	else:
            self.goal.target_pose.pose.position.x = -2.03596353531
            self.goal.target_pose.pose.position.y = -0.625330209732
            self.goal.target_pose.pose.orientation.w = 1.0

    	self.navigation_client.send_goal(self.goal)
    	finished_before_timeout = self.navigation_client.wait_for_result(rospy.Duration(60.0))
    	if (finished_before_timeout):
    		print("Action finished!");
    	else:
    		print("Action did not finish before the time out.");


if __name__=="__main__":
    try:
        SimpleNavigation()
        rospy.spin()
    except rospy.ROSInterruptException:
        print("SimpleNavigation is over!")