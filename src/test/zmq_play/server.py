#!/usr/bin/env python3

import zmq

PORT = 5001

ctx = zmq.Context()

socket = ctx.socket(zmq.REP)
socket.bind('tcp://*:' + str(PORT))

'''
poller = zmq.Poller()
polling = True
print("Entering poll loop...")
while polling:
    try:
        socks = dict(poller.poll(250))
        print("socks: %s" % str(socks))
    except KeyboardInterrupt:
        break
    except zmq.error.ZMQError as zerr:
        print("Exception raised while polling: %s" % zerr)
        raise
    if socks:
        msg = socket.recv_pyobj()
        print(msg)
        socket.send(pickle.dumps('Rgr Roger'))
'''
msg = socket.recv_pyobj()
print(msg)
socket.send_pyobj('Rgr Roger')

socket.close()
