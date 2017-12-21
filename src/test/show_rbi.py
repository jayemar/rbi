#!/usr/bin/env python

import cv2
import sys

sys.path.append('..')

from lib import camera
from lib import camutils

camera = camera.Camera()
feed = camera.feed

good_M = None
max_height = None
max_width = None

step_count = 0
MATRIX_HEIGHT = 84
MATRIX_WIDTH = 84
ratio = 1.0
screenCnt = None
blue_hex = "063793"

IMG_MAP = {'original': True, 'mask': False, 'edges': False, 'neural': False}


while(True):
    step_count += 1

    # Capture frame-by-frame
    ret, frame = feed.read()
    if not ret:
        continue
    orig = frame.copy()

    p = camutils.get_perspective(feed, blue_hex, 0.35, IMG_MAP)
    print("P: %s" % str(p))
    if not p:
        continue

    screenCnt = p['c']
    M = p['M']
    max_width = p['w']
    max_height = p['h']

    # Warp the perspective to grab the screen
    warp = cv2.warpPerspective(orig, M, (max_width, max_height))
    cv2.imshow('R.B.I. Baseball', warp)

    if cv2.waitKey(1) & 0xFF == ord('1'):
        break


# When everything is done, release the capture
feed.release()
cv2.destroyAllWindows()
