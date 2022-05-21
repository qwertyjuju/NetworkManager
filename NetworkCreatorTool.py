import sys
from PyQt5.QtWidgets import QApplication, QDialog, QTextEdit,QVBoxLayout
from PyQt5.QtGui import QColor, QIcon
from PyQt5 import uic
from logger import log, get_logger


class ConfigTool:
    def __init__(self, uifile):
            self.app = QApplication(sys.argv)
            Ui, Window = uic.loadUiType(uifile)
            self.window = Window()
            self.ui = Ui()
            self.ui.setupUi(self.window)