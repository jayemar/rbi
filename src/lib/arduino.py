import serial


class Arduino:
    def __init__(self, port='/dev/ttyACM0', baudrate=57600):
        self.tty = serial.Serial(port=port, baudrate=baudrate)

    def write(self, string):
        self.tty.write(string + '\r\n')
