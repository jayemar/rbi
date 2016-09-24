#!/usr/bin/env python

from lib import camera
from lib import camutils
from lib import imgutils

import cv2
import numpy as np
import pdb
import time

from pprint import pprint as pp

camera = camera.Camera()
feed = camera.get_feed()

good_M = None
max_height = None
max_width = None

step_count = 0
MATRIX_HEIGHT = 84
MATRIX_WIDTH = 84
ratio = 1.0
screenCnt = None


while(True):
    step_count += 1

    # Capture frame-by-frame
    ret, frame = feed.read()
    if not ret: continue

    cv2.imshow('Raw Frame', frame)

    mask = imgutils.get_color_mask(frame, "052C72", 0.25)
    cv2.imshow('Blue Mask', mask)

    blurred = cv2.bilateralFilter(mask, 11, 17, 17)
    cv2.imshow('Blurred', blurred)

    edged = cv2.Canny(blurred, 30, 200)
    cv2.imshow('Edged', edged)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('1'):
        break
    elif key == ord('2'):
        b = int(camera.get_brightness())
        new_b = b - 5
        camera.set_brightness(new_b)
        print("Brightness set to %d" % new_b)
    elif key == ord('3'):
        b = int(camera.get_brightness())
        new_b = b + 5
        camera.set_brightness(new_b)
        print("Brightness set to %d" % new_b)



# When everything is done, release the capture
feed.release()
cv2.destroyAllWindows()
