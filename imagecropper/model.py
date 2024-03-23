import os
import datetime

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtCore import QMetaType

from . import core

# def register_qt_type(cls):
#     """Dekorátor pro registraci tříd Pythonu pro použití v PyQt signálech."""
#     QMetaType.registerType(cls)
#     return cls
#
# @register_qt_type


class DataModel(QObject):
    crop_rect_changed = pyqtSignal()
    pixmap_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.width = core.container.cfg.width()
        self.height = core.container.cfg.height()
        self.scale = 1
        self.path = "./homer.png"
        self.frame_width = int(core.container.cfg.frame_width())
        self.frame_color = core.container.cfg.frame_color()


    def crop_frame_color(self):
        return self.frame_color


    def crop_frame_width(self):
        return self.frame_width

    def image_path(self):
        return self.path

    def new_cropped_file_path(self, rect):
        return self.modify_filename(self.image_path(), rect)

    def crop_rect_width(self):
        return int(self.scale * self.width)

    def crop_rect_height(self):
        return int(self.scale * self.height)

    def crop_scale(self):
        return self.scale

    def new_width(self, value):
        self.width = int(value)
        self.crop_rect_changed.emit()

    def new_height(self, value):
        self.height = int(value)
        self.crop_rect_changed.emit()

    def new_scale(self, value):
        self.scale = float(value)
        self.crop_rect_changed.emit()

    def new_pixmap_path(self, path):
        self.path = path
        self.pixmap_changed.emit()

    def modify_filename(self, original_path, rect):
        directory, filename = os.path.split(original_path)
        base_name, extension = os.path.splitext(filename)

        now = datetime.datetime.now()
        timestamp = now.strftime("%Y-%m-%dT%H-%M-%S")

        new_filename = f"{base_name}_{timestamp}_{rect.width()}x{rect.height()}{extension}"

        new_file_path = os.path.join(directory, "cropped", new_filename)
        os.makedirs(os.path.dirname(new_file_path), exist_ok=True)

        return new_file_path