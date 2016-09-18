#!/usr/bin/env python

import camutils
import imgutils
import Perspective

import cv2
import numpy as np
import pdb
import time

from pprint import pprint as pp

camera = camutils.Camera()
feed = camera.get_feed()

good_M = None
max_height = None
max_width = None

step_count = 0
MATRIX_HEIGHT = 84
MATRIX_WIDTH = 84
ratio = 1.0
screenCnt = None


def show_blue(f):
    #f = cv2.inRange(f, (100, 0, 255), (255, 255, 255))

    cv2.cvtColor(f, cv2.COLOR_BGR2HSV, dst=f)
    #f = cv2.inRange(f, (100, 0, 100), (255, 255, 255))

    #cv2.cvtColor(f, cv2.COLOR_BGR2HLS, dst=f)
    #f = cv2.inRange(f, (0, 100, 100), (255, 255, 255))



    return f

def angle2hex(a):
    return (a/360.0) * 255

while(True):
    step_count += 1

    # Capture frame-by-frame
    ret, frame = feed.read()
    if not ret: continue

    frame = show_blue(frame)

    cv2.imshow('Camera View', frame)

    if cv2.waitKey(1) & 0xFF == ord('1'):
        break


# When everything is done, release the capture
feed.release()
cv2.destroyAllWindows()
