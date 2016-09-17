#!/usr/bin/env python

import cv2
import pdb
import numpy as np


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

