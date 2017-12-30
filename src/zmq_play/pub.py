#!/usr/bin/env python3

import random
import time
import zmq

PORT = 5000

ctx = zmq.Context()

socket = ctx.socket(zmq.PUB)
socket.bind('tcp://*:' + str(PORT))

looping = True
print("Entering loop...")
while looping:
    try:
        lucky_number = random.randint(1, 100)
        msg = "Lucky number: {0}".format(lucky_number)
        print(msg)
        # socket.send_string(msg)
        socket.send_pyobj(['Lucky', msg])
        time.sleep(1.0)
    except KeyboardInterrupt:
        looping = False

socket.close()
ctx.destroy()
