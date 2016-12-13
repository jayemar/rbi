#!/usr/bin/env python
'''
Computer AI plays RBI Baseball on FCEUX Emulator

Optional Args:
    log_level: level of logging to use for execution
Returns:
    None
Raises:
    None
'''

import argparse
import logging
import cv2
import time
import json
import os
import inspect
import subprocess

from pprint import pprint as pp

from lib import camera
from lib import arduino
from lib import camutils
from lib import imgutils

import NES_keyboard as kbrd

BLUE = 9
GREEN = 11
RED = 12

OFF = 0
ON = 1
FAST_BLINK = 2
SLOW_BLINK = 3


class RBI(object):
    '''
    Computer AI plays RBI Baseball on FCEUX Emulator

    Args:
        height: height of matrix to feed in to neural network
        width: width of matrix to feed in to neural network
    Optional Args:
        log_level: level of logging to use for execution
    Returns:
        None
    Raises:
        None
    '''
    def __init__(self, height, width, log_level="info"):
        log_map = {'info': logging.INFO,
                   'debug': logging.DEBUG,
                   'warn': logging.WARN}

        try:
            self.__configure_logger(log_map[log_level])
        except AttributeError:
            if log_level is None:
                self.__configure_logger(logging.INFO)
            else:
                self.__configure_logger(logging.DEBUG)
                self._log.warn("Unable to configure logger with value '" +
                               str(log_level) + "'\n")

        self.nn_matrix_info = {'height': height, 'width': width}
        self.__configure_camera()
        self.__configure_arduino()
        self.kbrd = kbrd.Keyboard()

        self.templates = {}
        self.templates['BALL']   = cv2.imread('../images/templates/warped/ball_small_warped.png')
        self.templates['FOUL']   = cv2.imread('../images/templates/warped/foul_small_warped.png')
        self.templates['OUT']    = cv2.imread('../images/templates/warped/out_small_warped.png')
        self.templates['STRIKE'] = cv2.imread('../images/templates/warped/strike_small_warped.png')


    @staticmethod
    def parse_args():
        '''
        Parse command line arguments

        Called when this file is run from the command line.
        '''
        arg_map = argparse.ArgumentParser()
        arg_map.add_argument("-t", "--train", required=False, action="store_true",
                             help="Operate in training mode")
        arg_map.add_argument("-c", "--calibrate", required=False, action="store_true",
                             help="Calibrate camera prior to running program")
        arg_map.add_argument("-o", "--original", required=False, action="store_true",
                             help="Show the Original unwarped/unscaled image")
        arg_map.add_argument("-m", "--mask", required=False, action="store_true",
                             help="Show the color Masked Image")
        arg_map.add_argument("-e", "--edges", required=False, action="store_true",
                             help="Show Edges/Contours on original image")
        arg_map.add_argument("-w", "--warped", required=False, action="store_true",
                             help="Show the Warped (perspective shifted) image")
        arg_map.add_argument("-n", "--neural", required=False, action="store_true",
                             help="Show the Image to be passed to the Neural Network")
        arg_map.add_argument("-l", "--loglevel", required=False,
                             help="Log level to be used")
        return vars(arg_map.parse_args())


    def loop(self, perspective, img_map=False):
        '''
        Loop to use when actually playing RBI

        Args:
            perspective: dict containing Transformation matrix M, height H,
            and width W
        Optional Args:
            img_map: dict of intermediate image matrices to show; mainly for
            debugging
        Returns:
            None
        Raises:
            None
        '''
        while True:
            _, frame = self.feed.read()

            if img_map and img_map['original']:
                cv2.imshow("My Frame", frame)

            warped = self.warp_frame(frame, perspective)

            for key, val in self.templates.items():
                resp = imgutils.match_template(warped, val)
                if resp[1] > 0.6:
                    print key

            if img_map and img_map['warped']:
                cv2.imshow('Warped', warped)

            nn_frame = self.prepare_nn_frame(warped,
                                             self.nn_matrix_info['height'],
                                             self.nn_matrix_info['width'])
            #print "DEBUG - nn_frame.shape = %s" % str(nn_frame.shape)
            if img_map and img_map['neural']:
                cv2.imshow('NN', nn_frame)

            #nn_vector = nn_frame.ravel()

            if cv2.waitKey(1) & 0xFF == ord('1'):
                break


    @staticmethod
    def warp_frame(frame, perspective):
        '''
        Warp input view frame to show head-on perspective

        Args:
            frame: input view frame
            perspective: dict with warp matrix, height, width, and 'c'
        Returns:
            warped matrix
        Raises:
            None
        '''
        translation_matrix = perspective['M']
        height = perspective['h']
        width = perspective['w']
        #c = perspective['c']
        warped = cv2.warpPerspective(frame, translation_matrix, (width, height))

        return warped


    @staticmethod
    def prepare_nn_frame(frame, height=None, width=None):
        '''
        Resize frame and convert to grayscale

        If neither height nor widht are provided, the dimentions of the input
        frame are retained.
        If only one of either height or width is provided, the missing
        dimesion is calculated to keep the height/width ratio the same while
        changing the provided dimension.

        Args:
            frame: frame to be converted
        Optional Args:
            height: height of the converted frame
            width: width of the converted frame
        Returns:
            Grayscale frame with scaled height and width if specified
        Raises:
            None
        '''
        grayed = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #scaled = imgutils.scale_2d(grayed, height, width)
        scaled = cv2.resize(grayed, (height, width), interpolation=cv2.INTER_AREA)
        return scaled

    
    def load_game(self,
                  emulator_path='/usr/bin/fceux',
                  #emulator_path='/usr/bin/nestopia',
                  #emulator_path='/usr/bin/fakenes',
                  rom_path='/home/jreinhart/projects/rbi/roms/RBI-Unlicensed.zip',
                  fullscreen=True):
        subprocess.Popen([emulator_path, rom_path])
        if fullscreen:
            time.sleep(0.25)
            self.kbrd.fullscreen()

    def quit_game(self):
        self.kbrd.quit()

    def restart_game(self):
        self.quit_game()
        time.sleep(2)
        self.load_game()


    def random_select_start(self):
        '''
        Begin a 1-player game with teams randomly selected

        Parameters:
            None
        Return Value:
            None
        '''
        self.kbrd.select()
        self.kbrd.start()


    def __configure_logger(self, log_level):
        logging.basicConfig(level=log_level)
        self._log = logging.getLogger('RBI_Class')


    def __configure_camera(self):
        self.camera = camera.Camera()
        self.feed = self.camera.get_feed()

        directory = os.path.dirname(os.path.abspath(
            inspect.getfile(inspect.currentframe())))
        cam_cfg = json.load(open(directory + '/../camera.cfg'))
        self.camera.set_brightness(int(cam_cfg['Brightness']))
        self.camera.set_focus(int(cam_cfg['Focus']))
        self._log.debug("Brightness set to %s", str(self.camera.get_brightness()))
        self._log.debug("Focus set to %s", str(self.camera.get_focus()))


    def __configure_arduino(self, port='/dev/ttyACM0', baudrate=57600):
        self.arduino = arduino.Arduino(port=port, baudrate=baudrate)
        self._log.debug("Configured Arduino on port %s, baudrate %d", port, baudrate)
        self.arduino.write(BLUE, OFF)
        self.arduino.write(GREEN, OFF)
        self.arduino.write(RED, FAST_BLINK)


    def __del__(self):
        try:
            self.feed.release()
            cv2.destroyAllWindows()
        except AttributeError:
            self._log.warn("Attribute Error when closing RBI")


def main():
    '''
    Called if __name__ == __main__
    '''
    arg_dict = RBI.parse_args()
    print("Arg dict:")
    pp(arg_dict)

    blue_hex = "063793"
    #blue_hex = "052e7a"

    #blue_hex = "052C72"

    #blue_hex = "042562"
    #blue_hex = "031c49"

    matrix_height = 84
    matrix_width = 84

    # Determines which intermediate frames will be shown
    img_map = arg_dict

    log_level = arg_dict['loglevel']
    if log_level is None:
        log_level = 'info'
    rbi = RBI(matrix_height, matrix_width, log_level)

    rbi.load_game()

    #if arg_dict['calibrate']:
    #    camutils.calibrate_camera(rbi.feed, img_map)

    #perspective = camutils.get_perspective(rbi.feed, blue_hex, 0.25, img_map)
    perspective = camutils.get_perspective(rbi.feed, blue_hex, 0.35, img_map)
    print("FOUND THE PERSPECTIVE!")
    rbi.arduino.write(BLUE, OFF)
    rbi.arduino.write(GREEN, ON)
    rbi.arduino.write(RED, OFF)

    cv2.destroyAllWindows()
    rbi.loop(perspective, img_map)

if __name__ == '__main__':
    main()

