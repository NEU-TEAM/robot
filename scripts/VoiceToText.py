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

is_ready_to_translate = False
is_ready_to_play = False
capturedVoice = "/robot/wav/capturedVoice.wav"


class VoiceToText:
    def __init__(self):
        rospy.init_node('VoiceToText', anonymous=True)
        self.recognized_result = ''
        self.VoiceToText_url = 'http://vop.baidu.com/server_api'
        self.apiKey = "1GQyi2TtlQc1xmkAkiaHzNtL"
        self.secretKey = "mcdf5t6QZWNHzGbwFkhjm5nT3KuKrMyf"
        self.auth_url = "https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=" + self.apiKey + "&client_secret=" + self.secretKey;
        self.access_token = self.getToken()
        self.cuid = uuid.UUID(int=uuid.getnode()).hex[-12:]
        self.pub_order_search = rospy.Publisher('order_search', String, queue_size=1)

        while not rospy.is_shutdown():
            is_ready_to_translate = rospy.get_param("is_ready_to_translate")
            if is_ready_to_translate:
                result_translation = self.voiceToText()
                print result_translation

                if result_translation == '':
                    os.remove(capturedVoice)
                    rospy.set_param('is_ready_to_translate', False)
                    rospy.set_param('is_ready_to_capture', True)
                    continue
                is_ready_to_play = rospy.get_param('is_ready_to_play')
                if is_ready_to_play:
                    rospy.set_param('is_ready_to_interrupt', True)
                rospy.set_param('is_ready_to_remind', True)
                self.recognized_result = result_translation
                self.pub_order_search.publish(self.recognized_result)
                os.remove(capturedVoice)
                rospy.set_param('is_ready_to_translate', False)
                rospy.set_param('is_ready_to_capture', True)

    def getToken(self):
        res = urllib2.urlopen(self.auth_url)
        json_data = res.read()
        return json.loads(json_data)['access_token']

    def voiceToText(self):
        wav_fp = open(capturedVoice, 'rb')
        voice_data = wav_fp.read()
        data = {'format': 'wav', 'rate': 16000, 'channel': 1, 'cuid': self.cuid, 'token': self.access_token,'lan': 'zh', 'len': len(voice_data), 'speech': base64.b64encode(voice_data).decode('utf-8')}
        result = requests.post(self.VoiceToText_url, data=json.dumps(data), headers={'Content-Type': 'application/json'}, stream=False)
        data_result = result.json()
        if data_result['err_no'] == 0:
            return data_result['result'][0]
        else:
            return ''


if __name__ == "__main__":
    VoiceToText()
    print("VoiceToText is over!")
