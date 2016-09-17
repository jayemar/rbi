#!/usr/bin/env python

import cv2
import pdb

camera = cv2.VideoCapture(0)

step_count = 0

while(True):
    # Capture frame-by-frame
    ret, frame = camera.read()
    step_count += 1

    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)




    # Find corners of TV screen
    #ret, thresh = cv2.threshold(gray, 100, 155, cv2.THRESH_BINARY)

    #contours, hierarchy = cv2.findContours(gray, 1, 2)
    contours = cv2.findContours(gray, 1, 2)



    # Attempt my Affine Transformation
    rows, cols = gray.shape
    M = cv2.getRotationMatrix2D((cols/2, rows/2), -13, 1)

    
    unskewed = cv2.warpAffine(frame, M, (cols, rows))
    # For a 3x3 Perspective Transform
    #cv2.getPerspectiveTransform
    #cv2.warpPerspective


    # Display the resulting frame
    cv2.imshow('R.B.I. Baseball', frame)
    if cv2.waitKey(1) & 0xFF == ord('1'):
        break

# When everything is done, release the capture
camera.release()
cv2.destroyAllWindows()
