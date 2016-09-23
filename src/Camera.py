#!/usr/bin/env python

"""
Uses the 'uvcdynctrl' utility to control an attached USB webcam
"""

import cv2
import numpy
import subprocess
import pdb

class Camera:
    def __init__(self):
        pass

    def __del__(self):
        self.feed.release()
        cv2.destroyAllWindows()

    def get_feed(self):
        self.feed = cv2.VideoCapture(0)
        return self.feed

    def get_live_stream(self):
        while(True):
            ret, frame = self.feed.read()
            return frame


    def get_brightness(self):
        return self.__uvc("Brightness").strip()

    def set_brightness(self, b):
        self.__uvc("Brightness", b)

    def get_contrast(self):
        return self.__uvc("Contrast").strip()

    def set_contrast(self, b):
        self.__uvc("Contrast", b)

    def get_saturation(self):
        return self.__uvc("Saturation").strip()

    def set_saturation(self, b):
        self.__uvc("Saturation", b)

    def get_focus(self):
        return self.__uvc("Focus (absolute)").strip()

    def set_focus(self, b):
        self.__uvc("Focus, Auto", 0)
        self.__uvc("Focus (absolute)", b)

    def auto_focus(self):
        self.__uvc("Focus, Auto", 1)


    def get_sharpness(self):
        return self.__uvc("Sharpness").strip()

    def set_sharpness(self, b):
        self.__uvc("Sharpness", b)


    def __uvc(self, cmd, val=None):
        if val:
            resp = subprocess.check_output(["uvcdynctrl", "-s", cmd, str(val)])
        else:
            resp = subprocess.check_output(["uvcdynctrl", "-g", cmd])
        return resp

