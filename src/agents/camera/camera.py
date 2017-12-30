#!/usr/bin/env python

"""
Control an attached USB webcam using the 'uvcdynctrl' utility
"""
import imgutils

import cv2
import logging
import numpy as np
import subprocess
import threading
import time
import zmq

from functools import reduce

PUBLISH_PORT = 5000
REPLY_PORT = 5001
LOG_FILENAME = '/var/log/rbi/camera.log'
# HEX_BLUE = "052C72"
HEX_BLUE = "153C82"

""" Frame Masks """
raw_mask = 0x01
contour_mask = 0x02
warp_mask = 0x04
DEFAULT_MASK = 7


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

        self.perspective = None
        self.frame_mask = DEFAULT_MASK

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
        self.ctx.destroy()
        self.feed.release()
        cv2.destroyAllWindows()
        print("Camera shutdown")

    def _configure_messaging(self):
        self._create_publisher()
        self.replier_thread = threading.Thread(
            target=self._create_replier)
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
            try:
                socks = dict(poller.poll())
                if self.replier in socks and socks[self.replier] == zmq.POLLIN:
                    msg = self.replier.recv_pyobj()
                    self._log.debug("Received message: %s" % str(msg))
                    if msg.lower() == 'close':
                        self.is_active = False
                    else:
                        self._handle_request(msg)
            except KeyboardInterrupt:
                self.is_active = False
        self._log.info("Closing Reply socket")
        self.replier.close()

    def _handle_request(self, msg):
        """Handle Camera Settings:
        b: brightness
        c: contract
        s: saturation
        f: focus
        h: sharpness
        m: frame mask
        """
        if msg.lower() == 'b':
            self.replier.send_pyobj(self.get_brightness())
        elif msg.lower() == 'c':
            self.replier.send_pyobj(self.get_contrast())
        elif msg.lower() == 's':
            self.replier.send_pyobj(self.get_saturation())
        elif msg.lower() == 'f':
            self.replier.send_pyobj(self.get_focus())
        elif msg.lower() == 'h':
            self.replier.send_pyobj(self.get_sharpness())
        elif msg.lower() == 'm':
            self.replier.send_pyobj(self.get_frame_mask())
        else:
            if msg.lower().startswith('b'):
                cmd = self.set_brightness
            elif msg.lower().startswith('c'):
                cmd = self.set_contrast
            elif msg.lower().startswith('s'):
                cmd = self.set_saturation
            elif msg.lower().startswith('f'):
                cmd = self.set_focus
            elif msg.lower().startswith('h'):
                cmd = self.set_sharpness
            elif msg.lower().startswith('m'):
                cmd = self.set_frame_mask
            try:
                level = int(msg[1:])
                cmd(level)
                self.replier.send_pyobj("%s: %d" % (str(cmd), level))
            except Exception:
                self.replier.send_pyobj("Unknown command: %s" % msg)

    def publish_frames(self):
        if not self.feed.isOpened():
            self._log.error("Feed is not open")
            return

        self._log.debug("Publishing camera frames")
        while self.is_active and self.frame_mask:
            try:
                success, frame = self.feed.read()
                if not success:
                    self._log.error("Unable to read frame from camera")
                    break

                frame_dict = dict()
                if self.frame_mask & raw_mask:
                    frame_dict.update({'raw': frame})
                if not self.perspective:
                    if self.frame_mask > 1:
                        contours = self._get_perspective(frame)
                    if self.frame_mask & contour_mask:
                        frame_dict.update(contours)
                if self.perspective and self.frame_mask & warp_mask:
                    warped = self._warp_frame(frame, self.perspective)
                    frame_dict.update({'warped': warped})
                self.publisher.send_pyobj(frame_dict)
            except KeyboardInterrupt:
                self.is_active = False

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

    def get_frame_mask(self):
        return self.frame_mask

    def set_frame_mask(self, mask):
        try:
            self.frame_mask = int(mask)
        except Exception:
            pass
        return self.frame_mask

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

    def _warp_frame(self, frame, perspective):
        '''
        Warp input view frame to show head-on perspective

        Parameters
        ----------
        frame : numpy array
        perspective : dict
            dict with warp matrix, height, width, and 'c'

        Returns
        -------
        warped : numpy array
            warped matrix
        '''
        translation_matrix = perspective['M']
        height = perspective['h']
        width = perspective['w']
        # c = perspective['c']
        warped = cv2.warpPerspective(frame,
                                     translation_matrix,
                                     (width, height))
        return warped

    def _get_perspective(self, frame, tolerance=0.35, img_map=None):
        """
        Find a rectangular perspective to represent a head-on view of the image

        Parameters
        ----------
        tolerance : float
            amount of tolerance in the hex color value
        img_map : dictionary
            map of intermediate images to be shown during the
            perspective-finding process

        Returns
        -------
        map including height and width of perspective, the transform_matrix to
        achieve the perspective, and the contour of the selected perspective in
        the original image
        """
        '''
        contour = None
        while contour is None:
            read_success, frame = self.feed.read()
            # self._log.debug("Frame: %s" % str(frame))
            if not read_success:
                self._log.debug("No frame read; continuing loop...")
                continue
            contour = self._get_screen_contour(
                frame, HEX_BLUE, tolerance=tolerance, img_map=img_map)
        '''
        contour, contour_dict = self._get_screen_contour(
            frame, HEX_BLUE, tolerance=tolerance, img_map=img_map)

        # Try to determine corners of Contour
        try:
            pts = contour.reshape(4, 2)
        except Exception:
            return contour_dict

        rect = np.zeros((4, 2), dtype="float32")

        # the top-left point has the smallest sum whereas
        # the bottom-right point has the largest
        points_sum = pts.sum(axis=1)
        rect[0] = pts[np.argmin(points_sum)]
        rect[2] = pts[np.argmax(points_sum)]

        # compute the difference between the points; the top-right
        # point will have the minimum different and the bottom-left
        # will have the maximum difference
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        """
        # Multiply the rectangle by the original ratio
        rect *= ratio
        """

        max_height, max_width = imgutils.get_height_width(rect)

        # Determine destination points
        dst = np.array([
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1]], dtype="float32")

        # Calculate the perspective transform matrix
        transform_matrix = cv2.getPerspectiveTransform(rect, dst)
        self._log.info("Found Perspective!")
        self.found_perspective = True
        # return {'w': max_width,
        #         'h': max_height,
        #         'M': transform_matrix,
        #         'c': contour}
        transformation_dict = {'w': max_width,
                               'h': max_height,
                               'M': transform_matrix,
                               'c': contour}
        self.perspective = transformation_dict
        return contour_dict

    def _get_color_mask(self, frame, hex_color, tolerance):
        return imgutils.get_color_mask(frame, hex_color, tolerance)

    def _get_blur(self, mask):
        return cv2.bilateralFilter(mask, 11, 17, 17)

    def _get_edges(self, blurred):
        return cv2.Canny(blurred, 30, 200)

    def _get_screen_contour(self, frame, hex_color, tolerance, img_map=False):
        # blue_frame = imgutils.show_primary(frame.copy(), 'blue', True)
        # blue_orig = blue_frame.copy()
        # _, t_frame = cv2.threshold(blue_frame, 50, 200, cv2.THRESH_BINARY)
        # blurred = cv2.bilateralFilter(t_frame, 11, 17, 17)

        mask = self._get_color_mask(frame, hex_color, tolerance)
        blurred = self._get_blur(mask)
        edges = self._get_edges(blurred)

        _image, contours, _hierarchy = cv2.findContours(
            edges.copy(),
            cv2.RETR_TREE,
            cv2.CHAIN_APPROX_SIMPLE
        )
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

        # Assume the largest Contour is the one we want
        contour = None
        for cnt in contours:
            # approximate the contour
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

            # if our approximate contour has 4 points then we can
            # assume that we have the right one
            if (len(approx) == 4 and
                approx.sum() == np.unique(approx).sum() and
                approx.shape[0] == 4 and
                cv2.contourArea(approx) >=
                    (reduce(lambda x, y: x * y, mask.shape) / 4)):
                contour = approx
                break
            '''
            else:
                # print("Contour area: %f" % cv2.contourArea(approx))
                if cv2.waitKey(1) & 0xFF == ord('1'):
                    break
            '''
        return contour, {'blue': mask, 'blur': blurred, 'edge': edges}


if __name__ == '__main__':
    camera = Camera()
    print("Publishing on port %d" % PUBLISH_PORT)
    print("Messaging on port %d" % REPLY_PORT)
    camera.publish_frames()
