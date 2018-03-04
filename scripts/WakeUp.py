#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import rospy
import serial


# lsusb
# modprobe usbserial vendor=<0x067b> product=<0x2303>
# dmesg | grep 'ttyUSB'
# sudo chmod 777 /dev/ttyUSB0* 


class WakeUp:
    def __init__(self):
        rospy.init_node('wakeup', anonymous=True)
        self.ser = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, timeout=1, writeTimeout=0.1,
                                 stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE)
        self.ser.write('RESET\n')
        while self.ser.isOpen():
            wakeup = self.ser.readline()
            if wakeup.find('angle') != -1:
                angle = int(filter(str.isdigit, wakeup))
                print(angle)


if __name__ == "__main__":
    WakeUp()
    print("WakeUp is over!")
