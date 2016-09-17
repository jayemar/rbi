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
FRAME_SIZE = 200
ratio = 1.0
screenCnt = None

while(True):
    step_count += 1

    # Capture frame-by-frame
    ret, frame = feed.read()
    if not ret: continue
    orig = frame.copy()

    P = Perspective.Perspective()
    p = P.get_perspective(frame)

    screenCnt = p['c']
    M = p['M']
    max_width = p['w']
    max_height = p['h']

    # Display the results
    if screenCnt is not None:
        print("Contour area: %s" % str(cv2.contourArea(screenCnt)))
        cv2.drawContours(frame, [screenCnt], -1, (0, 255, 0), 3)
    else:
        print("Good Contour not found")
    cv2.imshow('R.B.I. Baseball - Original', frame)

    # Warp the perspective to grab the screen
    warp = cv2.warpPerspective(orig, M, (max_width, max_height))
    cv2.imshow('R.B.I. Baseball', warp)

    if cv2.waitKey(1) & 0xFF == ord('1'):
        break


# When everything is done, release the capture
feed.release()
cv2.destroyAllWindows()
