import json
import sys
import math
import ipaddress
from pathlib import Path
from logger import log, init_logger
import openpyxl as xl
from openpyxl.chart import BarChart, Reference


"""
Project
"""
class Project:
    def __init__(self, name, supernet=None):
        self.name = name
        self.networks = {}
        self.ip_supernet = ipaddress.IPv4Interface(supernet).network if supernet is not None else None

    def create_network(self, ipadd, name=None):
        ipadd = ipaddress.IPv4Interface(ipadd).network
        for net in self.networks.values():
            if net.overlaps(ipadd):
                log("error", f"network not created, {str(ipadd)} overlaps already created network {str(net.ip)}")
                return None
        network = Network(ipadd, name)
        self.networks[network.name] = network
        return network

    def get_info(self):
        return {netname: network.get_info() for netname, network in self.networks.items()}

    def save_json(self, directory= None):
        if not directory:
            path = Path(f"{self.name}.json")
        else:
            path = Path(directory).joinpath(f"{self.name}.json")
        with open(path,"w") as f:
            json.dump(self.get_info(), f, indent=4)

    def save_excel(self, directory=None):
        if not directory:
            path = Path(f"{self.name}.xlsx")
        else:
            path = Path(directory).joinpath(f"{self.name}.xlsx")
        data = self.get_info()
        wb = xl.Workbook()
        mainws = wb.active
        mainws.title = "Networks"
        mainws.append(Network.xl_categories)
        for networkname, networkinfo in data.items():
            mainws.append([value for key, value in networkinfo.items() if key in Network.xl_categories])
            netws = wb.create_sheet(networkname)
            netws.append([networkname])
            netws.append(["Vlans"])
            netws.append(Vlan.xl_categories)
            total_nb_hosts = 0
            if networkinfo["Vlans"]:
                for vlanname, vlaninfo in networkinfo["Vlans"].items():
                    total_nb_hosts += vlaninfo["Number of hosts"]
                    netws.append([value for key, value in vlaninfo.items() if key in Vlan.xl_categories])
                values = Reference(netws, min_col=4, min_row=4, max_col=4, max_row=3+len(networkinfo["Vlans"]))
                names = Reference(netws, min_col=1, min_row=4, max_col=1, max_row=3+len(networkinfo["Vlans"]))
                chart = BarChart()
                chart.add_data(values)
                chart.set_categories(names)
                netws.add_chart(chart, "I1")
        values = Reference(mainws, min_col=3, min_row=2, max_col=3, max_row=1 + len(data))
        names = Reference(mainws, min_col=1, min_row=2, max_col=1, max_row=1 + len(data))
        chart = BarChart()
        chart.add_data(values)
        chart.set_categories(names)
        mainws.add_chart(chart, "I1")
        try:
            wb.save(path)
        except PermissionError:
            log("error", "excel file not saved, please close file")

    def save_all(self):
        directory = Path(f"{self.name}")
        if not directory.exists():
            directory.mkdir()
        self.save_json(directory)
        self.save_excel(directory)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

"""
TODO
Network creation tool
"""
class AbstractNetwork:

    _cidr = None

    def __new__(cls, *args, **kwargs):
        try:
            ipaddress.IPv4Interface(args[0])
        except ValueError:
            log("error", f"Network creation: not ip network format, network not created, ip address argument: {str(args[0])}")
            return None
        else:
            return super().__new__(cls)

    def __init__(self, ipadd):
        self.ip = ipaddress.IPv4Interface(ipadd).network
        self._name = None

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @classmethod
    def __init_class__(cls):
        cls._create_cidr_dict()

    @classmethod
    def _create_cidr_dict(cls):
        cls._cidr = {
            1: 2147483646,
            30: 2,
        }
        for i in range(2, 30):
            cls._cidr[i] = math.floor((cls._cidr[1] * ((1 / 2) ** (i - 1))) - 1)

    def overlaps(self, network):
        if isinstance(network, (Network, Vlan)):
            return self.ip.overlaps(network.ip)
        else:
            return self.ip.overlaps(network)




AbstractNetwork.__init_class__()


class Network(AbstractNetwork):
    xl_categories = ["Name", "IP", "Number of hosts", "Broadcast", "Range"]
    """
    Base class for a network
    """
    _counter = 1

    def __init__(self, ipadd, name=None):
        """
        Creates new network. if no name is passed as parameter, the network
        name will be the ip address.
        :param ipadd:
        :param name:
        """
        super().__init__(ipadd)
        self.name = name if name is not None else "LAN"+str(Network._counter)
        self.subnets = {}
        self.devices = {}
        self.vlans = {}
        self.nb_vlan = 1
        Network._counter += 1
        log("info", f"network created, ip address: {str(self.ip)}, name: {self.name}")

    def create_subnet(self, ipadd):
        pass

    def create_vlans(self, vlan_param_list):
        vlan_param_list = sorted(vlan_param_list,key = lambda x: x[0] if isinstance(x,(list,tuple)) else x, reverse=True)
        for params in vlan_param_list:
            if isinstance(params, (list, tuple)):
                self.create_vlan(*params)
            else:
                self.create_vlan(params)

    def create_vlan(self, nb_devices, name=None, number = None):
        cidr = None
        if nb_devices < 2:
            cidr = 30
        else:
            for i in range(30, 0, -1):
                if nb_devices < self._cidr[i]:
                    cidr = i
                    break
        if cidr:
            net = self.find_suitable_net(list(self.ip.subnets(new_prefix=cidr)))
            if net:
                vlan = Vlan(net, self, name, number)
                self.vlans[vlan.name] = vlan
            else:
                log("warning", f"can't create vlan with cidr:/{cidr}, not enough space on network")

    def find_suitable_net(self, netl):
        subnets = [vlan for vlan in self.vlans.values()]
        subnets.extend([subnet for subnet in self.subnets.values()])
        for i in netl:
            if subnets:
                for j in subnets:
                    if j.overlaps(i):
                        break
                else:
                    return i
            else:
                return i
        else:
            return None

    def get_info(self):
        """
        create info dictionnary of the network and its subnetworks.
        :return:
        """
        info = {
            "Name": self.name,
            "IP": str(self.ip),
            "Subnetworks": {},
            "Devices": {},
            "Vlans": {},
            "Number of hosts": self.ip.num_addresses,
            "Broadcast": str(self.ip.broadcast_address),
            "Range": f"{str(list(self.ip.hosts())[0])} - {str(list(self.ip.hosts())[-1])}"
        }
        for subip, subnet in self.subnets.items():
            info["Subnetworks"][subip] = subnet.get_info()
        for devicename, device in self.devices.items():
            info["Devices"][devicename] = device.get_info()
        for vlanname, vlan in self.vlans.items():
            info["Vlans"][vlanname] = vlan.get_info()
        return info

class Vlan (AbstractNetwork):
    xl_categories = ["Name", "number", "IP", "Number of hosts", "Broadcast", "Range"]

    def __init__(self, ipadd, network: Network, name=None, number=None):
        super().__init__(ipadd)
        self.network = network
        self.name = name if name is not None else "VLAN"+str(self.network.nb_vlan)
        if number is not None:
            try:
                self.number = int(number)
            except ValueError:
                log("warning", f"wrong vlan number. Default number used: {self.network.nb_vlan}")
                self.number = self.network.nb_vlan
        else:
            self.number = self.network.nb_vlan
        self.network.nb_vlan += 1
        log("info", f"vlan created, vlan number: {str(self.number)}, ip address: {str(self.ip)}, name: {self.name}")

    def get_info(self):
        info = {
            "Name": self.name,
            "number": self.number,
            "IP": str(self.ip),
            "Number of hosts": self.ip.num_addresses,
            "Broadcast": str(self.ip.broadcast_address),
            "Range": f"{str(list(self.ip.hosts())[0])} - {str(list(self.ip.hosts())[-1])}"
        }
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


init_logger("NetworkCreator")


    #lan5 = project.create_network("172.16.96.2/21")

