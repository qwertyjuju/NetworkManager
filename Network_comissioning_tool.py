import sys
import time
import logging
import logging.handlers
from pathlib import Path
import serial
import json
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5 import uic
"""
Commissionning Tool UI
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
            LOGGER.addHandler(LogViewer(self.ui.PTE_log))
            self.init_data("data/device_data.json")
            self.init_ui()
            self.window.show()
            self.app.exec()

    def init_ui(self):
        self.ui.L_success.hide()
        # main configuration
        self.ui.LE_device_name.editingFinished.connect(self.update_name)
        self.ui.CB_device_type.currentIndexChanged.connect(self.update_devices)
        self.ui.CB_device_ref.addItems(self.data[self.ui.CB_device_type.currentText()])
        self.ui.CB_device_ref.activated.connect(self.update_ports)
        # port configuration
        self.update_ports()
        # vlan configuration
        self.ui.B_add_vlans.clicked.connect(self.set_vlan)
        self.ui.B_delete_vlans.clicked.connect(self.del_vlan)
        self.ui.B_create_device.clicked.connect(self.deviceconfig.save_json)
        # exit button
        self.ui.B_exit.clicked.connect(self.exit_prog)

    def init_data(self, file):
        with open(file, 'r', encoding="UTF-8") as f:
            self.data.update(json.load(f))
        for cle in self.data.keys():
            for cle_2, data in self.data[cle].items():
                ports = []
                for port in data["ports"]:
                    ports.extend([port["type"] + str(i) for i in range(port["nb"])])
                data["ports"] = ports
        log("info", 'device data loaded.',
                    f'\n\t switches: {" - ".join(self.data["Switch"].keys())} ;',
                    f'\n\t routeurs: {" - ".join(self.data["Router"].keys())}')

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

    def set_vlan(self):
        try:
            self.deviceconfig.set_vlan(self.ui.LE_vlannb.text(), self.ui.LE_name_vlan.text())
        except ValueError:
            pass
        else:
            self.ui.LW_vlans.addItem(self.ui.LE_vlannb.text() + " - " + self.ui.LE_name_vlan.text())

    def del_vlan(self):
        for ele in self.ui.LW_vlans.selectedItems():
            self.ui.LW_vlans.takeItem(self.ui.LW_vlans.row(ele))


class LogViewer(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.widget.setReadOnly(True)
        formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
        self.setFormatter(formatter)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)
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

    def set_ports(self, portlist):
        self.data["ports"] = {port: None for port in portlist}

    def set_device_type(self, devicetype):
        self.data["device_type"] = devicetype

    def set_device_ref(self, deviceref):
        self.data["device_ref"] = deviceref

    def set_name(self, name):
        self.name = name
        self.data["name"] = self.name

    def set_vlan(self, number, name):
        number = int(number)
        if number in self.data["vlan"].keys():
            log("warning","vlan number already exists. Please delete existing one before creating new one.")
            raise ValueError
        else:
            self.data["vlan"][number] = {"name": name}

    def save_json(self):
        if self.name is not None:
            with open(Path("data/configs").joinpath(self.name+".json"), "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
            #try:
            #    self.ui.L_success.setText("SUCCESS")
            #except Exception as e:
            #   print(e)
            log("info", f"config json saved in data/configs/{self.name}.json")
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


LOGGER = init_logger()


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


if __name__ == "__main__":
    ct = CommissionningTool("data/ui/commissioning_tool.ui")
