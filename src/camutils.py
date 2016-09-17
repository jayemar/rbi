#!/usr/bin/env python

import cv2
import pdb

class Camera:
    def __init__(self):
        self.feed = cv2.VideoCapture(0)

    def __del__(self):
        self.feed.release()
        cv2.destroyAllWindows()

    def get_feed(self):
        return self.feed

    def get_live_stream(self):
        while(True):
            ret, frame = self.feed.read()
            return frame

