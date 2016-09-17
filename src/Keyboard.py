import uinput
import time
import subprocess

import pdb

fceux_cmd = "/usr/bin/fceux /home/jreinhart/projects/rbi/roms/RBI_Baseball_USA.zip"
fceux_cmd_1 = "/usr/bin/fceux"
fceux_cmd_2 = "/home/jreinhart/projects/rbi/roms/RBI_Baseball_USA.zip"

class Keyboard:
    def __init__(self):
        self.keys = uinput.Device([
            uinput.KEY_G,
            uinput.KEY_H,

            uinput.KEY_W,
            uinput.KEY_A,
            uinput.KEY_S,
            uinput.KEY_D,

            uinput.KEY_K,
            uinput.KEY_J])

    def up(self):
        #self.keys.emit(uinput.KEY_W)
        self.keys.emit_click(uinput.KEY_W)

    def down(self):
        self.keys.emit(uinput.KEY_S)

    def left(self):
        self.keys.emit(uinput.KEY_A)

    def right(self):
        self.keys.emit(uinput.KEY_D)


    def upA(self):
        self.keys.emit(uinput.KEY_W)
        self.keys.emit(uinput.KEY_K)

    def downA(self):
        self.keys.emit(uinput.KEY_S)
        self.keys.emit(uinput.KEY_K)

    def leftA(self):
        self.keys.emit(uinput.KEY_A)
        self.keys.emit(uinput.KEY_K)

    def rightA(self):
        self.keys.emit(uinput.KEY_D)
        self.keys.emit(uinput.KEY_K)


    def upB(self):
        self.keys.emit(uinput.KEY_W)
        self.keys.emit(uinput.KEY_J)

    def downB(self):
        self.keys.emit(uinput.KEY_S)
        self.keys.emit(uinput.KEY_J)

    def leftB(self):
        self.keys.emit(uinput.KEY_A)
        self.keys.emit(uinput.KEY_J)

    def rightB(self):
        self.keys.emit(uinput.KEY_D)
        self.keys.emit(uinput.KEY_J)


    def upAB(self):
        self.keys.emit(uinput.KEY_W)
        self.keys.emit(uinput.KEY_K)
        self.keys.emit(uinput.KEY_J)

    def downAB(self):
        self.keys.emit(uinput.KEY_S)
        self.keys.emit(uinput.KEY_K)
        self.keys.emit(uinput.KEY_J)

    def leftAB(self):
        self.keys.emit(uinput.KEY_A)
        self.keys.emit(uinput.KEY_K)
        self.keys.emit(uinput.KEY_J)

    def rightAB(self):
        self.keys.emit(uinput.KEY_D)
        self.keys.emit(uinput.KEY_K)
        self.keys.emit(uinput.KEY_J)


    def ne(self):
        self.keys.emit(uinput.KEY_W)
        self.keys.emit(uinput.KEY_D)

    def se(self):
        self.keys.emit(uinput.KEY_S)
        self.keys.emit(uinput.KEY_D)

    def sw(self):
        self.keys.emit(uinput.KEY_S)
        self.keys.emit(uinput.KEY_A)

    def nw(self):
        self.keys.emit(uinput.KEY_W)
        self.keys.emit(uinput.KEY_A)


    def neA(self):
        self.keys.emit(uinput.KEY_W)
        self.keys.emit(uinput.KEY_D)
        self.keys.emit(uinput.KEY_K)

    def seA(self):
        self.keys.emit(uinput.KEY_S)
        self.keys.emit(uinput.KEY_D)
        self.keys.emit(uinput.KEY_K)

    def swA(self):
        self.keys.emit(uinput.KEY_S)
        self.keys.emit(uinput.KEY_A)
        self.keys.emit(uinput.KEY_K)

    def nwA(self):
        self.keys.emit(uinput.KEY_W)
        self.keys.emit(uinput.KEY_A)
        self.keys.emit(uinput.KEY_K)


    def neB(self):
        self.keys.emit(uinput.KEY_W)
        self.keys.emit(uinput.KEY_D)
        self.keys.emit(uinput.KEY_J)

    def seB(self):
        self.keys.emit(uinput.KEY_S)
        self.keys.emit(uinput.KEY_D)
        self.keys.emit(uinput.KEY_J)

    def swB(self):
        self.keys.emit(uinput.KEY_S)
        self.keys.emit(uinput.KEY_A)
        self.keys.emit(uinput.KEY_J)

    def nwB(self):
        self.keys.emit(uinput.KEY_W)
        self.keys.emit(uinput.KEY_A)
        self.keys.emit(uinput.KEY_J)


    def neAB(self):
        self.keys.emit(uinput.KEY_W)
        self.keys.emit(uinput.KEY_D)
        self.keys.emit(uinput.KEY_K)
        self.keys.emit(uinput.KEY_J)

    def seAB(self):
        self.keys.emit(uinput.KEY_S)
        self.keys.emit(uinput.KEY_D)
        self.keys.emit(uinput.KEY_K)
        self.keys.emit(uinput.KEY_J)

    def swAB(self):
        self.keys.emit(uinput.KEY_S)
        self.keys.emit(uinput.KEY_A)
        self.keys.emit(uinput.KEY_K)
        self.keys.emit(uinput.KEY_J)

    def nwAB(self):
        self.keys.emit(uinput.KEY_W)
        self.keys.emit(uinput.KEY_A)
        self.keys.emit(uinput.KEY_K)
        self.keys.emit(uinput.KEY_J)


    def select(self):
        #self.keys.emit_click(uinput.KEY_G)
        self.keys.emit(uinput.KEY_G, 5)

    def start(self):
        #self.keys.emit_click(uinput.KEY_H)
        self.keys.emit(uinput.KEY_H, 5)


if __name__ == '__main__':
    kbrd = Keyboard()
    #subprocess.call([fceux_cmd_1, fceux_cmd_2])
    subprocess.Popen([fceux_cmd_1, fceux_cmd_2])

    time.sleep(3)
    kbrd.select()
    print("Pressed Select")

    time.sleep(1)
    kbrd.select()
    print("Pressed Select")

    time.sleep(1)
    kbrd.select()
    print("Pressed Select")

    time.sleep(1)
    kbrd.select()
    print("Pressed Select")

    time.sleep(1)
    kbrd.start()
    print("Pressed Start")

    print("Keyboard created")
