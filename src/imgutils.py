#!/usr/bin/env python

import cv2
import pdb
import numpy as np

color_dict = {'red': [0, 1], 'green': [0, 2], 'blue': [1, 2]}

def scale_2d(matrix, height=None, width=None):
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


def show_primary(matrix, color, single_channel=False):
    if __color_check(color):
        channels = __get_channels(matrix)
        for c in color_dict[color]:
            channels[c] = np.zeros(channels[c].shape, dtype="uint8")

        resp = np.array([])
        if (single_channel):
            resp = channels[__get_color_index(color)]
        else:
            resp = cv2.merge(channels)
        return resp


def remove_primary(matrix, color="blue"):
    if __color_check(color):
        channels = __get_channels(matrix)
        p_index = __get_color_index(color)
        channels[p_index] = np.zeros(channels[p_index].shape, dtype="uint8")
        return cv2.merge(channels)


def get_perspective(frame):
    frame = show_primary(frame, 'blue')

def __get_channels(matrix, color=None):
    if color is not None and color not in color_dict.keys():
        raise ValueError("Color must be one of %s" % color_dict.keys())
    return cv2.split(matrix)

def __color_check(color=None):
    if color is not None and color not in color_dict.keys():
        raise ValueError("Color must be one of %s" % color_dict.keys())
    else:
        return True

def __get_color_index(color):
    return list(set([0,1,2]) - set(color_dict[color])).pop()
