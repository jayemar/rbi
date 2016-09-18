#!/usr/bin/env python

import pyautogui
import subprocess
import time
import pdb

fceux = "/usr/bin/fceux"
rom = "/home/jreinhart/projects/rbi/roms/RBI-Unlicensed.zip"


if __name__ == '__main__':
    subprocess.Popen([fceux, rom])

    time.sleep(1)
    print("sleep 1")
    pyautogui.press('g')

    time.sleep(1)
    print("sleep 1")
    pyautogui.press('h')

    time.sleep(1)
    print("sleep 1")
    pyautogui.press('g')

    time.sleep(1)
    print("sleep 1")
    pyautogui.typewrite('g')

    time.sleep(1)
    print("sleep 1")
    pyautogui.typewrite('h')

