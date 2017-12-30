#!/usr/bin/env python

import subprocess
import time
import pdb

from evdev import uinput
from evdev import UInput
from evdev import ecodes as e

fceux = "/usr/bin/fceux"
rom = "/home/jreinhart/projects/rbi/roms/RBI-Unlicensed.zip"


if __name__ == '__main__':
    #ui = uinput.UInput()
    ui = UInput()

    subprocess.Popen([fceux, rom])
    #subprocess.Popen(["pluma"])

    time.sleep(8)
    print("sleep 8")
    ui.write(e.EV_KEY, e.KEY_G, 1)  # 1 for key down
    ui.syn()
    time.sleep(0.250)
    ui.write(e.EV_KEY, e.KEY_G, 0)  # 0 for key up
    ui.syn()
    time.sleep(0.250)

    time.sleep(1)
    print("sleep 1")
    ui.write(e.EV_KEY, e.KEY_G, 1)
    ui.syn()
    time.sleep(0.250)
    ui.write(e.EV_KEY, e.KEY_G, 0)
    ui.syn()
    time.sleep(0.250)

    time.sleep(1)
    print("sleep 1")
    ui.write(e.EV_KEY, e.KEY_G, 1)
    ui.syn()
    time.sleep(0.250)
    ui.write(e.EV_KEY, e.KEY_G, 0)
    ui.syn()
    time.sleep(0.250)

    time.sleep(1)
    print("sleep 1")
    ui.write(e.EV_KEY, e.KEY_G, 1)
    ui.syn()
    time.sleep(0.250)
    ui.write(e.EV_KEY, e.KEY_G, 0)
    ui.syn()
    time.sleep(0.250)
