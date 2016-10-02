'''
Class to represent an Arduino microcontroller board
'''
import time
import threading
import serial


class Arduino(object):
    '''
    Arduino class
    '''
    def __init__(self, port='/dev/ttyACM0', baudrate=57600):
        '''
        Configure system to communicate with Arduino

        Parameters:
            port        - Optional; serial port on which to communicate with
                          Arduino
            baudrate    - Optional; baud rate at which Arduino is set to
                          communicate
        Return value:
            None
        '''
        self.tty = serial.Serial(port=port, baudrate=baudrate)
        self.threads = []


    def write(self, pin_number, string):
        '''
        Convenience method to send characters to Arduino

        Args:
            string: character string to send to Arduino
        Return value:
            None
        '''
        self.tty.write(pin_number + string + '\r\n')


    def blink_led(self, pin_number=11, interval=0.5):
        '''
        Blink an LED with a full cycle frequency of 'interval'

        Parameters:
            pin_number  - pin number mapping to pin on the Arduino Uno
            interval    - Optional; time in seconds to run through on/off
            cycle
        Returns:
            None
        '''
        thread = threading.Thread(target=self.__blink_led,
                                  args=(pin_number, interval))
        self.threads.append(thread)
        thread.start()


    def __blink_led(self, pin_number, interval):
        '''
        Blink an LED with a full cycle frequency of 'interval'

        Parameters:
            pin_number  - pin number mapping to pin on the Arduino Uno
            interval    - Optional; time in seconds to run through on/off
            cycle
        Returns:
            None
        '''
        while True:
            self.write(pin_number, '1')
            time.sleep(interval/2.0)
            self.write(pin_number, '0')
            time.sleep(interval/2.0)

