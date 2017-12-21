#!/usr/bin/env python

'''
Filename:   camutils.py
Date:       02 Oct 2016
Version:    1.0
Author:     jayemar

Library of common camera functions
'''

import cv2
import numpy as np
import logging

from functools import reduce
from lib import imgutils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('camutils')

IMG_MAP = {'original': False, 'mask': False, 'edges': False, 'neural': False}


def scale_2d(orig_matrix, height=None, width=None):
    """
    Do some bad ass scaling

    Parameters
    ----------
    height : integer
        height of output matrix
    width : integer
        width of output matrix

    Returns
    -------
    Scaled matrix

    """
    matrix = orig_matrix.copy()

    if len(matrix.shape) != 2:
        raise ValueError("The Matrix must have 2 and only 2 dimensions")

    orig_h = matrix.shape[0]
    orig_w = matrix.shape[1]

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

    dim = tuple([int(x) for x in dim])
    return cv2.resize(matrix, dim, interpolation=cv2.INTER_AREA)


def get_perspective(feed, hex_color, tolerance=0.10, img_map=False):
    """
    Find a rectangular perspective to represent a head-on view of the image

    Parameters
    ----------
    hex_color : string (represents hex value)
        color value of rectangle representing the perspective in the image
    tolerance : float
        amount of tolerance in the hex color value
    img_map : dictionary
        map of intermediate images to be shown during the perspective-finding
        process

    Returns
    -------
    map including height and width of perspective, the transform_matrix to
    achieve the perspective, and the contour of the selected perspective in
    the original image
    """

    contour = None
    while contour is None:
        read_success, frame = feed.read()
        logger.info("Frame: %s" % str(frame))
        if not read_success:
            logger.info("No frame read; continuing loop...")
            continue
        contour = _get_screen_contour(
            frame, hex_color, tolerance=tolerance, img_map=img_map)

    # Determine corners of Contour
    try:
        pts = contour.reshape(4, 2)
    except ValueError:
        print("ERROR - Countour shape: %s" % str(contour.shape))
        raise

    rect = np.zeros((4, 2), dtype="float32")

    # the top-left point has the smallest sum whereas
    # the bottom-right point has the largest
    points_sum = pts.sum(axis=1)
    rect[0] = pts[np.argmin(points_sum)]
    rect[2] = pts[np.argmax(points_sum)]

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

    max_height, max_width = _get_height_width(rect)

    # Determine destination points
    dst = np.array([
        [0, 0],
        [max_width - 1, 0],
        [max_width - 1, max_height - 1],
        [0, max_height - 1]], dtype="float32")

    # Calculate the perspective transform matrix
    transform_matrix = cv2.getPerspectiveTransform(rect, dst)

    return {'w': max_width,
            'h': max_height,
            'M': transform_matrix,
            'c': contour}


def _get_height_width(rect):
    """
    Get height and width of a rectangle

    Parameters
    ----------
    rect :
        (top_left, top_right, bottom_right, bottom_left)

    Returns
    -------
    (max_height, max_width)
    """
    (top_left, top_right, bottom_right, bottom_left) = rect
    # Compute the Width of the new image
    (top_left, top_right, bottom_right, bottom_left) = rect
    width1 = np.sqrt(((bottom_right[0] - bottom_left[0]) ** 2) +
                     ((bottom_right[1] - bottom_left[1]) ** 2))
    width2 = np.sqrt(((top_right[0] - top_left[0]) ** 2) +
                     ((top_right[1] - top_left[1]) ** 2))

    # Compute the Height of the new image
    height1 = np.sqrt(((top_right[0] - bottom_right[0]) ** 2) +
                      ((top_right[1] - bottom_right[1]) ** 2))
    height2 = np.sqrt(((top_left[0] - bottom_left[0]) ** 2) +
                      ((top_left[1] - bottom_left[1]) ** 2))

    # Determine final dimensions
    max_height = max(int(height1), int(height2))
    max_width = max(int(width1), int(width2))

    return (max_height, max_width)


def calibrate_camera(feed, timeout=9, known_word="TENGEN", img_map=False):
    """
    Tweak various camera parameters (brightness, focus, contrast, etc) in
    order to get a good fix on the desired viewing area and to be able to
    recognize characters for optical character recognition (OCR).

    Parameters
    ----------
    timeout : number
        the maximum number of seconds to spend on the calibration process,
        after which time the camera will be set to the parameters that seemed
        to be the best before the timeout
    known_word : string
        a word that will be known to show up that the camera can look for in
        order to determine OCR performance
    img_map : dictionary
        map of intermediate frames to be shown during the calibration process

    Returns
    -------
    None
    """
    # while True:
    #     _, frame = feed.read()
    #     print "Frame Mean: %f" % np.mean(frame)
    pass


def _get_screen_contour(frame, hex_color, tolerance, img_map=False):
    # blue_frame = imgutils.show_primary(frame.copy(), 'blue', True)
    # blue_orig = blue_frame.copy()
    # _, thresh_frame = cv2.threshold(blue_frame, 50, 200, cv2.THRESH_BINARY)
    # blurred = cv2.bilateralFilter(thresh_frame, 11, 17, 17)

    if img_map and img_map['original']:
        cv2.imshow('Original', frame)

    mask = imgutils.get_color_mask(frame, hex_color, tolerance)
    if img_map and img_map['mask']:
        cv2.imshow('Mask', mask)

    blurred = cv2.bilateralFilter(mask, 11, 17, 17)

    edges = cv2.Canny(blurred, 30, 200)
    if img_map and img_map['edges']:
        cv2.imshow('Edges', edges)

    _image, contours, _hierarchy = cv2.findContours(
        edges.copy(),
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

    # Assume the largest Contour is the one we want
    contour = None
    for cnt in contours:
        # approximate the contour
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

        # if our approximate contour has 4 points then we can
        # assume that we have the right one
        if (len(approx) == 4 and
            approx.sum() == np.unique(approx).sum() and
            approx.shape[0] == 4 and
            cv2.contourArea(approx) >=
                (reduce(lambda x, y: x * y, mask.shape) / 4)):
            contour = approx
            break
        else:
            # print("Contour area: %f" % cv2.contourArea(approx))
            if cv2.waitKey(1) & 0xFF == ord('1'):
                break

    return contour
