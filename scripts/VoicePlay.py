#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import rospy
import pyaudio
import wave
import os

path_prefix = os.path.abspath('..') + '/catkin_ws/src/robot/robot/wav/'

onVoice = path_prefix + 'on.wav'
offVoice = path_prefix + 'off.wav'
remindVoice = path_prefix + 'remindVoice.wav'
synthesizedVoice = path_prefix + 'synthesizedVoice.wav'

param_is_ready_to_serve = '/comm/param/ctrl/is_ready_to_serve'
param_is_ready_to_remind = '/voice/param/is_ready_to_remind'
param_is_ready_to_play = '/voice/param/is_ready_to_play'
param_is_ready_to_interrupt = '/voice/param/is_ready_to_interrupt'


def voice_remind(sound_file):
    wave_file = wave.open(sound_file, 'rb')
    dev_to_play = pyaudio.PyAudio()
    stream = dev_to_play.open(format=dev_to_play.get_format_from_width(wave_file.getsampwidth()),
                              channels=wave_file.getnchannels(), rate=wave_file.getframerate(), output=True)

    while True:
        data = wave_file.readframes(500)  # 从音频流中读取1000个采样数据，data类型为str.注意对音频流的读写都是字符串
        if data == '':
            break
        stream.write(data)

    wave_file.close()
    rospy.set_param(param_is_ready_to_remind, False)
    stream.stop_stream()
    stream.close()
    dev_to_play.terminate()


def voice_play():
    wave_file = wave.open(synthesizedVoice, 'rb')
    dev_to_play = pyaudio.PyAudio()
    stream = dev_to_play.open(format=dev_to_play.get_format_from_width(wave_file.getsampwidth()),
                              channels=wave_file.getnchannels(), rate=wave_file.getframerate(), output=True)
    while True:
        is_ready_to_interrupt = rospy.get_param(param_is_ready_to_interrupt)
        if is_ready_to_interrupt:
            break
        data = wave_file.readframes(500)  # 从音频流中读取1000个采样数据，data类型为str.注意对音频流的读写都是字符串
        if data == '':
            break
        stream.write(data)

    wave_file.close()
    rospy.set_param(param_is_ready_to_interrupt, False)
    rospy.set_param(param_is_ready_to_play, False)
    stream.stop_stream()
    stream.close()
    dev_to_play.terminate()


if __name__ == '__main__':
    rospy.init_node('VoicePlay', anonymous=True)

    while not rospy.is_shutdown():
        is_ready_to_remind = rospy.get_param(param_is_ready_to_remind)
        is_ready_to_play = rospy.get_param(param_is_ready_to_play)
        is_ready_to_serve = rospy.get_param(param_is_ready_to_serve)
        if is_ready_to_serve:
            voice_remind(onVoice)
        else:
            voice_remind(offVoice)
        if is_ready_to_remind:
            voice_remind(remindVoice)
        if is_ready_to_play:
            voice_play()
            
    print("VoicePlay is over!")
