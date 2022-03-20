import json
import sys
import logging
import logging.handlers
import ipaddress
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5 import uic


"""
Logger
"""

def init_logger():
    """
    creates logger object. The logger has 2 handlers: One handler
    for showing logs in terminal and one handler for saving logs
    in file.
    """
    global LOGGER
    LOGGER = logging.getLogger('Network_creation_tool')
    LOGGER.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(formatter)
    LOGGER.addHandler(sh)
    fh = logging.handlers.RotatingFileHandler(filename=Path("logs/Network_creation.log"),
                                              maxBytes=1048576, backupCount=5, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    LOGGER.addHandler(fh)


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
TODO
UI part
"""


class CreationTool:
    def __init__(self, uifile):
        self.app = QApplication(sys.argv)
        Ui, Window = uic.loadUiType(uifile)
        self.window = Window()
        self.ui = Ui()
        self.ui.setupUi(self.window)
        self.init_ui()
        self.window.show()
        self.app.exec_()

    def init_ui(self):
        self.ui.B_CreateNetwork.clicked.connect(self.create_network)

    def create_network (self):
        Network(self.ui.LE_Ipaddr.text())


"""
TODO
Network creation tool
"""


class Network:
    """
    Base class for a network
    """

    def __new__(cls, *args, **kwargs):
        try:
            ipaddress.ip_network(args[0])
        except ValueError:
            print("not ip network format, network not created")
            return None
        else:
            return super().__new__(cls)

    def __init__(self, ipadd, name=None):
        """
        Creates new network. if no name is passed as parameter, the network
        name will be the ip address.
        :param ipadd:
        :param name:
        """
        self.ip = ipaddress.ip_network(ipadd)
        self.name = name if name is not None else str(self.ip)
        self.subnets = {}
        self.devices = {}
        self.vlans={}
        log("info", "network created, ip address:", str(self.ip))

    def create_subnet(self, ipadd):
        """
        Create subnet with ipadd and returns the subnet created if the
        ipadd parameter is valid
        :param ipadd:
        :return:
        """
        if ipadd not in self.subnets.keys:
            subnet = Network(ipadd)
            if subnet is not None:
                self.subnets[ipadd] = subnet
                return subnet

    def create_vlan(self, nb_devices):
        pass

    def get_info(self):
        """
        create info dictionnary of the network and its subnetworks.
        :return:
        """
        info={
            "Subnetworks": {},
            "Devices": {},
            "Vlans":{},
            "Number of hosts": None
        }
        for subip, subnet in self.subnets.items():
            info["Subnetworks"][subip] = subnet.get_info()
        for devicename, device in self.devices.items():
            info["Devices"][devicename] = device.get_info()
        for vlanname, vlan in self.vlans.items():
            info["Vlans"][vlanname] = vlan.get_info()
        return info

    def create_excel(self):
        pass

    def create_json(self):
        """
        calls the get_info method of the network and creates a json with
        all the network information
        :return:
        """
        json_info = self.get_info()
        with open(self.name+".json", "w") as f:
            json.dump(json_info, f)


class Vlan:
    def __new__(cls, *args, **kwargs):
        try:
            ipaddress.ip_network(args[1])
        except ValueError:
            print("not ip network format, vlan not created")
            return None
        else:
            return super().__new__(cls)

    def __init__(self, name, ipaddr):
        self.name = name
        self.ip= ipaddr

    def get_info(self):
        info = {}
        pass


class NetworkDevice:
    _counter = 0

    def __init__(self):
        self._ID = self._counter
        NetworkDevice._counter += 1


class Switch(NetworkDevice):
    def __init__(self):
        super().__init__()
        pass

init_logger()
if __name__ == "__main__":
    pass
    #CreationTool(Path("data/ui/creation_tool.ui"))