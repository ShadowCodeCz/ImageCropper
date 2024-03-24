import os
import datetime

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from PIL import ImageQt, Image

from . import core

import io

class DataModel(QObject):
    crop_rect_changed = pyqtSignal()
    pixmap_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.width = core.container.cfg.width()
        self.height = core.container.cfg.height()
        self.scale = float(core.container.cfg.crop_scale())
        self.path = "./homer.png"
        self.path = "./test.JPG"
        self.frame_width = int(core.container.cfg.frame_width())
        self.frame_color = core.container.cfg.frame_color()

        self.screen_width = 800
        self.screen_height = 600

        self.screen_modifier = float(core.container.cfg.screen_modifier())

        self.image_scale = 1
        self.original_pixmap = None
        self.a = None

    def crop_frame_color(self):
        return self.frame_color

    def load_pixmap(self):
        try:
            if self.image_path() is None:
                return QPixmap(800, 500)
            else:
                return self.load_and_correct_image(self.image_path())
                # return QPixmap(self.image_path())
        except Exception as e:
            # self.logger.error(f"Error during opening image {self.model.image_path()}")
            print(e)
            return QPixmap(800, 500)

    def load_and_correct_image(self, image_path):
        image = Image.open(image_path)

        try:
            exif = image._getexif()
            orientation_key = 274
            if exif and orientation_key in exif:
                orientation = exif[orientation_key]

                if orientation == 3:
                    image = image.rotate(180, expand=True)
                elif orientation == 6:
                    image = image.rotate(270, expand=True)
                elif orientation == 8:
                    image = image.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            QPixmap(800, 500)
            # print("error")

        # qt_image = ImageQt.toqpixmap(image)
        return self.convert_pil_to_pixmap(image)

    def convert_pil_to_pixmap(self, pil_image):
        byte_array = io.BytesIO()
        img_format = pil_image.format if pil_image.format else 'PNG'
        pil_image.save(byte_array, format=img_format)

        qimage = QImage()
        qimage.loadFromData(byte_array.getvalue())

        pixmap = QPixmap.fromImage(qimage)

        return pixmap

    def crop_frame_width(self):
        return self.frame_width

    def screen_scaled_pixmap(self):
        self.original_pixmap = self.load_pixmap()

        scale_width = self.usable_screen_width() / self.original_pixmap.width()
        print(f"scale_width = {self.usable_screen_width()} / {self.original_pixmap.width()}")
        scale_height = self.usable_screen_height() / self.original_pixmap.height()
        print(f"scale_height = {self.usable_screen_height()} / {self.original_pixmap.height()}")
        self.image_scale = min(scale_width, scale_height)

        if self.image_scale < 1:
            return self.original_pixmap.scaled(
                self.usable_screen_width(),
                self.usable_screen_height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        else:
            self.image_scale = 1
            return self.original_pixmap

    def usable_screen_width(self):
        return int(self.screen_width * self.screen_modifier)

    def usable_screen_height(self):
        return int(self.screen_height * self.screen_modifier)

    def image_path(self):
        return self.path

    def new_cropped_file_path(self, rect):
        return self.modify_filename(self.image_path(), rect)

    def crop_rect_width(self):
        return int(self.scale * self.width * self.image_scale)

    def crop_rect_height(self):
        return int(self.scale * self.height * self.image_scale)

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

    def save_pixmap(self, pixmap, crop_rect):
        # resized_pixmap = pixmap.scaled(self.model.width, self.model.height, Qt.AspectRatioMode.KeepAspectRatio)
        # resized_pixmap.save(self.model.new_cropped_file_path(QRect(self.crop_rect.x(), self.crop_rect.y(), self.model.width, self.model.height)), "PNG")

        cropped_x = crop_rect.x()
        cropped_y = crop_rect.y()
        cropped_width = crop_rect.width()
        cropped_height = crop_rect.height()

        original_x = cropped_x / self.image_scale
        original_y = cropped_y / self.image_scale
        original_width = cropped_width / self.image_scale
        original_height = cropped_height / self.image_scale

        original_crop_rect = QRect(int(original_x), int(original_y), int(original_width), int(original_height))

        # Qt.AspectRatioMode.IgnoreAspectRatio
        # resized_pixmap = self.original_pixmap.scaled(self.width, self.height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        # resized_pixmap.save(self.new_cropped_file_path(QRect(int(original_crop_rect.x()), int(original_crop_rect.y()), self.width, self.height)), "PNG")

        crop_pixmap = self.original_pixmap.copy(int(original_x), int(original_y), int(original_width), int(original_height))
        scaled_pixmap = crop_pixmap.scaled(self.width, self.height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        tmp_crop_rect = QRect(int(original_crop_rect.x()), int(original_crop_rect.y()), self.width, self.height)
        path = self.new_cropped_file_path(tmp_crop_rect)
        scaled_pixmap.save(path, "PNG")