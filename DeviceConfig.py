import ipaddress
from pathlib import Path
import json
from logger import log

"""
Device Configuration Class
"""


class DeviceConfig:
    _device_data = None

    @classmethod
    def init_class(cls, file):
        """
        function to call before creation of a device configuration
        :param file:
        :return:
        """
        cls._device_data={}
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

    def __new__(cls):
        if cls._device_data is None:
            log("warning", "no device data loaded. please use init_class() to pass device data info (json format)")
            return None
        else:
            return super().__new__(cls)

    def __init__(self):
        self.data = {
            "name": None,
            "device_type": None,
            "device_ref": None,
            "ports": {},
            "vlan": {}
        }
        self._name = self.data["name"]
        self._device_type = self.data["device_type"]
        self._device_ref = self.data["device_ref"]

    def _init_ports(self):
        if self.device_type is not None and self.device_ref is not None:
            self.data["ports"] = {portname: {} for portname in self._device_data[self.device_type][self.device_ref]["ports"]}

    def set_port(self, port, port_mode=None, access_vlan=None, allowed_vlans=None, native_vlan=None, ipadd=None):
        if port_mode is not None and port_mode.lower() in ["access", "trunk"]:
            if port_mode.lower() == "access":
                if access_vlan is not None or "":
                    try:
                        int(access_vlan)
                    except ValueError:
                        log("warning", f"vlan access value is not int. access vlan for port {port} not set. ")
                    else:
                        self.data["ports"][port]["port_mode"] = port_mode
                        self.data["ports"][port]["access_vlan"] = access_vlan
            if port_mode.lower() == "trunk":
                if allowed_vlans is not None or "":
                    self.data["ports"][port]["port_mode"] = port_mode
                    self.data["ports"][port]["allowed_vlans"] = allowed_vlans
                    if native_vlan is not None or "":
                        self.data["ports"][port]["native_vlan"] = native_vlan
                    else:
                        log("warning", "no native vlan set.")
        if ipadd:
            try:
                ipaddress.IPv4Address(ipadd)
            except ValueError:
                log("warning", f"ip address: {ipadd} not set. Ip address not valid")
            else:
                self.data["ports"][port]["ip_address"] = ipaddress
        log("info", f"{port} port set with attributes: {self.data['ports'][port]}")

    def set_ports(self, portlist, portconfig):
        for port in portlist:
            self.set_port(port, **portconfig)

    def get_portsname(self):
        return self.data["ports"].keys()

    @property
    def device_type(self):
        """
        device type property
        :return:
        """
        return self._device_type

    @device_type.setter
    def device_type(self, devicetype):
        """
        device type setter. if devicetype is not in the device data dictionnary, a ValueError Exception will be raised
        :param devicetype:
        :return:
        """
        if (isinstance(devicetype, str) and devicetype in self._device_data.keys()) or devicetype is None:
            if self.device_type == devicetype:
                pass
            else:
                self._device_type, self.data["device_type"] = devicetype, devicetype
                self.device_ref = None
        else:
            raise ValueError

    @property
    def device_ref(self):
        """
        device ref property
        :return:
        """
        return self._device_ref

    @device_ref.setter
    def device_ref(self, deviceref):
        """
        device ref setter. If deviceref is not in the device data dictionary for the actual device type, a ValueError Exception
        will be raised
        :param deviceref:
        :return:
        """
        if (isinstance(deviceref, str) and deviceref in self._device_data[self.device_type].keys()) or deviceref is None:
            self._device_ref, self.data["device_ref"] = deviceref, deviceref
            self._init_ports()
        else:
            log("error", f"device reference value not recognised, deviceref value: {deviceref}")
            raise ValueError

    @property
    def name(self):
        """
        name property
        :return:
        """
        return self._name

    @name.setter
    def name(self, device_name):
        """
        name setter
        :param device_name:
        :return:
        """
        if isinstance(device_name, str) or device_name is None:
            self._name = device_name
        else:
            raise ValueError

    def set_vlan(self, number, name):
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
            if number in self.data["vlan"].keys():
                log("warning","vlan number already exists. Please delete existing one before creating new one.")
                return None
            else:
                self.data["vlan"][number] = {"name": name}
                return number, name

    def get_json(self):
        """
        returns data in json format
        :return:
        """
        return json.dumps(self.data, indent=4)

    def create_commands(self):
        commands = [
            "enable",
            "configure terminal"
        ]
        # vlan commands creation
        for vlannb, vlan in self.data["vlan"].items():
            temp = f'vlan {vlannb}|name {vlan["name"]}|exit'.split("|")
            if "ip_address" in vlan.keys():
                temp.extend(f'interface vlan {vlannb}|ip address {vlan["ip_address"]}|exit'.split("|"))
            commands.extend(temp)
        # port commands creation
        for portname, port in self.data["ports"].items():
            try:
                port["port_mode"]
            except KeyError:
                pass
            else:
                if port["port_mode"].lower() == "trunk":
                    commands.extend(f'interface {portname}|switchport mode trunk|switchport trunk allowed vlan {port["allowed_vlans"]}|switchport trunk native {port["native_vlan"]}'.split("|"))
        self.commands = commands

    def save_json(self):
        if self.name is not None:
            with open(Path("data").joinpath("configs", self.name+".json"), "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
            log("info", f"config json saved in data/configs/{self.name}.json")
        else:
            log("error", "config not saved, no name was set.")