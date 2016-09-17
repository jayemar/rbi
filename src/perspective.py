#!/usr/bin/env python

import camutils
import imgutils

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

    # Convert to gray scale
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    blue_frame = imgutils.show_primary(orig, 'blue', True)
    blue_orig = blue_frame.copy()
    _, blue_frame = cv2.threshold(blue_frame, 50, 200, cv2.THRESH_BINARY)

    gray = blue_frame


    # Resize; starts @ 480 x 640
    #gray = imgutils.scale_2d(gray, height=FRAME_SIZ)

    # TODO: This doesn't need to be done if we've found the TV
    # Filter and Edge detection
    blurred = cv2.bilateralFilter(gray, 11, 17, 17)
    gray = blurred
    edged = cv2.Canny(blue_frame, 30, 200)
    #edged = cv2.Canny(blue_frame, 0, 30, 4)    # Adopted from my C++ stuff

    if good_M is None:
        # Find the 10 largest Contours
        (cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]

        # Assume the largest Contour is the one we want
        for c in cnts:
            # approximate the contour
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)

            screenCnt = approx
            # if our approximate contour has 4 points then we can
            # assume that we have the right one
            if len(approx) == 4 and approx.sum() == np.unique(approx).sum():
                screenCnt = approx
                break

        if screenCnt is None:
            print("screenCnt is None")
            continue
        
        # Determine corners of Contour
        pts = screenCnt.reshape(4, 2)
        rect = np.zeros((4, 2), dtype="float32")

        # the top-left point has the smallest sum whereas
        # the bottom-right point has the largest
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        # compute the difference between the points; the top-right
        # point will have the minimum different and the bottom-left
        # will have the maximum difference
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        # Multiply the rectangle by the original ratio
        rect *= ratio

        # Compute the Width of the new image
        (tl, tr, br, bl) = rect
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))

        # Compute the Height of the new image
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))

        # Determine final dimensions
        maxWidth = max(int(widthA), int(widthB))
        maxHeight = max(int(heightA), int(heightB))

        # Determine destination points
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")

        # Calculate the perspective transform matrix
        M = cv2.getPerspectiveTransform(rect, dst)

        good_M = M
        max_width = maxWidth
        max_height = maxHeight

    # FIXME: This is for debugging only
    """
    if maxWidth < orig.shape[1] * 0.25 or maxHeight < orig.shape[0] * 0.25 \
            or maxWidth < maxHeight:
        good_M = None
        max_width = None
        max_height = None

        print
        print("maxWidth:  %s" % str(maxWidth))
        print("maxHeight: %s" % str(maxHeight))
        #pp(rect)
        continue
    """


    # Display the results
    if screenCnt is not None:
        cv2.drawContours(frame, [screenCnt], -1, (0, 255, 0), 3)
    else:
        print("Good Contour not found")
    cv2.imshow('R.B.I. Baseball - Original', frame)
    #cv2.imshow('R.B.I. Baseball - Blue Threshold', blue_frame)
    #cv2.imshow('R.B.I. Baseball - Blue Original', blue_orig)

    cv2.imshow('R.B.I. Baseball - Blurred', blurred)
    cv2.imshow('R.B.I. Baseball - Contours', edged)

    # Warp the perspective to grab the screen
    warp = cv2.warpPerspective(orig, good_M, (max_width, max_height))
    cv2.imshow('R.B.I. Baseball', warp)

    if cv2.waitKey(1) & 0xFF == ord('1'):
        break


# When everything is done, release the capture
feed.release()
cv2.destroyAllWindows()
