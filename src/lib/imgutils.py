#!/usr/bin/env python

'''
Filename:   imgutils.py
Date:       02 Oct 2016
Version:    1.0
Author:     jayemar

Library of functions for common image manipulation tasks
'''

import cv2
import numpy as np
import pdb

COLOR_DICT = {'red': [0, 1], 'green': [0, 2], 'blue': [1, 2]}

def scale_2d(matrix, height=None, width=None):
    '''
    Scale 2-dimensional matrix to height and/or width, if specified.

    If either height or width is specified, the output matrix will have that
    height or width with the other dimension being scaled so as to keep the
    height/width ratio the same as the input matrix.

    If neither height nor width are specified, the output matrix will have the
    same dimensions as the input matrix.

    Parameters:
        height  - optional; height of output matrix
        width   - optional; width of output matrix
    Return value:
        2-dimensional matrix with specified height and width
    '''
    if len(matrix.shape) != 2:
        raise ValueError("The Matrix must have 2 and only 2 dimensions")

    # These dimensions will be required for scaling
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

def get_color_mask(matrix, color_hex, tolerance=0.10):
    '''
    Get color mask for a specified RGB hex color value

    Parameters:
        color_hex   - hex value in RGB form
        tolerance   - optional; how close searched values will match color_hex
    Return value:
        grayscale mask matrix
    '''
    (min_val, max_val) = __get_color_min_max(color_hex, tolerance)
    mask = cv2.inRange(matrix, min_val, max_val)
    return mask


def match_template(img, tmp, show_match=False,
                   img_xy_start=(0.0, 0.0), img_xy_end=(1.0, 1.0)):
    '''
    *** NOT IMPLEMENTED ***

    Return a location and value for the largest match between an image and a
    template

    Parameters:
        img             - main image as obtained from cv2.imread
        tmp             - template image as obtained from cv2.imread
        show_match      - display box around matched area
        img_xy_start    - tuple of starting (minX, minY) decimal to begin match
        img_xy_end      - tuple of ending (minX, minY) decimal to end match
    Return value:
        tuple of the form (minVal, maxVal, (minLoc), (maxLoc))
    '''
    match = cv2.matchTemplate(img, tmp, cv2.TM_CCORR)
    resp = cv2.minMaxLoc(match)

    if show_match:
        match_img = img.copy()
        p1 = resp[2]
        p2 = resp[3]
        p3 = tuple([p1[0], p2[0]])
        p4 = tuple([p1[1], p2[1]])

        cv2.rectangle(match_img, p2, p1, (0, 0, 255), 3)

        cv2.namedWindow('Template Match', cv2.WINDOW_NORMAL)

        cv2.imshow('Template Match', match_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return resp


def show_primary(matrix, color, single_channel=False):
    '''
    Show only the single layer of the image representing the specified primary
    color

    Parameters:
        color   - one of 'red', 'green', or 'blue'
    Return value:
        1-dimensional matrix
    '''
    if __color_check(color):
        channels = __get_channels(matrix)
        for color in COLOR_DICT[color]:
            channels[color] = np.zeros(channels[color].shape, dtype="uint8")

        resp = np.array([])
        if single_channel:
            resp = channels[__get_color_index(color)]
        else:
            resp = cv2.merge(channels)
        return resp


def remove_primary(matrix, color="blue"):
    '''
    Show the image representing without the layer representing the specified
    primary color

    Parameters:
        color   - one of 'red', 'green', or 'blue'
    Return value:
        3-dimensional matrix
    '''
    if __color_check(color):
        channels = __get_channels(matrix)
        p_index = __get_color_index(color)
        channels[p_index] = np.zeros(channels[p_index].shape, dtype="uint8")
        return cv2.merge(channels)


def __get_color_min_max(color_hex, tolerance=0.10):
    if len(color_hex) != 6:
        raise ValueError("The color must be a 6-digit hex value in RGB form")

    t_diff = int(tolerance * 255)

    min_red = int(color_hex[0:2], 16) - t_diff
    max_red = int(color_hex[0:2], 16) + t_diff
    min_green = int(color_hex[2:4], 16) - t_diff
    max_green = int(color_hex[2:4], 16) + t_diff
    min_blue = int(color_hex[4:6], 16) - t_diff
    max_blue = int(color_hex[4:6], 16) + t_diff

    return ((min_blue, min_green, min_red), (max_blue, max_green, max_red))


def __get_channels(matrix, color=None):
    if color is not None and color not in COLOR_DICT.keys():
        raise ValueError("Color must be one of %s" % COLOR_DICT.keys())
    return cv2.split(matrix)

def __color_check(color=None):
    if color is not None and color not in COLOR_DICT.keys():
        raise ValueError("Color must be one of %s" % COLOR_DICT.keys())
    else:
        return True

def __get_color_index(color):
    return list(set([0, 1, 2]) - set(COLOR_DICT[color])).pop()

