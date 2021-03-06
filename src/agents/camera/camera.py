#!/usr/bin/env python

"""
Control an attached USB webcam using the 'uvcdynctrl' utility
"""
import imgutils
from agent import MessagingAgent

import arrow
import cv2
import json
import numpy as np
import subprocess
import threading
import time
import zmq

from functools import reduce
from os import path
from pprint import pformat

import pdb

LOG_FILENAME = '/var/log/rbi/camera.log'
PUBLISH_PORT = 5000
REPLY_PORT = 5001
# HEX_BLUE = "052C72"
HEX_BLUE = "153C82"

""" Frame Masks """
raw_mask = 0x01
contour_mask = 0x02
warp_mask = 0x04
DEFAULT_MASK = 5


class Camera(MessagingAgent):
    """
    Object representing an attached USB webcam
    """
    def __init__(self, device_num=0):
        """
        Connect to camera at device_num

        Parameters
        ----------
        device_num : int
            id number of device to use
        Returns
        -------
        None
        """
        super(Camera, self).__init__(publish_port=PUBLISH_PORT,
                                     reply_port=REPLY_PORT)
        self.perspective = None
        self.feed = cv2.VideoCapture(device_num)
        self.is_debug = True
        self.frame_mask = DEFAULT_MASK
        self.debug_reader = FrameReader(enabled=self.is_debug)
        # self.debug_thread = threading.Thread(
        #     target=self.debug_reader.show_frames, args=[self.is_debug])
        # self.debug_reader.show_frames(enabled=self.is_debug)
        self.__initialize_camera()

    def __initialize_camera(self):
        with open(path.relpath('./camera.cfg'), 'r') as phil:
            initial_config = json.load(phil)

        self._log.debug(pformat(initial_config))
        for k, v in initial_config.items():
            time.sleep(0.250)
            print("Setting %s to %d" % (k, v))
            new_val = self.__uvc(k, v)
            print("%s set to %s" % (k, str(new_val)))

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

    def _handle_request(self, msg):
        """ Handle Camera Settings """
        options = {'h or ?': "help; show these options",
                   'q': "quit/close agent",
                   'd': "toggle debug mode; display frames",
                   'm': "frame mask",
                   't': "take screenshot of perspective view",
                   'r': "reset/recapture perspective",
                   'l': "calibrate camera (Not Implemented)",
                   'z': "zoom",
                   'b': "brightness",
                   'c': "contrast",
                   'e': "exposure",
                   's': "saturation",
                   'f': "focus",
                   'p': "sharpness"}
        if msg in ['h', '?']:
            self.replier.send_pyobj(options)
        elif msg == 'q':
            self.is_active = False
            self.replier.send_pyobj("Command received to close %s" % self.name)
        elif msg == 'd':
            self.is_debug = self.is_debug ^ True
            self.debug_reader.set_enabled(self.is_debug)
            self.replier.send_pyobj("Viewing frames: %s"
                                    % str(self.debug_reader.is_enabled()))
        elif msg == 't':
            if self.perspective:
                img_name = self._take_screenshot()
                if img_name:
                    self.replier.send_pyobj("Screenshot saved: %s" % img_name)
                else:
                    self.replier.send_pyobj("Unable to save screenshot")
            else:
                self.replier.send_pyobj("Perspective view not yet availble")
        elif msg == 'r':
            self.perspective = []
            self.replier.send_pyobj("Perspective reset")
        elif msg == 'l':
            self.calibrate_camera()
        elif msg == 'z':
            self.replier.send_pyobj(self.get_zoom())
        elif msg == 'b':
            self.replier.send_pyobj(self.get_brightness())
        elif msg == 'c':
            self.replier.send_pyobj(self.get_contrast())
        elif msg == 'e':
            self.replier.send_pyobj(self.get_exposure())
        elif msg == 's':
            self.replier.send_pyobj(self.get_saturation())
        elif msg == 'f':
            self.replier.send_pyobj(self.get_focus())
        elif msg == 'p':
            self.replier.send_pyobj(self.get_sharpness())
        elif msg == 'm':
            self.replier.send_pyobj(self.get_frame_mask())
        else:
            if msg.startswith('z'):
                cmd = self.set_zoom
            elif msg.startswith('b'):
                cmd = self.set_brightness
            elif msg.startswith('c'):
                cmd = self.set_contrast
            elif msg.startswith('e'):
                cmd = self.set_exposure
            elif msg.startswith('s'):
                cmd = self.set_saturation
            elif msg.startswith('f'):
                cmd = self.set_focus
            elif msg.startswith('p'):
                cmd = self.set_sharpness
            elif msg.startswith('m'):
                cmd = self.set_frame_mask
            try:
                level = int(msg[1:])
                cmd(level)
                self.replier.send_pyobj(level)
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
        return self.__uvc("Brightness", b)

    def get_contrast(self):
        return self.__uvc("Contrast").strip()

    def set_contrast(self, b):
        return self.__uvc("Contrast", b)

    def get_exposure(self):
        return self.__uvc("Exposure (Absolute)").strip()

    def set_exposure(self, b):
        return self.__uvc("Exposure (Absolute)", b)

    def get_focus(self):
        return self.__uvc("Focus (absolute)").strip()

    def set_focus(self, b):
        return self.__uvc("Focus (absolute)", b)

    def auto_focus(self):
        return self.__uvc("Focus, Auto", 1)

    def get_saturation(self):
        return self.__uvc("Saturation").strip()

    def set_saturation(self, b):
        return self.__uvc("Saturation", b)

    def get_sharpness(self):
        return self.__uvc("Sharpness").strip()

    def set_sharpness(self, b):
        return self.__uvc("Sharpness", b)

    def get_zoom(self):
        return self.__uvc("Zoom, Absolute").strip()

    def set_zoom(self, b):
        return self.__uvc("Zoom, Absolute", b)

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
        self._log.info("Inside calibrate_camera")

        # 1. Change Exposure settings until we have a perspective lock
        # 2. Change zoom level until the edges of the perspective
        #    are near the edge of the frame
        self.calibration_thread = threading.Thread(
            target=self._calibrate_camera)

    def _calibrate_camera(self):
        # self._log.info("Inside _calibrate_camera")
        # while not self.perspective:
            # new_exposure = self.get_exposure() - 25
            # self._log.info("Setting exposure to %d" % new_exposure)
            # self.set_exposure(new_exposure)
            # time.sleep(3.0)
        # self._log.info("Perspective found; leaving _calibrate_camera")
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

    def _take_screenshot(self):
        resp = None
        tmp_subscriber = self.ctx.socket(zmq.SUB)
        tmp_subscriber.connect('tcp://localhost:%s' % str(self.publish_port))
        tmp_subscriber.setsockopt(zmq.SUBSCRIBE, b'')
        try:
            msg = tmp_subscriber.recv_pyobj()
            img_time = str(arrow.utcnow().timestamp)
            img_name = 'reader_screenshot_{0}.png'.format(img_time)
            # img_path = '../images/screenshots/' + img_name
            img_path = img_name
            if 'warped' in msg:
                cv2.imwrite(img_path, msg.get('warped'),
                            (cv2.IMWRITE_PNG_COMPRESSION, 0))
                resp = img_path
                self._log.info("Image saved to %s" % img_path)
                print("Image saved to %s" % img_path)
        finally:
            tmp_subscriber.close()
        return resp


class FrameReader(object):
    def __init__(self, enabled=False):
        self.ctx = zmq.Context()
        self.sub = self.ctx.socket(zmq.SUB)
        self.sub.connect('tcp://localhost:%s' % str(PUBLISH_PORT))
        self.sub.setsockopt(zmq.SUBSCRIBE, b'')
        self.enabled = enabled
        self.looper = threading.Thread(
            target=self.show_frames, args=[self.enabled])
        self.looper.start()

    def __del__(self):
        self.enabled = False
        self.looper.join(timeout=0.5)
        self.sub.close()
        self.ctx.destroy()

    def is_enabled(self):
        return self.enabled

    def set_enabled(self, enabled):
        self.enabled = enabled
        return self.enabled

    def show_frames(self, enabled=True):
        self.enabled = enabled
        while True:
            if self.enabled:
                try:
                    frame_dict = self.sub.recv_pyobj()
                    for label, frame in frame_dict.items():
                        cv2.imshow(label, frame)
                    cv2.waitKey(1) & 0xFF
                except KeyboardInterrupt:
                    self.enabled = False
                except Exception as err:
                    print("Exception receiving frames: %s" % err)
            else:
                cv2.destroyAllWindows()


if __name__ == '__main__':
    camera = Camera()
    camera.publish_frames()
