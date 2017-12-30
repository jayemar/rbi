import zmq

ctx = zmq.Context()
req = ctx.socket(zmq.REQ)
req.connect('tcp://localhost:5001')
sock = req
socket = req
