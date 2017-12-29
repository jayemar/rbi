#!/bin/env python3

import pdb
import pickle
import zmq

PORT = 5001

ctx = zmq.sugar.context.Context()

socket = ctx.socket(zmq.REQ)
socket.connect('tcp://127.0.0.1:' + str(PORT))

print("Sending message")
resp = socket.send(pickle.dumps('Test msg'))
print("Received message: %s" % str(resp))

socket.close()
