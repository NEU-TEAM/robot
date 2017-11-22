#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import rospy
from std_msgs.msg import String
import os
import urllib2
import json
import uuid
import base64
import requests

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

is_ready_to_translate = False
is_ready_to_play = False
captured_voice = "/robot/wav/captured_voice.wav"


class voice_to_text:
    def __init__(self):
        rospy.init_node('voice_to_text', anonymous=True)
        self.recognized_result = ''
        self.voice_to_text_url = 'http://vop.baidu.com/server_api'
        self.apiKey = "1GQyi2TtlQc1xmkAkiaHzNtL"
        self.secretKey = "mcdf5t6QZWNHzGbwFkhjm5nT3KuKrMyf"
        self.auth_url = "https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=" + self.apiKey + "&client_secret=" + self.secretKey;
        self.access_token = self.get_token()
        self.cuid = uuid.UUID(int=uuid.getnode()).hex[-12:]
        self.pub_command_text = rospy.Publisher('order_text', String, queue_size=5)

        while not rospy.is_shutdown():
            is_ready_to_translate = rospy.get_param("is_ready_to_translate")
            if is_ready_to_translate:
                result_translation = self.baidu_voice_to_text()
                print result_translation

                if result_translation == '':
                    os.remove(captured_voice)
                    rospy.set_param('is_ready_to_translate', False)
                    rospy.set_param('is_ready_to_capture', True)
                    continue
                is_ready_to_play = rospy.get_param('is_ready_to_play')
                if is_ready_to_play:
                    rospy.set_param('is_ready_to_interrupt', True)
                rospy.set_param('is_ready_to_remind', True)
                self.recognized_result = result_translation
                self.pub_command_text.publish(self.recognized_result)
                os.remove(captured_voice)
                rospy.set_param('is_ready_to_translate', False)
                rospy.set_param('is_ready_to_capture', True)

    def get_token(self):
        res = urllib2.urlopen(self.auth_url)
        json_data = res.read()
        return json.loads(json_data)['access_token']

    def baidu_voice_to_text(self):
        wav_fp = open(captured_voice, 'rb')
        voice_data = wav_fp.read()
        data = {'format': 'wav', 'rate': 16000, 'channel': 1, 'cuid': self.cuid, 'token': self.access_token,
                'lan': 'zh', 'len': len(voice_data), 'speech': base64.b64encode(voice_data).decode('utf-8')}
        result = requests.post(self.voice_to_text_url, json=data, headers={'Content-Type': 'application/json'},
                               stream=False)
        data_result = result.json()
        print data_result
        if data_result['err_no'] == 0:
            return data_result['result'][0]
        else:
            return ''


if __name__ == "__main__":
    voice_to_text()
    print("voice_to_text is over!")
