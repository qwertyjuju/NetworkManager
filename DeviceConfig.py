from pathlib import Path
import json
from logger import log

"""
Device Configuration Class
"""


class DeviceConfig:

    def __init__(self):
        self.name = None
        self.data = {
            "name": self.name,
            "device_type": None,
            "device_ref": None,
            "ports": {},
            "vlan": {}
        }

    def init_ports(self, portlist):
        self.data["ports"] = {port: {} for port in portlist}

    def set_port(self, port, port_mode=None, access_vlan=None, allowed_vlans=None, native_vlan=None):
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

    def set_ports(self, portlist, portconfig):
        for port in portlist:
            self.set_port(port, **portconfig)

    def set_device_type(self, devicetype):
        self.data["device_type"] = devicetype

    def set_device_ref(self, deviceref):
        self.data["device_ref"] = deviceref

    def set_name(self, name):
        self.name = name
        self.data["name"] = self.name

    def set_vlan(self, number, name):
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