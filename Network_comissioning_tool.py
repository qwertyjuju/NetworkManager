import time
import logging
import logging.handlers
import pathlib
import serial



def init_logger():
    """
    creates logger object. The logger has 2 handlers: One handler
    for showing logs in terminal and one handler for saving logs
    in file.
    """
    logger = logging.getLogger('Network_comissioning')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    fh = logging.handlers.RotatingFileHandler(filename=pathlib.Path("logs/Network_comissioning.log"),
                                              maxBytes=1048576, backupCount=5, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


class writer:
    def __init__(self,port_com):
        self._ser = serial.Serial()
        self._ser.baudrate = 9600
        self._ser.port = port_com
        self.initialised = 0
        self._ser.open()
        self.initialised = 0
        while not self.initialised:
            self._ser.write(b"\n")
            line = str(self._ser.readline()).lower()
            if line is "would you like to enter the initial configuration dialog? [yes/no]: \\r\\n":
                self._ser.write(b"no\n")
            elif line[:-1] in [">", "#"]:
                self.initialised = 1
            time.sleep(5)
        self._ser.close()

    def write_command(self, command):
        self._ser.open()
        self._ser.write(command)
        self._ser.close()

    def write_commands(self, commands):
        self._ser.open()
        for command in commands:
            self._ser.write(command)
        self._ser.close()