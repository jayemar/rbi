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


def show_blue(f, tolerance=0.10):
    #cv2.cvtColor(f, cv2.COLOR_BGR2HSV, dst=f)
    #cv2.cvtColor(f, cv2.COLOR_BGR2HLS, dst=f)

    f = imgutils.get_color_mask(f, "052C72", tolerance)
    return f


def angle2hex(a):
    return (a/360.0) * 255


while(True):
    step_count += 1

    # Capture frame-by-frame
    ret, frame = feed.read()
    if not ret: continue

    mask = show_blue(frame, 0.25)
    cv2.imshow('Blue Mask', mask)

    blurred = cv2.bilateralFilter(mask, 11, 17, 17)
    cv2.imshow('Blurred', blurred)

    edged = cv2.Canny(blurred, 30, 200)
    cv2.imshow('Edged', edged)

    if cv2.waitKey(1) & 0xFF == ord('1'):
        break


# When everything is done, release the capture
feed.release()
cv2.destroyAllWindows()
