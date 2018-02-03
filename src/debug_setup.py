import sys
import zmq

try:
    PORT = sys.argv[1]
except Exception:
    PORT = 5001

ctx = zmq.Context()
req = ctx.socket(zmq.REQ)
req.connect('tcp://localhost:%s' % str(PORT))
sock = req
socket = req
print("\nReady to send send_pyobj requests on port: %s" % str(PORT))


def send(msg):
    socket.send_pyobj(msg)
    return socket.recv_pyobj()
