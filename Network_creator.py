import sys
import ipaddress
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5 import uic

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
        self.ui.B_CreateNetwork.clicked.connect(self.test)

    def test (self):
        print("test")

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
        self._ID = self._counter
        NetworkDevice._counter += 1


class Switch(NetworkDevice):
    def __init__(self):
        super().__init__()
        pass



def main():
    pass


if __name__ == "__main__":
    CreationTool(Path("data/ui/creation_tool.ui"))