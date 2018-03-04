#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import rospy
from pyaudio import PyAudio, paInt16
import numpy as np
import wave
import os

path_prefix = os.path.abspath('..')

captured_voice = path_prefix + '/catkin_ws/src/robot/robot/wav/capturedVoice.wav'

param_is_ready_to_capture = '/comm/param/ctrl/is_ready_to_capture'
param_is_ready_to_serve = '/comm/param/ctrl/is_ready_to_serve'
param_is_ready_to_translate = '/voice/param/is_ready_to_translate'


def voice_capture():
    flag = False
    num_samples = 2000  # pyaudio内置缓冲大小
    sampling_rate = 16000  # 取样频率
    level = 2000  # 声音保存的阈值
    count_num_amp1 = 10
    count_num_amp2 = 15
    silence_length = 4
    min_length = 7

    dev_to_capture = PyAudio()
    stream = dev_to_capture.open(format=paInt16, channels=1, rate=sampling_rate,
                                 input=True, frames_per_buffer=num_samples)
    save_count = 0
    save_buffer = []
    length = 0
    silence = 0

    while True:
        string_audio_data = stream.read(num_samples)
        audio_data = np.fromstring(string_audio_data, dtype=np.short)
        large_sample_count = np.sum(audio_data > level)

        if not flag:
            if large_sample_count < count_num_amp1:
                save_buffer = []
                length = 0
            elif count_num_amp1 < large_sample_count < count_num_amp2:
                save_buffer.append(string_audio_data)
                length += 1
            else:
                save_buffer.append(string_audio_data)
                length += 1
                flag = True
                silence = 0
        else:
            if large_sample_count > count_num_amp1:
                save_buffer.append(string_audio_data)
                length += 1
            else:
                silence += 1
                if silence < silence_length:
                    save_buffer.append(string_audio_data)
                    length += 1
                elif length < min_length:
                    flag = False
                    length = 0
                    save_buffer = []
                    silence = 0
                else:
                    voice_string = save_buffer
                    wf = wave.open(captured_voice, 'wb')
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(sampling_rate)
                    wf.writeframes(np.array(voice_string).tostring())
                    wf.close()
                    stream.stop_stream()
                    stream.close()
                    dev_to_capture.terminate()
                    print("Recorded a piece of voice successfully!")
                    rospy.set_param(param_is_ready_to_capture, False)
                    rospy.set_param(param_is_ready_to_translate, True)
                    flag = False
                    length = 0
                    save_buffer = []
                    silence = 0
                    return True


if __name__ == '__main__':
    rospy.init_node('voice_capture', anonymous=True)
    rate = rospy.Rate(10)  # 10hz

    while not rospy.is_shutdown():
        is_ready_to_serve = rospy.get_param(param_is_ready_to_serve)
        is_ready_to_capture = rospy.get_param(param_is_ready_to_capture)
        if is_ready_to_serve and is_ready_to_capture:
            print("Recording a piece of voice!")
            voice_capture()
        rate.sleep()
        
    print("Voice capture is over!")
