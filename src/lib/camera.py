#!/usr/bin/env python

"""
Control an attached USB webcam using the 'uvcdynctrl' utility
"""

import cv2
import logging
import subprocess
import threading
import time
import zmq

PUBLISH_PORT = 5000
REPLY_PORT = 5001
LOG_FILENAME = '/var/log/rbi/camera.log'


class Camera(object):
    """
    Object representing an attached USB webcam
    """
    def __init__(self, device_num=0):
        """
        Connect to camera at device_num

        Optional Args:
            device_num: id number of device to use
        Returns:
            None
        Raises:
            None
        """
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            filename=LOG_FILENAME,
            filemode='a')
        logging.Formatter.converter = time.gmtime
        self._log = logging.getLogger('Camera')

        self.is_active = True
        self.feed = cv2.VideoCapture(device_num)

        self.ctx = zmq.Context()
        self._log.info("ZMQ context created")
        self._configure_messaging()

    def __del__(self):
        """
        Release camera feed and close all OpenCV windows
        """
        self.publisher.close()
        # self.replier_thread.join(timeout=0)
        self.ctx.destroy()
        self.feed.release()
        cv2.destroyAllWindows()
        print("Camera shutdown")

    def _configure_messaging(self):
        self._create_publisher()
        self.replier_thread = threading.Thread(target=self._create_replier)
        self.replier_thread.start()

    def _create_publisher(self):
        self.publisher = self.ctx.socket(zmq.PUB)
        self.publisher.bind('tcp://*:%s' % PUBLISH_PORT)
        self._log.debug("Listening on publisher socket")

    def _create_replier(self):
        self.replier = self.ctx.socket(zmq.REP)
        self.replier.bind('tcp://*:%s' % REPLY_PORT)
        self._log.debug("Listening on replier socket")
        poller = zmq.Poller()
        poller.register(self.replier, zmq.POLLIN)
        while self.is_active:
            socks = dict(poller.poll())
            if self.replier in socks and socks[self.replier] == zmq.POLLIN:
                msg = self.replier.recv_pyobj()
                self._log.debug("Received message: %s" % str(msg))
                if msg.lower() == 'close':
                    self._log.info("Closing Camera")
                    self.is_active = False
                    break
                else:
                    self.replier.send_pyobj("Rgr, Roger")
        self.replier.close()
        # self.__del__()

    def publish_frames(self):
        if not self.feed.isOpened():
            self._log.error("Feed is not open")
        else:
            self._log.info("Publishing camera frames")
            while self.is_active:
                success, frame = self.feed.read()
                if success:
                    self.publisher.send_pyobj(['Camera', frame])
                    # self.publisher.send_pyobj(frame)
                else:
                    self._log.error("Unable to read frame from camera")
                    break

    def get_live_stream(self):
        while True:
            _, frame = self.feed.read()
            return frame

    def get_brightness(self):
        return self.__uvc("Brightness").strip()

    def set_brightness(self, b):
        self.__uvc("Brightness", b)

    def get_contrast(self):
        return self.__uvc("Contrast").strip()

    def set_contrast(self, b):
        self.__uvc("Contrast", b)

    def get_saturation(self):
        return self.__uvc("Saturation").strip()

    def set_saturation(self, b):
        self.__uvc("Saturation", b)

    def get_focus(self):
        return self.__uvc("Focus (absolute)").strip()

    def set_focus(self, b):
        self.__uvc("Focus, Auto", 0)
        self.__uvc("Focus (absolute)", b)

    def auto_focus(self):
        self.__uvc("Focus, Auto", 1)

    def get_sharpness(self):
        return self.__uvc("Sharpness").strip()

    def set_sharpness(self, b):
        self.__uvc("Sharpness", b)

    def __uvc(self, cmd, val=None):
        if val:
            resp = subprocess.check_output(["uvcdynctrl", "-s", cmd, str(val)])
        else:
            resp = subprocess.check_output(["uvcdynctrl", "-g", cmd])
        return resp

    def calibrate_camera(self, timeout=9, known_word="TENGEN", img_map=False):
        """
        Tweak various camera parameters (brightness, focus, contrast, etc) in
        order to get a good fix on the desired viewing area and to be able to
        recognize characters for optical character recognition (OCR).

        Parameters
        ----------
        timeout : number
            the maximum number of seconds to spend on the calibration process,
            after which time the camera will be set to the parameters that
            seemed to be the best before the timeout
            The Blue Screen stays up for roughly 10 seconds
        known_word : string
            a word that will be known to show up that the camera can look for
            in order to determine OCR performance
        img_map : dictionary
            map of intermediate frames to be shown during the calibration
            process

        Returns
        -------
        None
        """
        # while True:
        #     _, frame = feed.read()
        #     print "Frame Mean: %f" % np.mean(frame)
        pass


if __name__ == '__main__':
    camera = Camera()
    camera.publish_frames()
