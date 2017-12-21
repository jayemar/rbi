#!/usr/bin/env python

import subprocess
import time
import pdb

from pynput.keyboard import Key, Controller

fceux = "/usr/bin/fceux"
rom = "/home/jreinhart/projects/rbi/roms/RBI-Unlicensed.zip"


if __name__ == '__main__':
    k = Controller()

    #subprocess.Popen([fceux, rom])
    subprocess.Popen(["pluma"])

    time.sleep(1)
    print("sleep 1")
    k.press('g')
    k.release('g')

    time.sleep(1)
    print("sleep 1")
    k.press('g')
    k.release('g')

    time.sleep(1)
    print("sleep 1")
    k.press('g')
    k.release('g')

    time.sleep(1)
    print("sleep 1")
    k.press('g')
    k.release('g')
