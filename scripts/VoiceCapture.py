#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import rospy
from pyaudio import PyAudio, paInt16
import numpy as np
import wave

captured_voice = '/robot/wav/capturedVoice.wav'

param_is_ready_to_capture = '/comm/param/ctrl/is_ready_to_capture'
param_is_ready_to_serve = '/comm/param/ctrl/is_ready_to_serve'
param_is_ready_to_translate = '/voice/param/is_ready_to_translate'


def voice_capture():
    num_samples = 2000  # pyaudio内置缓冲大小
    sampling_rate = 16000  # 取样频率
    level = 2000  # 声音保存的阈值
    count_num = 15  # NUM_SAMPLES个取样之内出现COUNT_NUM个大于LEVEL的取样则记录声音
    save_length = 4  # 声音记录的最小长度：save_length * num_samples 个取样
    min_length = 7

    dev_to_capture = PyAudio()
    stream = dev_to_capture.open(format=paInt16, channels=1, rate=sampling_rate,
                                 input=True, frames_per_buffer=num_samples)
    save_count = 0
    save_buffer = []
    length = 0

    while True:
        string_audio_data = stream.read(num_samples)
        audio_data = np.fromstring(string_audio_data, dtype=np.short)
        large_sample_count = np.sum(audio_data > level)

        if large_sample_count > count_num:
            save_count = save_length
        else:
            save_count -= 1

        if save_count > 0:
            save_buffer.append(string_audio_data)
            length += 1

        else:
            if length > min_length:
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
                return True
            else:
                save_count = 0
                length = 0
            save_buffer = []


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
