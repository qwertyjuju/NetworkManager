import sys
import time
import logging
import logging.handlers
from pathlib import Path
import serial
import json
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5 import uic

commands=["ena",
          "conf t",
          "hostname ju",
          "enable secret azerty123"
          ]
"""
UI
"""

class CommissionningTool:
    def __init__(self, uifile):
            self.data = dict()
            self.deviceconfig = DeviceConfig()
            self.app = QApplication(sys.argv)
            Ui, Window = uic.loadUiType(uifile)
            self.window = Window()
            self.ui = Ui()
            self.ui.setupUi(self.window)
            self.init_data("data/device_data.json")
            self.init_ui()
            self.window.show()
            self.app.exec()

    
    def init_ui(self):
        self.ui.B_exit.clicked.connect(self.exit_prog)
        self.ui.LE_device_name.editingFinished.connect(self.update_name)
        self.ui.CB_device_type.currentIndexChanged.connect(self.update_devices)
        self.ui.CB_device_ref.addItems(self.data[self.ui.CB_device_type.currentText()])
        self.ui.CB_device_ref.activated.connect(self.update_ports)
        self.ui.B_create_device.clicked.connect(self.deviceconfig.save_json)
        self.update_ports()

    def init_data(self, file):
        with open(file, 'r', encoding="UTF-8") as f:
            self.data.update(json.load(f))
        for cle in self.data.keys():
            for cle_2, data in self.data[cle].items():
                ports = []
                for port in data["ports"]:
                    ports.extend([port["type"] + str(i) for i in range(port["nb"])])
                data["ports"] = ports

        log("info", "commissioning tool data : ",str(self.data))

    def update_devices(self):
        self.ui.CB_device_ref.clear()
        self.ui.CB_device_ref.addItems(self.data[self.ui.CB_device_type.currentText()])
        self.deviceconfig.set_device_type(self.ui.CB_device_type.currentText())
        self.update_ports()

    def update_name(self):
        if self.ui.LE_device_name.text() != "":
            self.deviceconfig.set_name(self.ui.LE_device_name.text())

    def update_ports(self):
        self.ui.LW_ports.clear()
        self.ui.LW_ports.addItems(self.data[self.ui.CB_device_type.currentText()][self.ui.CB_device_ref.currentText()]["ports"])
        self.deviceconfig.set_ports(self.data[self.ui.CB_device_type.currentText()][self.ui.CB_device_ref.currentText()]["ports"])

    def exit_prog(self):
        sys.exit()


class DeviceConfig:

    def __init__(self):
        self.name = None
        self.data = {
            "name": self.name,
            "device_type": None,
            "device_ref": None,
            "ports": {}
        }

    def set_ports(self, portlist):
        self.data["ports"] = {port: None for port in portlist}

    def set_device_type(self, devicetype):
        self.data["device_type"] = devicetype

    def set_device_ref(self, deviceref):
        self.data["device_ref"] = deviceref

    def set_name(self, name):
        self.name = name
        self.data["name"] = self.name

    def save_json(self):
        if self.name is not None:
            with open(Path("data/configs").joinpath(self.name+".json"), "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
            #try:
            #    self.ui.L_success.setText("SUCCESS")
            #except Exception as e:
            #   print(e)
        else:
            log("warning", "config not saved, no name was set.")


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
    fh = logging.handlers.RotatingFileHandler(filename=Path("logs/Network_comissioning.log"),
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

"""
Writer
"""
class Writer:
    def __init__(self,port_com):
        self._ser = serial.Serial(timeout=1)
        self._ser.baudrate = 9600
        self._ser.port = port_com
        self._ser.open()
        log("info","serial opened")
        self.initialised = 0
        while not self.initialised:
            line = self._ser.readline().decode("utf-8").lower().replace('\r\n',"")
            self._ser.write(b'\n')
            log("info", "console output: ", line)
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
            
    def print_line(self):
        print(self._ser.readline())
        
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
    LOGGER=init_logger()
    ct = CommissionningTool("data/ui/commissioning_tool.ui")
