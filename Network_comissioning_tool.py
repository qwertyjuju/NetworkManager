import time
import logging
import logging.handlers
import pathlib
import serial

commands=["ena",
          "conf t",
          "hostname ju",
          "enable secret azerty123"
          ]

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


class Writer:
    def __init__(self,port_com):
        self._ser = serial.Serial(timeout=1)
        self._ser.baudrate = 9600
        self._ser.port = port_com
        self.initialised = 0
        self._ser.open()
        log("info","serial opened")
        self.initialised = 0
        while not self.initialised:
            self._ser.write(b'\n')
            line = self._ser.readline().decode("utf-8").lower().replace('\r\n',"")
            log("info", "console input: ", line)
            if "initial configuration dialog" in line:
                self.write_command("no")
            elif line[-1:] in [">", "#"]:
                self.initialised = 1
            time.sleep(1)

    def write_command(self, command=None):
        if command:
            self._ser.write(str.encode(command+"\n"))
        else:
           self._ser.write(str.encode("\n"))
        
    def write_commands(self, command):
        self._ser.write(b'\n')
        for command in commands:
            self.write_command(command)
            time.sleep(1)

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

LOGGER=init_logger()
wr = Writer("COM1")
wr.write_commands(commands)