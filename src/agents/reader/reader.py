#!/usr/bin/env python

"""
Read characters from screen
"""
from agent import MessagingAgent

import arrow
import cv2
import numpy as np
import threading
import zmq

import pdb

from PIL import ImageOps

PUBLISH_PORT = 5004
REPLY_PORT = 5005
CAMERA_SUBSCRIBER_PORT = 5000
BW_THRESHOLD = 0.5


class Reader(MessagingAgent):
    def __init__(self):
        super(Reader, self).__init__(publish_port=PUBLISH_PORT,
                                     reply_port=REPLY_PORT)
        self.receiving_frames = True
        self.display_frames = False
        self.threshold = BW_THRESHOLD
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

    def _create_camera_subscriber(self, port=CAMERA_SUBSCRIBER_PORT):
        self.camera_subscriber = self.ctx.socket(zmq.SUB)
        self.camera_subscriber.connect('tcp://localhost:%s' % str(port))
        self.camera_subscriber.setsockopt(zmq.SUBSCRIBE, b'')
        while self.is_active and self.receiving_frames:
            msg = self.camera_subscriber.recv_pyobj()
            if self.display_frames and 'warped' in msg:
                frame = self._preprocess_frame(msg.get('warped'),
                                               threshold=self.threshold)
                cv2.imshow("Reader View", frame)
                cv2.waitKey(1) & 0xFF
            else:
                cv2.destroyAllWindows()

    def _preprocess_frame(self, frame, threshold=0.5):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame[frame > (255.0 * threshold)] = 255
        frame[frame < 255.0] = 0
        frame = frame ^ 255
        # return ImageOps.invert(frame)
        return frame

    def _take_screenshot(self):
        AVG_FRAMES = 5
        success = False
        tmp_subscriber = self.ctx.socket(zmq.SUB)
        tmp_subscriber.connect('tcp://localhost:%s'
                               % str(CAMERA_SUBSCRIBER_PORT))
        tmp_subscriber.setsockopt(zmq.SUBSCRIBE, b'')
        try:
            msg = tmp_subscriber.recv_pyobj()
            if 'warped' not in msg:
                raise Exception("Unable to find warped frame")

            frames = list()
            for i in range(AVG_FRAMES):
                msg = tmp_subscriber.recv_pyobj()
                frames.append(msg.get('warped'))
            pdb.set_trace()
            frame = np.mean(frames, axis=0).astype('uint8')

            img_time = str(arrow.utcnow().timestamp)
            img_name = 'reader_screenshot_{0}.png'.format(img_time)
            # img_path = '../images/screenshots/' + img_name
            img_path = img_name
            frame = self._preprocess_frame(frame)
            cv2.imwrite(img_path, frame, (cv2.IMWRITE_PNG_COMPRESSION, 0))
            success = True
            self._log.info("Image saved to %s" % img_path)
            print("Image saved to %s" % img_path)
        finally:
            tmp_subscriber.close()
        return success

    def _handle_request(self, msg):
        """ Handle Reader configuration """
        options = {'h or ?': "help; show these options",
                   'q': "quit/close agent",
                   'r': "toggle active reader",
                   'd': "toggle debug mode to display frame in new window",
                   'b': "threshold for black/white conversion",
                   't': "save screenshot to disk"}
        if msg in ['h', '?']:
            self.replier.send_pyobj(options)
        elif msg == 'q':
            self.is_active = False
            self.replier.send_pyobj("Command received to close %s" % self.name)
        elif msg == 'r':
            self.replier.send_pyobj("Option 'r' not currently available for Reader agent")
            '''
            # XOR with True acts to toggle value
            self.receiving_frames = self.receiving_frames ^ True
            if self.receiving_frames:
                self.replier.send_pyobj("Enabling Camera frame subscriber")
                self._create_camera_subscriber_thread()
            else:
                self.replier.send_pyobj("Disabling Camera frame subscriber")
                self.camera_subscriber_thread.join(timeout=2.0)
                cv2.destroyAllWindows()
            '''
        elif msg == 'd':
            self.display_frames = self.display_frames ^ True
            self.replier.send_pyobj("Displaying frames: %s"
                                    % str(self.display_frames))
        elif msg.startswith('b'):
            try:
                thresh = float(msg[1:])
                self.threshold = thresh
            except Exception:
                pass
            finally:
                self.replier.send_pyobj("Threshold: %f" % self.threshold)
        elif msg == 't':
            if self.receiving_frames:
                if self._take_screenshot():
                    self.replier.send_pyobj("Screenshot saved")
                else:
                    self.replier.send_pyobj("Unable to save screenshot")
            else:
                self._log.warn("Not currently receiving frames")
                self.replier.send_pyobj("Not currently receiving frames")
        else:
            self.replier.send_pyobj("Unknown command: %s" % msg)


if __name__ == '__main__':
    try:
        agent = Reader()
    except KeyboardInterrupt:
        print("Closing %s" % agent.name)
        agent.is_active = False
