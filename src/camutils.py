#!/usr/bin/env python

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
        self.__uvc("Brightness")

    def set_brightness(self, b):
        self.__uvc("Brightness", b)

    def get_contrast(self):
        self.__uvc("Contrast")

    def set_contrast(self, b):
        self.__uvc("Contrast", b)

    def get_saturation(self):
        self.__uvc("Saturation")

    def set_saturation(self, b):
        self.__uvc("Saturation", b)

    def get_focus(self):
        self.__uvc("Focus (absolute)")

    def set_focus(self, b):
        self.__uvc("Focus, Auto", 0)
        self.__uvc("Focus (absolute)", b)

    def auto_focus(self):
        self.__uvc("Focus, Auto", 1)


    def get_sharpness(self):
        self.__uvc("Sharpness")

    def set_sharpness(self, b):
        self.__uvc("Sharpness", b)


    def __uvc(self, cmd, val=None):
        if val:
            resp = subprocess.call(["uvcdynctrl", "-s", cmd, str(val)])
        else:
            resp = subprocess.call(["uvcdynctrl", "-g", cmd])
        return resp

