#!/usr/bin/env python

import camutils
import imgutils
import Perspective

import cv2
import numpy as np
import serial
import json

import time
import argparse
import logging
import pdb

from pprint import pprint as pp


BLUE_HEX = "052c72"
MATRIX_HEIGHT = 128
MATRIX_WIDTH = 128
ratio = 1.0
screenCnt = None


""" USAGE INFORMATION """
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--original", required=False,
        help="Show the Original unwarped/unscaled Image", action="store_true")
ap.add_argument("-c", "--contour", required=False,
        help="Show Contour on original image", action="store_true")
ap.add_argument("-n", "--neural", required=False,
        help="Show the Image to be passed to the Neural Network", action="store_true")
ap.add_argument("-l", "--loglevel", required=False,
        help="Log level to be used")
arg_dict = vars(ap.parse_args())


class RBI:
    def __init__(self, log_level=logging.DEBUG):
        self.__configure_logger(log_level)
        self.__configure_camera()
        self.__configure_serial()

        P = Perspective.Perspective()
        self.warp = {'M': None,
                'height': None,
                'width': None}


    def __configure_logger(self, log_level):
        logging.basicConfig(level=log_level)
        self._log = logging.getLogger('RBI_Class')


    def __configure_camera(self):
        self.camera = camutils.Camera()
        self.feed = self.camera.get_feed()
        
        print("Current Brightness: %s" % str(self.camera.get_brightness()))
        print("Current Focus     : %s" % str(self.camera.get_focus()))

        cam_cfg = json.load(open('../camera.cfg'))
        print("Setting Brightness to %s" % str(cam_cfg['Brightness']))
        print("Setting Focus to      %s" % str(cam_cfg['Focus']))
        self.camera.set_brightness(int(cam_cfg['Brightness']))
        self.camera.set_focus(int(cam_cfg['Focus']))

        print("Current Brightness: %s" % str(self.camera.get_brightness()))
        print("Current Focus     : %s" % str(self.camera.get_focus()))


    def __configure_serial(self):
        self.arduino = serial.Serial(port='/dev/ttyACM0',
                baudrate=57600)
        self.arduino.write('0\r\n')


    # TODO: Not sure this will actually ever get called
    def __del__(self):
        try:
            self.feed.release()
            cv2.destroyAllWindows()
        except AttributeError, e:
            #self._log.info("Closing Log")
            #print(e)
            pass


    def calibrate_camera(self):
        start_time = time.time()
        while(True):
            ret, frame = self.feed.read()
            print("Frame Mean: %f" % np.mean(frame))


    def get_perspective(self):
        resp = False
        while resp == False:
            ret, frame = self.feed.read()
            resp = self.P.get_perspective(frame, BLUE_HEX, 0.10)


if __name__ == '__main__':
    rbi = RBI()
    #rbi.calibrate_camera()

