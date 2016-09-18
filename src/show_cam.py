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



while(True):
    step_count += 1

    # Capture frame-by-frame
    ret, frame = feed.read()
    if not ret: continue

    cv2.imshow('Camera View', frame)

    if cv2.waitKey(1) & 0xFF == ord('1'):
        break


# When everything is done, release the capture
feed.release()
cv2.destroyAllWindows()
