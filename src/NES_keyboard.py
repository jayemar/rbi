#!/usr/bin/env python

import subprocess
import time
import pdb

from evdev import UInput
from evdev import ecodes as e


DOWN_TIME=0.350

class Keyboard:
    def __init__(self, emulator='/usr/bin/fceux',
                 rom='/home/jreinhart/projects/rbi/roms/RBI-Unlicensed.zip'):
        self.emulator = emulator
        self.rom = rom
        self.ui = UInput()


    def quit(self):
        self.__keys_down([e.KEY_LEFTCTRL, e.KEY_Q])
        self.__keys_up([e.KEY_LEFTCTRL, e.KEY_Q])

    def fullscreen(self):
        self.__keys_down([e.KEY_LEFTALT, e.KEY_ENTER])
        self.__keys_up([e.KEY_LEFTALT, e.KEY_ENTER])


    def buttonA(self):
        self.__keys_down([e.KEY_K])
        self.__keys_up([e.KEY_K])

    def buttonB(self):
        self.__keys_down([e.KEY_J])
        self.__keys_up([e.KEY_J])


    def up(self):
        self.__keys_down([e.KEY_W])
        self.__keys_up([e.KEY_W])

    def down(self):
        self.__keys_down([e.KEY_S])
        self.__keys_up([e.KEY_S])

    def left(self):
        self.__keys_down([e.KEY_A])
        self.__keys_up([e.KEY_A])

    def right(self):
        self.__keys_down([e.KEY_D])
        self.__keys_up([e.KEY_D])


    def upA(self):
        self.__keys_down([e.KEY_W, e.KEY_K])
        self.__keys_up([e.KEY_W, e.KEY_K])

    def downA(self):
        self.__keys_down([e.KEY_S, e.KEY_K])
        self.__keys_up([e.KEY_S, e.KEY_K])

    def leftA(self):
        self.__keys_down([e.KEY_A, e.KEY_K])
        self.__keys_up([e.KEY_A, e.KEY_K])

    def rightA(self):
        self.__keys_down([e.KEY_D, e.KEY_K])
        self.__keys_up([e.KEY_D, e.KEY_K])


    def upB(self):
        self.__keys_down([e.KEY_W, e.KEY_J])
        self.__keys_up([e.KEY_W, e.KEY_J])

    def downB(self):
        self.__keys_down([e.KEY_S, e.KEY_J])
        self.__keys_up([e.KEY_S, e.KEY_J])

    def leftB(self):
        self.__keys_down([e.KEY_A, e.KEY_J])
        self.__keys_up([e.KEY_A, e.KEY_J])

    def rightB(self):
        self.__keys_down([e.KEY_D, e.KEY_J])
        self.__keys_up([e.KEY_D, e.KEY_J])


    def upAB(self):
        self.__keys_down([e.KEY_W, e.KEY_K, e.KEY_J])
        self.__keys_up([e.KEY_W, e.KEY_K, e.KEY_J])

    def downAB(self):
        self.__keys_down([e.KEY_S, e.KEY_K, e.KEY_J])
        self.__keys_up([e.KEY_S, e.KEY_K, e.KEY_J])

    def leftAB(self):
        self.__keys_down([e.KEY_A, e.KEY_K, e.KEY_J])
        self.__keys_up([e.KEY_A, e.KEY_K, e.KEY_J])

    def rightAB(self):
        self.__keys_down([e.KEY_D, e.KEY_K, e.KEY_J])
        self.__keys_up([e.KEY_D, e.KEY_K, e.KEY_J])


    def ne(self):
        self.__keys_down([e.KEY_W, e.KEY_D])
        self.__keys_up([e.KEY_W, e.KEY_D])

    def se(self):
        self.__keys_down([e.KEY_S, e.KEY_D])
        self.__keys_up([e.KEY_S, e.KEY_D])

    def sw(self):
        self.__keys_down([e.KEY_S, e.KEY_A])
        self.__keys_up([e.KEY_S, e.KEY_A])

    def nw(self):
        self.__keys_down([e.KEY_W, e.KEY_A])
        self.__keys_up([e.KEY_W, e.KEY_A])


    def neA(self):
        self.__keys_down([e.KEY_W, e.KEY_D, e.KEY_K])
        self.__keys_up([e.KEY_W, e.KEY_D, e.KEY_K])

    def seA(self):
        self.__keys_down([e.KEY_S, e.KEY_D, e.KEY_K])
        self.__keys_up([e.KEY_S, e.KEY_D, e.KEY_K])

    def swA(self):
        self.__keys_down([e.KEY_S, e.KEY_A, e.KEY_K])
        self.__keys_up([e.KEY_S, e.KEY_A, e.KEY_K])

    def nwA(self):
        self.__keys_down([e.KEY_W, e.KEY_A, e.KEY_K])
        self.__keys_up([e.KEY_W, e.KEY_A, e.KEY_K])


    def neB(self):
        self.__keys_down([e.KEY_W, e.KEY_D, e.KEY_J])
        self.__keys_up([e.KEY_W, e.KEY_D, e.KEY_J])

    def seB(self):
        self.__keys_down([e.KEY_S, e.KEY_D, e.KEY_J])
        self.__keys_up([e.KEY_S, e.KEY_D, e.KEY_J])

    def swB(self):
        self.__keys_down([e.KEY_S, e.KEY_A, e.KEY_J])
        self.__keys_up([e.KEY_S, e.KEY_A, e.KEY_J])

    def nwB(self):
        self.__keys_down([e.KEY_W, e.KEY_A, e.KEY_J])
        self.__keys_up([e.KEY_W, e.KEY_A, e.KEY_J])


    def neAB(self):
        self.__keys_down([e.KEY_W, e.KEY_D, e.KEY_K, e.KEY_J])
        self.__keys_up([e.KEY_W, e.KEY_D, e.KEY_K, e.KEY_J])

    def seAB(self):
        self.__keys_down([e.KEY_S, e.KEY_D, e.KEY_K, e.KEY_J])
        self.__keys_up([e.KEY_S, e.KEY_D, e.KEY_K, e.KEY_J])

    def swAB(self):
        self.__keys_down([e.KEY_S, e.KEY_A, e.KEY_K, e.KEY_J])
        self.__keys_up([e.KEY_S, e.KEY_A, e.KEY_K, e.KEY_J])

    def nwAB(self):
        self.__keys_down([e.KEY_W, e.KEY_A, e.KEY_K, e.KEY_J])
        self.__keys_up([e.KEY_W, e.KEY_A, e.KEY_K, e.KEY_J])


    def select(self):
        self.__keys_down([e.KEY_G], True)
        self.__keys_up([e.KEY_G], False)

    def start(self):
        self.__keys_down([e.KEY_H], True)
        self.__keys_up([e.KEY_H], False)
    

    def __keys_down(self, keys, wait=True):
        for key in keys:
            self.ui.write(e.EV_KEY, key, 1)
        self.ui.syn()
        if wait:
            time.sleep(DOWN_TIME)

    def __keys_up(self, keys, wait=False):
        for key in keys:
            self.ui.write(e.EV_KEY, key, 0)
        self.ui.syn()
        if wait:
            time.sleep(DOWN_TIME)


if __name__ == '__main__':
    kbrd = Keyboard()
    print("Keyboard created")
    subprocess.Popen([kbrd.emulator, kbrd.rom])

    time.sleep(2)
    print("Pressed Select")
    kbrd.select()


    time.sleep(1)
    print("Start game")
    kbrd.start()

    time.sleep(1)
    print("Select Team #1")
    kbrd.buttonA()

    time.sleep(1)
    print("Select Team #2")
    kbrd.buttonA()

    time.sleep(2)
    print("Select pitcher")
    kbrd.buttonA()

    time.sleep(12.95)
    print("Swing bat")
    kbrd.buttonA()

