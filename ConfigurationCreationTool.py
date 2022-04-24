import sys
from pathlib import Path
import json
from PyQt5.QtWidgets import QApplication, QDialog, QTextEdit,QVBoxLayout
from PyQt5.QtGui import QColor, QIcon
from PyQt5 import uic
from DeviceConfig import DeviceConfig
from logger import log, get_logger

"""
Configuration creation tool
"""


class ConfigTool:
    def __init__(self, uifile):
            self.data = dict()
            self.deviceconfig = DeviceConfig()
            self.app = QApplication(sys.argv)
            Ui, Window = uic.loadUiType(uifile)
            self.window = Window()
            self.window.setWindowIcon(QIcon(str(Path("data").joinpath("logo.png"))))
            self.ui = Ui()
            self.ui.setupUi(self.window)
            get_logger().set_logviewer(self.ui.PTE_log)
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
        # RIP configuration
        self.ui.GB_rip.toggled.connect(self.test)
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

    def set_vlan(self):
        res = self.deviceconfig.set_vlan(self.ui.LE_vlannb.text(), self.ui.LE_name_vlan.text())
        if res is not None:
            self.ui.LW_vlans.addItem(" - ".join(res))

    def set_ports(self):
        config = {}
        if self.ui.RB_mode_access.isChecked():
            config["port_mode"] = "Access"
            config["access_vlan"] = self.ui.LE_accessvlan.text()
        elif self.ui.RB_mode_trunk.isChecked():
            config["port_mode"] = "Trunk"
            config["allowed_vlans"] = self.ui.LE_allowedvlans.text()
            config["native_vlan"] = self.ui.LE_nativevlan.text()
        self.deviceconfig.set_ports([item.text() for item in self.ui.LW_ports.selectedItems()], config)

    def exit_prog(self):
        sys.exit()

    def preview_config(self):
        dlg = JsonPreviewDialog(self.window, self.deviceconfig.get_json())
        dlg.exec()

    def del_vlan(self):
        for ele in self.ui.LW_vlans.selectedItems():
            self.ui.LW_vlans.takeItem(self.ui.LW_vlans.row(ele))

    def test(self):
        print("test")


class JsonPreviewDialog(QDialog):

    def __init__(self, parent, jsondata):
        super().__init__(parent)
        self.jsondisplay = QTextEdit()
        self.jsondisplay.setReadOnly(True)
        self.jsondisplay.setText(jsondata)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.jsondisplay)
        self.setLayout(self.layout)





if __name__ == "__main__":
    ct = ConfigTool("data/ui/commissioning_tool.ui")
