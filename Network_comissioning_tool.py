import sys
import time
import logging
import logging.handlers
from pathlib import Path
import serial
import json
from PyQt5.QtWidgets import QApplication, QDialog, QTextEdit,QVBoxLayout
from PyQt5.QtGui import QColor, QIcon
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
            self.window.setWindowIcon(QIcon(str(Path("data").joinpath("logo.png"))))
            self.ui = Ui()
            self.ui.setupUi(self.window)
            LOGGER.addHandler(LogViewer(self.ui.PTE_log))
            self.init_data(Path("data").joinpath("device_data.json"))
            self.init_ui()
            self.window.show()
            self.app.exec()

    def init_ui(self):
        self.ui.L_success.hide()
        # main configuration
        self.ui.LE_device_name.editingFinished.connect(self.update_name)
        self.ui.CB_device_type.currentIndexChanged.connect(self.update_devices)
        self.ui.CB_device_ref.addItems(self.data[self.ui.CB_device_type.currentText()])
        self.deviceconfig.set_device_type(self.ui.CB_device_type.currentText())
        self.deviceconfig.set_device_ref(self.ui.CB_device_ref.currentText())
        self.ui.CB_device_ref.activated.connect(self.update_ports)
        # port configuration
        self.ui.RB_mode_trunk.toggled.connect(self.toggle_portconf)
        self.ui.RB_mode_access.toggled.connect(self.toggle_portconf)
        self.ui.B_applyportconf.clicked.connect(self.set_ports)
        self.update_ports()
        # vlan configuration
        self.ui.B_add_vlans.clicked.connect(self.set_vlan)
        self.ui.B_delete_vlans.clicked.connect(self.del_vlan)
        self.ui.B_create_device.clicked.connect(self.deviceconfig.save_json)
        # exit button
        self.ui.B_preview_json.clicked.connect(self.preview_config)
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
        self.deviceconfig.set_device_ref(self.ui.CB_device_ref.currentText())
        self.update_ports()

    def update_ports(self):
        self.ui.LW_ports.clear()
        self.ui.LW_ports.addItems(self.data[self.ui.CB_device_type.currentText()][self.ui.CB_device_ref.currentText()]["ports"])
        self.deviceconfig.init_ports(self.data[self.ui.CB_device_type.currentText()][self.ui.CB_device_ref.currentText()]["ports"])

    def update_name(self):
        if self.ui.LE_device_name.text() != "":
            self.deviceconfig.set_name(self.ui.LE_device_name.text())

    def toggle_portconf(self):
        if self.ui.RB_mode_access.isChecked():
            self.ui.access_conf_frame.setEnabled(1)
            self.ui.trunk_conf_frame.setEnabled(0)
        if self.ui.RB_mode_trunk.isChecked():
            self.ui.access_conf_frame.setEnabled(0)
            self.ui.trunk_conf_frame.setEnabled(1)

    def set_ports(self):
        config={}
        if self.ui.RB_mode_access.isChecked():
            config["port_mode"] = "Access"
            config["access_vlan"] = self.ui.LE_accessvlan.text()
        elif self.ui.RB_mode_trunk.isChecked():
            config["port_mode"] = "Trunk"
            config["allowed_vlans"] = self.ui.LE_allowedvlans.text()
        self.deviceconfig.set_ports([item.text() for item in self.ui.LW_ports.selectedItems()], config)

    def exit_prog(self):
        sys.exit()

    def preview_config(self):
        dlg = JsonPreviewDialog(self.window, self.deviceconfig.get_json())
        dlg.exec()

    def set_vlan(self):
        try:
            self.deviceconfig.set_vlan(self.ui.LE_vlannb.text(), self.ui.LE_name_vlan.text())
        except ValueError:
            log("error", "vlan number not integer, vlan not created")
        else:
            self.ui.LW_vlans.addItem(self.ui.LE_vlannb.text() + " - " + self.ui.LE_name_vlan.text())

    def del_vlan(self):
        for ele in self.ui.LW_vlans.selectedItems():
            self.ui.LW_vlans.takeItem(self.ui.LW_vlans.row(ele))

class JsonPreviewDialog(QDialog):

    def __init__(self, parent, jsondata):
        super().__init__(parent)
        self.jsondisplay = QTextEdit()
        self.jsondisplay.setText(jsondata)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.jsondisplay)
        self.setLayout(self.layout)


class LogViewer(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.widget.setReadOnly(True)
        formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
        self.setFormatter(formatter)

    def emit(self, record):
        msg = self.format(record)
        if record.levelname == "INFO":
            self.widget.setTextColor(QColor(33, 184, 2))
        elif record.levelname == "WARNING":
            self.widget.setTextColor(QColor(208, 113, 0))
        elif record.levelname == "ERROR":
            self.widget.setTextColor(QColor(221, 0, 0))
        elif record.levelname == "CRITICAL":
            self.widget.setTextColor(QColor(255, 0, 0))
        else:
            self.widget.setTextColor(QColor(0, 0, 0))
        self.widget.append(msg)

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

    def set_port(self, port, port_mode=None, access_vlan=None, allowed_vlans=None):
        self.data["ports"][port] = {
            "port_mode": port_mode,
        }
        if port_mode == "Access":
            if access_vlan is not None:
                try:
                    int(access_vlan)
                except ValueError:
                    log("error", f"vlan access value is not int. access vlan for port {port} not set. ")
                else:
                     self.data["ports"][port]["access_vlan"]=access_vlan
        if port_mode == "Trunk":
            if allowed_vlans is not None:
                    self.data["ports"][port]["allowed_vlans"]=allowed_vlans
            else:
                pass

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
        number = int(number)
        if number in self.data["vlan"].keys():
            log("warning","vlan number already exists. Please delete existing one before creating new one.")
        else:
            self.data["vlan"][number] = {"name": name}

    def get_json(self):
        return json.dumps(self.data, indent=4)

    def save_json(self):
        if self.name is not None:
            with open(Path("data").joinpath("configs", self.name+".json"), "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
            log("info", f"config json saved in data/configs/{self.name}.json")
        else:
            log("error", "config not saved, no name was set.")
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
