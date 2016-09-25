#!/usr/bin/env python

import tensorflow as tf
import tensorlib as tflib

import pdb


layer_map = {
    1: ( 1, 100, 'layer1', tf.nn.relu ),
    2: ( 100, 84, 'layer2', tf.nn.relu ),
    3: ( 84, 36, 'output', tf.nn.softmax )
}


if __name__ == '__main__':
    l_map = layer_map
    pdb.set_trace()
    
