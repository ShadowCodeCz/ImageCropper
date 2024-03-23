import json
import os
import ctypes
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import *

# import app_core
import qdarktheme
import datetime

from . import core
from . import gui


class ApplicationCLI:
    @staticmethod
    def run(arguments):
        cfg = core.container.cfg
        cfg.from_json(arguments.configuration)
        app = Application()
        app.run()


class Application:
    def __init__(self, logger=core.container.logger()):
        self.app = None
        self.logger = logger
        self.window = None
        self.arguments = None
        self.model = core.container.model()
        self.a = None

    def run(self):
        self.app = QApplication([])

        screen = self.app.primaryScreen()
        size = screen.size()

        self.model.screen_width = size.width()
        self.model.screen_height = size.height()
        print(f"{self.model.screen_width}x{self.model.screen_height}")

        qdarktheme.setup_theme(corner_shape="sharp")
        self.window = gui.MainWindow()
        self.window.setWindowTitle(f"Image cropper")
        self.set_logo()

        self.window.show()
        self.app.exec()

    def set_logo(self):
        my_app_id = f'shadowcode.{core.container.app_description().name}.0.1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)
        path = os.path.join(core.container.package_paths().image_directory(), 'logo.png')
        self.window.setWindowIcon(QIcon(path))
        self.app.setWindowIcon(QIcon(path))



