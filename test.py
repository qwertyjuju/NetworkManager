import serial
import logging

wr = Writer("COM1")

wr.write_command(b"enable\n")
print(ser.read_until(b"#"))
ser.close()

class writer:
    def __init__(self,port_com):
        self._ser = serial.Serial()
        self._ser.baudrate = 9600
        self._ser.port = port_com
        self._ser.open()
        
    def write_command(self):
        self._ser.write()