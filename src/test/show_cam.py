#!/usr/bin/env python

import cv2
import zmq

ctx = zmq.Context()
pub = ctx.socket(zmq.SUB)
pub.connect('tcp://localhost:5000')
pub.setsockopt(zmq.SUBSCRIBE, b'')

'''
mask = imgutils.get_color_mask(frame, "052C72", 0.25)
cv2.imshow('Blue Mask', mask)

blurred = cv2.bilateralFilter(mask, 11, 17, 17)
# cv2.imshow('Blurred', blurred)

edged = cv2.Canny(blurred, 30, 200)
# cv2.imshow('Edged', edged)
'''

looping = True
print("Press '1' on the image to close")
while looping:
    try:
        frame_dict = pub.recv_pyobj()
        # cv2.imshow('Raw Frame', frame_dict.get('raw', []))
        for label, frame in frame_dict.items():
            cv2.imshow(label, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('1'):
            break
    except KeyboardInterrupt:
        looping = False
    except Exception as err:
        print("Exception receiving frames: %s" % err)


pub.close()
ctx.destroy()
cv2.destroyAllWindows()
