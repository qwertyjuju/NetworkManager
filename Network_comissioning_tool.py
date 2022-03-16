import serial
import logging


class writer:
    def __init__(self,port_com):
        self._ser = serial.Serial()
        self._ser.baudrate = 9600
        self._ser.port = port_com
        self._ser.open()
        self._ser
        while str(self._ser.readline()).lower() is "would you like to enter the initial configuration dialog? [yes/no]: \\r\\n":

        
    def write_command(self, command):
        self._ser.open()
        self._ser.write(command)
        self._ser.close()

    def write_commands(self, commands):
        self._ser.open()
        for command in commands:
            self._ser.write(command)