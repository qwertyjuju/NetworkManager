import json
import sys
import logging
import logging.handlers
import ipaddress
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5 import uic
from logger import log
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
Project
"""
class Project:
    def __init__(self, name, supernet=None):
        self.name = name
        self.networks = {}
        self.ip_supernet = ipaddress.IPv4Interface(supernet).network if supernet is not None else None

    def create_network(self, ipadd, name=None):
        network = Network(ipadd, name)
        for net in self.networks.values():
            if network.overlaps(net):
                log("error", f"network not created, {str(network.ip)} overlaps other network {str(net.ip)}")
                return None
        self.networks[network.name] = network
        return network

    def create_json(self):
        json_info = {netname: network.get_info() for netname, network in self.networks.items()}
        with open(f"{self.name}.json","w") as f:
            json.dump(json_info, f, indent=4)
"""
TODO
Network creation tool
"""


class Network:
    """
    Base class for a network
    """
    _counter = 1

    def __new__(cls, *args, **kwargs):
        try:
            ipaddress.IPv4Interface(args[0])
        except ValueError:
            log("error", f"Network creation: not ip network format, network not created, ip address argument: {str(args[0])}")
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
        self.ip = ipaddress.IPv4Interface(ipadd).network
        self.name = name if name is not None else "LAN"+str(Network._counter)
        self.subnets = {}
        self.devices = {}
        self.vlans = {}
        self.nb_vlan = 0
        Network._counter += 1
        log("info", f"network created, ip address: {str(self.ip)}")

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
        info = {
            "Name": self.name,
            "Ip": str(self.ip),
            "Subnetworks": {},
            "Devices": {},
            "Vlans": {},
            "Number of hosts": self.ip.num_addresses,
            "Broadcast": str(self.ip.broadcast_address),
            "range": f"{str(list(self.ip.hosts())[0])} - {str(list(self.ip.hosts())[-1])}"
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

    def overlaps(self, network):
        return self.ip.overlaps(network.ip)


class Vlan:

    def __new__(cls, *args, **kwargs):
        if isinstance(args[0], Network):
            try:
                ipaddress.ip_network(args[1])
            except ValueError:
                log("error", "Vlan creation: not ip network format. vlan not created")
                return None
            else:
                return super().__new__(cls)
        else:
            log("error", "Vlan creation: No Network given as first argument. Vlan not created")
            return None

    def __init__(self, network: Network, ipadd: str, name=None):
        self.network = network
        self.name = name if name is not None else "VLAN"+str(self.network.nb_vlan)
        self.ip = ipaddress.IPv4Interface(ipadd).network
        self.network.nb_vlan += 1

    def get_info(self):
        info = {}
        return info


class NetworkDevice:
    _counter = 0
    device_data = {}

    @classmethod
    def __init_class__(cls):
        with open(Path("data/device_data.json"), "r") as f:
            cls._device_data = json.load(f)

    def __init__(self):
        self._ID = self._counter
        NetworkDevice._counter += 1

NetworkDevice.__init_class__()


class Switch(NetworkDevice):
    _counter = 0

    def __new__(cls, *args, **kwargs):
        if args[0] not in cls.device_data["switches"].keys():
            log("error", "Switch creation failed: type not recognised")
            return None
        else:
            return super().__new__(cls)

    def __init__(self, ref, name="Switch",):
        super().__init__()
        self.config = NetworkDevice.device_data["switches"][ref]
        self.name = name if name != "Switch" else name+str(Switch._counter)
        Switch._counter += 1

    def add_device(self):
        pass


if __name__ == "__main__":
    project = Project("SAE21")
    lan1 = project.create_network("172.16.104.0/23")
    lan2 = project.create_network("172.16.64.0/19")
    lan3 = project.create_network("172.16.0.0/18")
    lan4 = project.create_network("172.16.96.0/21")
    #lan5 = project.create_network("172.16.96.2/21")
    project.create_json()
    #CreationTool(Path("data/ui/creation_tool.ui"))
