import cv2
import zmq

ctx = zmq.Context()

req = ctx.socket(zmq.REQ)
req.connect('tcp://localhost:5001')

sub = ctx.socket(zmq.SUB)
sub.connect('tcp://localhost:5000')
# sub.setsockopt_string(zmq.SUBSCRIBE, 'Camera')
# sub.setsockopt(zmq.SUBSCRIBE, b'Camera')
sub.setsockopt(zmq.SUBSCRIBE, b'')
