#!/bin/env python3

import zmq

PORT = 5000

ctx = zmq.sugar.context.Context()

socket = ctx.socket(zmq.SUB)
socket.connect('tcp://localhost:' + str(PORT))
socket.setsockopt(zmq.SUBSCRIBE, b'')

looping = True
while looping:
    try:
        # msg = socket.recv_string()
        topic, msg = socket.recv_pyobj()
        print(topic)
        print(msg)
    except KeyboardInterrupt:
        looping = False

socket.close()
ctx.destroy()
