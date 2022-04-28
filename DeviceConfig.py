import ipaddress
from pathlib import Path
import json
import pickle
from copy import deepcopy
from logger import log
from exceptions import *



"""
Device Configuration Class

"""


class DeviceConfig:
    _device_data = None
    _categories = {
        "name": {
            "type": str,
            "mandatory": 1,
            "default": None
        },
        "device_type": {
            "type": str,
            "mandatory": 1,
            "default": None
        },
        "device_ref": {
            "type": str,
            "mandatory": 1,
            "default": None
        },
        "ports": {
            "type": dict,
            "mandatory": 0,
            "default": {}
        },
        "vlan": {
            "type": dict,
            "mandatory": 0,
            "default": {}
        },
        "rip": {
            "type": dict,
            "mandatory": 0,
            "default": {}
        }
    }

    def __new__(cls):
        if cls._device_data is None:
            log("warning", "no device data loaded. please use init_class() to pass device data info (json format)")
            return None
        else:
            return super().__new__(cls)

    def __init__(self):
        self._data = {categoryname: deepcopy(category["default"]) for categoryname, category in self._categories.items()}
        self.commands = []

    def _init_ports(self):
        """
        initialize port list depending on the device reference
        :return:
        """
        info = self.get_device_type(), self.get_device_ref()
        if info[0] is not None and info[1] is not None:
            self._data["ports"] = {portname: {
                "port_mode": None,
                "access_vlan": None,
                "allowed_vlans": None,
                "native_vlan": None,
                "ip_address": None
            } for portname in self._device_data[info[0]][info[1]]["ports"]}

    def load(self, filename):
        """
        load configuration file. This function will check data in the configuration file.
        :param filename:
        :return:
        """
        file = Path(filename)
        if file.suffix in [".json"]:
            if file.suffix == ".json":
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._data = self.check_data(data)

    def check_data(self, tempdata):
        data = {}
        for categoryname, category in self._categories.items():
            if categoryname in tempdata.keys() and isinstance(category, self._categories[categoryname]["type"]):
                data[categoryname] = tempdata[categoryname]
            else:
                if category["mandatory"]:
                    raise DataError
        """
        if ("name" or "device_ref" or "device_type") not in tempdata.keys():
            raise DataError
        for categoryname, content in tempdata.items():
            # noinspection PyTypeHints
            if categoryname in self._categories.keys() and isinstance(content, self._categories[categoryname]["type"]):
                data[categoryname] = content
            else:
                log("warning", f"{categoryname} category not recognised.")
        """
        return data

    def create_txt(self):
        pass

    def set_vlan(self, number, name=None, ipadd=None):
        """
        set a vlan with name, ip adress
        :param number:
        :param name:
        :return:
        """
        try:
            number = int(number)
        except ValueError:
            log("error", "vlan number not integer, vlan not created")
            return None
        else:
            if number in self._data["vlan"].keys():
                log("warning", "vlan number already exists. Please delete existing one before creating new one.")
                return None
            else:
                self._data["vlan"][number] = {
                    "name": name,
                    "ip_address": ipadd
                }
                return number, name, ipadd

    def del_vlan(self, number):
        del self._data["vlan"][number]

    def set_port(self, port, port_mode=None, access_vlan=None, allowed_vlans=None, native_vlan=None, ipadd=None):
        """
        Checks the different parameters for port configuration and sets them.
        :param port:
        :param port_mode:
        :param access_vlan:
        :param allowed_vlans:
        :param native_vlan:
        :param ipadd:
        :return:
        """
        if access_vlan:
            try:
                int(access_vlan)
            except ValueError:
                log("warning", f"vlan access value is not int. access vlan for port {port} not set. ")
                access_vlan = None
        if allowed_vlans:
            if native_vlan is None or "":
                log("warning", "no native vlan set.")
                native_vlan = None
        if ipadd:
            try:
                ipaddress.IPv4Address(ipadd)
            except ValueError:
                log("warning", f"ip address: {str(ipadd)} not set. Ip address not valid")
                ipadd = None
        self._data["ports"][port] = {
            "port_mode": port_mode,
            "access_vlan": access_vlan,
            "allowed_vlans": allowed_vlans,
            "native_vlan": native_vlan,
            "ip_address": ipadd
        }

    def set_ports(self, portlist, portconfig):
        for port in portlist:
            self.set_port(port, **portconfig)

    def get_device_type(self):
        """
        device type property
        :return:
        """
        return self._data["device_type"]

    def set_device_type(self, devicetype):
        """
        device type setter. if devicetype is not in the device data dictionnary, a ValueError Exception will be raised
        :param devicetype:
        :return:
        """
        if (isinstance(devicetype, str) and devicetype in self._device_data.keys()) or devicetype is None:
            if self._data["device_type"] == devicetype:
                pass
            else:
                self._data["device_type"] = devicetype
                self.set_device_ref(None)
        else:
            raise ValueError

    def get_device_ref(self):
        """
        device ref property
        :return:
        """
        return self._data["device_ref"]

    def set_device_ref(self, deviceref):
        """
        device ref setter. If deviceref is not in the device data dictionary for the actual device type, a ValueError Exception
        will be raised
        :param deviceref:
        :return:
        """
        if (isinstance(deviceref, str) and deviceref in self._device_data[self._data["device_type"]].keys()) or deviceref is None:
            self._data["device_ref"] = deviceref
            self._init_ports()
        else:
            log("error", f"device reference value not recognised, deviceref value: {deviceref}")
            raise ValueError

    def get_name(self):
        """
        name property
        :return:
        """
        return self._data["name"]

    def set_name(self, device_name):
        """
        name setter
        :param device_name:
        :return:
        """
        if isinstance(device_name, str) or device_name is None:
            self._data["name"] = device_name
        else:
            raise ValueError

    def get_portsname(self):
        return self._data["ports"].keys()

    def set_rip(self, enable, version=1, no_auto_summary=1):
        if enable:
            self._data["rip"] = {
                "version": version,
                "auto-summary": no_auto_summary,
                "networks": []
            }
        else:
            self._data["rip"] = {}

    def add_rip_network(self, ipadd):
        try:
            ipaddress.IPv4Address(ipadd)
        except ValueError:
            log("error", "IPadress not in ip format.")
            return None
        else:
            if self._data["rip"]:
                if ipadd not in self._data["rip"]["networks"]:
                    self._data["rip"]["networks"] = ipadd
                    return ipadd
                else:
                    log("warning", "network address already in list")
                    return None
            else:
                log("error", "RIP is not enabled")
                return None

    def get_json(self):
        """
        returns data in json format
        :return:
        """
        return json.dumps(self._data, indent=4)

    def create_commands(self):
        commands = [
            "enable",
            "configure terminal"
        ]
        #
        if self._data["name"]:
            commands.extend(f"hostname {self._data['name']}")
        # vlan commands creation
        for vlannb, vlan in self._data["vlan"].items():
            temp = f'vlan {vlannb}|name {vlan["name"]}|exit'.split("|")
            if "ip_address" in vlan.keys():
                temp.extend(f'interface vlan {vlannb}|ip address {vlan["ip_address"]}|exit'.split("|"))
            commands.extend(temp)
        # port commands creation
        for portname, port in self._data["ports"].items():
            if port["port_mode"]:
                if port["port_mode"].lower() == "access":
                    commands.extend(f'interface {portname}|switchport mode access|switchport access vlan {port["access_vlan"]}'.split("|"))
                if port["port_mode"].lower() == "trunk":
                    commands.extend(f'interface {portname}|switchport mode trunk|switchport trunk allowed vlan {port["allowed_vlans"]}|switchport trunk native {port["native_vlan"]}'.split("|"))
                commands.extend("exit")
        self.commands = commands

    def save_all(self):
        if self._data["name"]:
            directory = Path(f"{self._data['name']}")
            if not directory.exists():
                directory.mkdir()
            self.save_json(directory)
            self.create_commands()
            self.save_cmdl(directory)
        else:
            log("error", "config not saved, no name was set.")

    def save_json(self, directory=None):
        if not directory:
            path = Path(f"{self._data['name']}.json")
        else:
            path = Path(directory).joinpath(f"{self._data['name']}.json")
            print(path)
        if self._data["name"]:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=4)
            log("info", f"config json saved in {path}")
        else:
            log("error", "config not saved, no name was set.")

    def save_cmdl(self, directory=None):
        if not directory:
            path = Path(f"{self._data['name']}.cmdl")
        else:
            path = Path(directory).joinpath(f"{self._data['name']}.cmdl")
        if self._data["name"]:
            if self.commands:
                with open(path, "wb") as f:
                    pickle.dump(self.commands,f)
                    log("info", f"command lines file saved in {path}")
            else:
                log("warning", "cmdl not created, no commands were created. Please call \"create_commands()\" method")
        else:
            log("error", "config not saved, no name was set.")


    @classmethod
    def init_class(cls, file):
        """
        function to call before creation of a device configuration
        :param file:
        :return:
        """
        cls._device_data = {}
        with open(file, 'r', encoding="UTF-8") as f:
            cls._device_data.update(json.load(f))
        for cle in cls._device_data.keys():
            for cle_2, data in cls._device_data[cle].items():
                ports = []
                for port in data["ports"]:
                    ports.extend([port["type"] + str(i) for i in range(port["nb"])])
                data["ports"] = ports
        log("info", 'device data loaded.',
                    f'\n\t switches: {" - ".join(cls._device_data["Switch"].keys())} ;',
                    f'\n\t routeurs: {" - ".join(cls._device_data["Router"].keys())}')

    @classmethod
    def get_device_types(cls):
        return cls._device_data.keys()

    @classmethod
    def get_device_refs(cls, device_type):
        if device_type in cls._device_data.keys():
            return [i for i in cls._device_data[device_type]]

    @classmethod
    def get_device_data(cls):
        return cls._device_data

    @classmethod
    def get_categories(cls):
        return cls._categories