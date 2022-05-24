import logging
import logging.handlers
from PyQt5.QtGui import QColor
from pathlib import Path

class Logger:
    logger = None

    def __new__(cls, *args, **kwargs):
        if cls.logger is None:
            return super().__new__(cls)

    def __init__(self, name="logs"):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(formatter)
        self._logger.addHandler(sh)
        fh = logging.handlers.RotatingFileHandler(filename=Path("logs").joinpath(f"{name}.log"),
                                                  maxBytes=1048576, backupCount=5, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        self._logger.addHandler(fh)
        self.init_logger(self)

    @classmethod
    def init_logger(cls, logger):
        cls.logger = logger

    def log(self, logtype: str, *texts):
        text = " ".join(texts)
        if logtype.lower() == "info":
            self._logger.info(text)
        elif logtype.lower() == "warning":
            self._logger.warning(text)
        elif logtype.lower() == "error":
            self._logger.error(text)
        else:
            self._logger.warning("message type incorrect. Message: " + text)

    def set_logviewer(self, widget):
        self._logger.addHandler(LogViewer(widget))


class LogViewer(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.widget.setReadOnly(True)
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
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


def get_logger():
    return Logger.logger


def log(logtype, *texts):
    Logger.logger.log(logtype, *texts)


def init_logger(name="logs"):
    if Logger.logger is None:
        Logger(name)

