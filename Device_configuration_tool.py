import multiprocessing as proc
from pathlib import Path
import logging
import logging.handlers
import time
import re
import serial


commands=["ena",
          "conf t",
          "hostname ju",
          "enable secret azerty123"
          ]
"""
logger
"""

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
    fh = logging.handlers.RotatingFileHandler(filename=Path("logs/Device_configuration.log"),
                                              maxBytes=1048576, backupCount=5, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


LOGGER = init_logger()


def log(logtype, *texts):
    text = " ".join(texts)
    if logtype.lower() == "info":
        LOGGER.info(text)
    elif logtype.lower() == "warning":
        LOGGER.warning(text)
    elif logtype.lower() == "error":
        LOGGER.error(text)
    else:
        LOGGER.warning("message type incorrect. Message: " + text)


class SerialDisplay:
    def __init__(self, display):
        self.display = display
        self.display.setReadOnly(0)

    def add(self):
        pass


"""
SerialInterface
"""


class SerialInterface:
    def __init__(self, port_com):
        self._ser = serial.Serial(
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            stopbits=serial.STOPBITS_ONE,
            parity=serial.PARITY_NONE,
            timeout=1)
        self._ser.port = port_com
        self._ser.open()
        log("info", "serial opened")
        self.initialised = 0
        last_line = self.write_command(sleeptime=10)
        print(last_line)
        regex= re.compile('^(\w+[#>])$')
        while not self.initialised:
            last_line = self.write_command()
            if "[yes/no]:" in last_line:
                self.write_command("no")
                out = self.write_command(sleeptime=3)
                print(out)
            elif regex.search(last_line) is not None:
                    print("init complete")
                    self.initialised=1
            print(last_line)


        """
        while not self.initialised:
            line=self.write_command()
            if line:
                print(line)
            if "[yes/no]:" in line:
                self.write_command("no")
            if line[-1:] in [">", "#"]:
                self.initialised = 1
        """
    """
    def write_command(self, command=None, sleeptime=1):
        out = ""
        self._ser.reset_input_buffer()
        if command:
            self._ser.write(str.encode(command + " \r\n"))
        else:
            self._ser.write(str.encode("\r\n"))
        time.sleep(sleeptime)
        while self._ser.inWaiting()>0:
            out+= str(self._ser.read(self._ser.inWaiting()).decode("utf-8").lower().replace('\r\n',""))
        return out
    """
    def write_command(self, command=None, sleeptime=1):
        if command:
            self._ser.writelines([str.encode(command+"\r\n")])
        else:
            self._ser.writelines([str.encode("\r\n")])
        time.sleep(sleeptime)
        return self._ser.readline().decode("utf-8").lower().replace('\r\n',"")

    def write_commands(self, commands):
        for command in commands:
            self.write_command(command)

    def print_line(self):
        print(self._ser.readline())

    def loop(self):
        print(self.write_command("ena"))
        print(self.write_command("reload"))
        print(self.write_command())

    def get_mode(self):
        pass

    def close(self):
        """
        Permet de fermer la connexion entre l'hôte et la machine
        :return:
        """
        self._ser.close()

    def line(self):
        """
        Permet d'afficher la dernière ligne. Fonction d'affichage
        :return: La dernière ligne
        """
        return self._ser.readline()


if __name__ == "__main__":
    t = SerialInterface("COM7")
    t.loop()


"""
DUMP



        while not self.initialised:
            self._ser.write(b'\n')
            nbbytes = self._ser.inWaiting()
            print(nbbytes)
            if nbbytes > 0:
                line = str(self._ser.read(nbbytes).decode("utf-8").lower().replace('\r\n',""))
                print(type(line), line)
                if "[yes/no]:" in line:
                    self.write_command("no")
                if line[-1:] in [">", "#"]:
                    self.initialised = 1
            self._ser.reset_input_buffer()
            time.sleep(0.5)
            
            
        while not self.initialised:
            self._ser.break_condition = 1
            self._ser.write(b'\n')
            line = self._ser.readline().decode("utf-8").lower().replace('\r\n',"")
            self._ser.break_condition = 0
            log("info", "console output: ", line)
            if "[yes/no]:" in line:
                self.write_command("no")
            if line[-1:] in [">", "#"]:
                self.initialised = 1
            else:
                print(self._ser.readline().decode("utf-8").lower().replace('\r\n',""))
                print("no")
            time.sleep(1)
            
        self._ser.readline().decode("utf-8").lower().replace('\r\n',"")
"""
