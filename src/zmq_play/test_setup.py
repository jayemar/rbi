import zmq

ctx = zmq.Context()
socket = ctx.socket(zmq.REQ)
socket.connect('tcp://localhost:5001')
