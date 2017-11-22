#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import rospy
from std_msgs.msg import String
import urllib
import json


class TextToText:
    def __init__(self):
        rospy.init_node('text_to_text', anonymous=True)
        self.response_text = ""
        self.key = 'a9c913f6e8f146a19ee8b40eca9cee03'
        self.user_id = '102043'
        self.loc = '辽宁省沈阳市'
        self.request = 'http://www.tuling123.com/openapi/api?key=' + self.key + '&loc=' + self.loc + '&userid=' \
                       + self.user_id + '&info='
        self.pub_text_to_voice = rospy.Publisher("text_to_voice", String, queue_size=5)
        self.pub_android_remote_control = rospy.Publisher("android_remote_control", String, queue_size=5)
        rospy.Subscriber("request_text", String, self.turing_callback)

    def turing_callback(self, msg):
        url = self.request + msg.data
        response = urllib.urlopen(url)
        text_str = response.read()
        text_json = json.loads(text_str)
        self.response_text = text_json["text"]
        print(self.response_text)
        if rospy.has_param("is_remote_control"):
            self.pub_android_remote_control.publish(self.response_text)
            self.pub_text_to_voice.publish(self.response_text)
            rospy.delete_param("is_remote_control")
        else:
            self.pub_text_to_voice.publish(self.response_text)


if __name__ == "__main__":
    try:
        TextToText()
        rospy.spin()
    except rospy.ROSInterruptException:
        print("text_to_text is over!")
