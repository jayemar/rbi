#!/usr/bin/env python

"""
Read characters from screen
"""
from agent import MessagingAgent

import cv2
import threading
import zmq

PUBLISH_PORT = 5004
REPLY_PORT = 5005


class Reader(MessagingAgent):
    def __init__(self):
        super(Reader, self).__init__(publish_port=PUBLISH_PORT,
                                     reply_port=REPLY_PORT)
        self.receiving_frames = True
        self.display_frames = True
        self._create_camera_subscriber_thread()

    def __del__(self):
        self.receiving_frames = False
        self.display_frames = False
        self.camera_subscriber_thread.join(timeout=2.0)
        super(Reader, self).__del__()

    def is_receiving_frames(self):
        return self.receiving_frames

    def _create_camera_subscriber_thread(self):
        self.camera_subscriber_thread = threading.Thread(
            target=self._create_camera_subscriber)
        self.camera_subscriber_thread.start()

    def _create_camera_subscriber(self, port=5000):
        self.camera_subscriber = self.ctx.socket(zmq.SUB)
        self.camera_subscriber.connect('tcp://localhost:%s' % str(port))
        self.camera_subscriber.setsockopt(zmq.SUBSCRIBE, b'')
        while self.is_active and self.receiving_frames:
            msg = self.camera_subscriber.recv_pyobj()
            if self.display_frames and 'warped' in msg:
                cv2.imshow("Reader View", msg.get('warped'))
                cv2.waitKey(1) & 0xFF
                # key = cv2.waitKey(1) & 0xFF
                # if key == ord('1'):
                #     break

    def _handle_request(self, msg):
        """ Handle Reader configuration
        r: toggle active reader
        """
        if msg == 'close':
            self.is_active = False
            self.replier.send_pyobj("Command received to close %s" % self.name)
        elif msg == 'r':
            # XOR with True acts to toggle value
            self.receiving_frames = self.receiving_frames ^ True
            if self.receiving_frames:
                self.replier.send_pyobj("Enabling Camera frame subscriber")
                self._create_camera_subscriber_thread()
            else:
                self.replier.send_pyobj("Disabling Camera frame subscriber")
                self.camera_subscriber_thread.join(timeout=2.0)
        elif msg == 'd':
            self.display_frames = self.display_frames ^ True
            self.replier.send_pyobj("Displaying frames: %s"
                                    % str(self.display_frames))
        else:
            self.replier.send_pyobj("Unknown command: %s" % msg)


if __name__ == '__main__':
    try:
        agent = Reader()
    except KeyboardInterrupt:
        print("Closing %s" % agent.name)
        agent.is_active = False
