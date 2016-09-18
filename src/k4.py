#!/usr/bin/env python

import subprocess
import time
import pdb

from evdev import uinput, ecodes as e

fceux = "/usr/bin/fceux"
rom = "/home/jreinhart/projects/rbi/roms/RBI-Unlicensed.zip"


if __name__ == '__main__':
    ui = uinput.UInput()

    #subprocess.Popen([fceux, rom])
    subprocess.Popen(["pluma"])

    time.sleep(1)
    print("sleep 1")
    #ui.write(e.EV_KEY, e.KEY_G, 1)
    ui.write(e.EV_KEY, e.KEY_G, 0)

    time.sleep(1)
    print("sleep 1")
    #ui.write(e.EV_KEY, e.KEY_G, 1)
    ui.write(e.EV_KEY, e.KEY_G, 0)

    time.sleep(1)
    print("sleep 1")
    #ui.write(e.EV_KEY, e.KEY_G, 1)
    ui.write(e.EV_KEY, e.KEY_G, 0)

    time.sleep(1)
    print("sleep 1")
    #ui.write(e.EV_KEY, e.KEY_G, 1)
    ui.write(e.EV_KEY, e.KEY_G, 0)

