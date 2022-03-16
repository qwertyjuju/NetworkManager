import ipaddress
import serial


class Network:
    def __init__(self, ipadd, nb_subnets=None):
        self.ip = ipaddress.ip_network(ipadd)
        self.subnets={}
        self.Devices={}

    def create_subnet(self, ipadd, nb_subnets=None):
        pass


class NetworkDevice:
    _counter = 0

    def __init__(self):
        self._ID=self._counter
        NetworkDevice._counter+=1


class Switch(NetworkDevice):
    pass


def main():
    pass