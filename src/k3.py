#!/usr/bin/env python

import subprocess
import time
import pdb

from pykeyboard import PyKeyboard

fceux = "/usr/bin/fceux"
rom = "/home/jreinhart/projects/rbi/roms/RBI-Unlicensed.zip"


if __name__ == '__main__':
    k = PyKeyboard()

    subprocess.Popen([fceux, rom])
    #subprocess.Popen(["pluma"])

    time.sleep(1)
    print("sleep 1")
    k.tap_key('g')

    time.sleep(1)
    print("sleep 1")
    k.tap_key('g')

    time.sleep(1)
    print("sleep 1")
    k.press_key('g')

    time.sleep(1)
    print("sleep 1")
    k.release_key('g')

    time.sleep(1)
    print("sleep 1")
    k.tap_key('h')

