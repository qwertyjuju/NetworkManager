import sys
from PyQt5.QtWidgets import QApplication, QDialog, QTextEdit,QVBoxLayout
from PyQt5.QtGui import QColor, QIcon
from PyQt5 import uic
from logger import log, get_logger
import NetworkCreator


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
        self.project = NetworkCreator.Project()
        self.window.show()
        self.app.exec_()

    def init_ui(self):
        self.ui.B_CreateNetwork.clicked.connect()

