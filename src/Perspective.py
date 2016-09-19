#!/usr/bin/env python

import cv2
import pdb
import numpy as np

import imgutils


class Perspective:
    def __init__(self):
        self.color_dict = {'red':   [0, 1],
                           'green': [0, 2],
                           'blue':  [1, 2]}

    def scale_2d(self, matrix, height=None, width=None):
        if len(matrix.shape) != 2:
            raise ValueError("The Matrix must have 2 and only 2 dimensions")

        # These dimensions will be required for scaling
        orig_m = matrix.copy()
        orig_dim = matrix.shape
        orig_h = matrix.shape[0]
        orig_w = matrix.shape[1]
        orig_ratio = float(orig_w) / float(orig_h)

        dim = (0, 0)

        if not height and not width:
            dim = matrix.shape

        elif not height:
            width = width
            new_ratio = float(width) / float(orig_w)
            height = orig_h * new_ratio
            dim = (width, height)

        elif not width:
            height = height
            new_ratio = float(height) / float(orig_h)
            width = orig_w * new_ratio
            dim = (width, height)

        else:
            dim = (height, width)

        dim = tuple(map(lambda x: int(x), dim))
        return cv2.resize(matrix, dim, interpolation=cv2.INTER_AREA)


    def get_perspective(self, frame):
        screenCnt = self.__get_screen_contour(frame)
        if screenCnt is False:
            return False

        # Determine corners of Contour
        #print("DEBUG - Countour shape: %s" % str(screenCnt.shape))
        try:
            pts = screenCnt.reshape(4, 2)
        except ValueError:
            print("ERROR - Countour shape: %s" % str(screenCnt.shape))
            raise 

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

        """
        # Multiply the rectangle by the original ratio
        rect *= ratio
        """

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

        return {'w': maxWidth, 'h': maxHeight, 'M': M, 'c': screenCnt}


    def __get_screen_contour(self, frame):
        #print("DEBUG - Trying to find screen contour")
        blue_frame = imgutils.show_primary(frame.copy(), 'blue', True)
        blue_orig = blue_frame.copy()
        _, thresh_frame = cv2.threshold(blue_frame, 50, 200, cv2.THRESH_BINARY)

        blurred = cv2.bilateralFilter(thresh_frame, 11, 17, 17)
        edged = cv2.Canny(blurred, 30, 200)

        (cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]

        # Assume the largest Contour is the one we want
        screenCnt = None
        for c in cnts:
            # approximate the contour
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)

            # if our approximate contour has 4 points then we can
            # assume that we have the right one
            if (len(approx) == 4)                        and \
               (approx.sum() == np.unique(approx).sum()) and \
               (approx.shape[0] == 4)                    and \
               (cv2.contourArea(approx) > (reduce(lambda x, y: x*y, blue_frame.shape)/4)):
                screenCnt = approx
                print("DEBUG - Found screenCnt")
                break

        #return False if screenCnt is None else screenCnt
        if screenCnt is None:
            return False
        else:
            return screenCnt


    def __get_channels(self, matrix, color):
        if self.__color_check(color):
            return cv2.split(matrix)

    def __color_check(self, color):
        if color not in color_dict.keys():
            raise ValueError("Color must be one of %s" % color_dict.keys())
        else:
            return True

    def __get_color_index(self, color):
        return list(set([0,1,2]) - set(color_dict[color])).pop()

