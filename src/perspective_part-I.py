#!/usr/bin/env python

import camutils
import imgutils

import cv2
import numpy as np
import pdb

camera = camutils.Camera()
feed = camera.get_feed()

step_count = 0
FRAME_SIZE = 200

while(True):
    step_count += 1

    # Capture frame-by-frame
    ret, frame = feed.read()
    orig = frame.copy()

    # Convert to gray scale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Resize; starts @ 480 x 640
    #gray = imgutils.scale_2d(gray, height=FRAME_SIZE)

    # Filter and Edge detection
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(gray, 30, 200)

    # Find the 10 largest Contours
    (cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]
    screenCnt = None

    # Assume the largest Contour is the one we want
    for c in cnts:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        # if our approximate contour has 4 points then we can
        # assume that we have the right one
        if len(approx) == 4:
            screenCnt = approx
            break
    
    # Display the resulting frame with Contour
    cv2.drawContours(frame, [screenCnt], -1, (0, 255, 0), 3)
    cv2.imshow('R.B.I. Baseball', frame)
    if cv2.waitKey(1) & 0xFF == ord('1'):
        break

# When everything is done, release the capture
feed.release()
cv2.destroyAllWindows()
