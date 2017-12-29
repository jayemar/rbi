#!/usr/bin/env python3

import pickle
import zmq

PORT = 5001

ctx = zmq.sugar.context.Context()

socket = ctx.socket(zmq.REP)
socket.bind('tcp://*:' + str(PORT))

poller = zmq.sugar.poll.Poller()
polling = True
'''
print("Entering poll loop...")
while polling:
    try:
        socks = dict(poller.poll(250))
    except KeyboardInterrupt:
        break
    except zmq.error.ZMQError as zerr:
        print("Exception raised while polling: %s" % zerr)
        raise
    if socks:
        pickled_msg = socket.recv()
        msg = pickle.loads(pickled_msg)
        print(msg)
        socket.send(pickle.dumps('Rgr Roger'))
'''
pickled_msg = socket.recv()
msg = pickle.loads(pickled_msg)
print(msg)
socket.send(pickle.dumps('Rgr Roger'))

socket.close()
