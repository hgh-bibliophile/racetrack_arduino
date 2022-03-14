from serial.tools.list_ports import comports
import serial
import inquirer
import time

from .heat import Heat


class PortException(BaseException):
    pass

class ArduinoException(BaseException):
    pass

def select_port(msg: str):
    ports = sorted(comports())

    if len(ports) == 0:
        raise PortException('No COM Ports Avaliable')

    return inquirer.list_input(msg, choices=ports)[0]

class Arduino:
    """Handles all arduino communication via serial bus"""

    arduino = None

    def __init__(self, com: str):
        self.com = com

    def connect(self):
        """Connect to the arduino at COM port `self.com`"""

        if self.arduino and self.arduino.is_open:
            return

        try:
            self.arduino = serial.Serial(self.com, 9600, timeout=5)
            self.connected = True
            time.sleep(1)  # Allow arduino to reset
        except serial.SerialException as e:
            raise ArduinoException(e)

    def disconnect(self):
        self.arduino.close()

    def raise_error(self, msg):
        self.disconnect()
        raise ArduinoException(msg)

    def readline(self):
        """Read, decode, and return one decoded from the arduino serial connection"""
        try:
            return bytes.decode(self.arduino.readline())

        except serial.SerialException as e:
            raise ArduinoException('Serial readline from arduino failed. Check usb connection.')

    def sendline(self, msg, ran_before=False):
        try:
            b_msg = bytes(msg + '\n', 'ascii')
            self.arduino.write(b_msg)

        except serial.SerialException as e:
            raise ArduinoException('Serial write to arduino failed. Check usb connection.')

    def start_race(self):
        """Signal `self.arduino` to start race, listen for acknowledgement."""

        self.sendline('START RACE')  # Arduino is looping, waiting for 'START RACE' command

        response = self.readline()
        if 'ERR' in response:  # Some sensors are high
            self.raise_error("Arduino arming failed: check sensors")
        elif "ACK" not in response:  # Arduino isn't working properly
            self.raise_error("Did not receive 'ACK' or 'ERR' response from Arduino")


    def get_race(self):
        """Return the race data as a Heat instance"""
        self.arduino.timeout = 300
        try:
            data_trigger = self.readline()
            if "START" not in data_trigger:
                self.raise_error("Did not recieve expected 'START DATA' or 'START ERROR' after 'ACK'")

            heat = Heat()

            if 'ERR' in data_trigger:
                heat.err = True

            while True:
                data = self.readline()

                if "END" in data:
                    break

                heat.add_bit_change(data)

            self.disconnect()
            return heat

        except serial.SerialTimeoutException as e:
            raise ArduinoException(e)


