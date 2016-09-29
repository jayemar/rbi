'''
Class to represent an Arduino microcontroller board
'''
import serial


class Arduino(object):
    '''
    Arduino class
    '''
    def __init__(self, port='/dev/ttyACM0', baudrate=57600):
        '''
        Configure system to communicate with Arduino

        Optional Args:
            port: serial port on which to communicate with Arduino
            baudrate: baud rate at which Arduino is set to communicate
        Returns:
            None
        Raises:
            None
        '''
        self.tty = serial.Serial(port=port, baudrate=baudrate)

    def write(self, string):
        '''
        Convenience method to send characters to Arduino

        Args:
            string: character string to send to Arduino
        Returns:
            None
        Raises:
            None
        '''
        self.tty.write(string + '\r\n')

