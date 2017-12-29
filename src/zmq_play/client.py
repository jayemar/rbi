#!/bin/env python3

import zmq

PORT = 5001

ctx = zmq.sugar.context.Context()

socket = ctx.socket(zmq.REQ)
socket.connect('tcp://127.0.0.1:' + str(PORT))

print("Sending message")
socket.send_pyobj('Test msg')
resp = socket.recv_pyobj()
print("Received message: %s" % str(resp))

socket.close()
