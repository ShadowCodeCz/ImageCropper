from PyQt6.QtGui import QDoubleValidator, QFont
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from . import core

import os
import datetime

def clear_layout(layout):
    if layout:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                clear_layout(item.layout())


class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__()
        cfg = core.container.cfg

        self.model = core.container.model()
        self.main_layout = QVBoxLayout(self)

        self.image_cropper = ImageCropper(self)

        panel = ControlPanel(self)
        self.main_layout.addWidget(panel)

        scroll_area = QScrollArea(self)
        scroll_area.setObjectName("ScrollArea")
        scroll_area.setStyleSheet("#ScrollArea {border: 0px solid black}")
        scroll_area.setWidget(self.image_cropper)
        scroll_area.setWidgetResizable(True)

        self.main_layout.addWidget(scroll_area)
        self.setLayout(self.main_layout)
        self.resize(cfg.window.open_width(), cfg.window.open_height())
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        render_cfg = core.container.cfg.render.main_window
        # self.setStyleSheet(f"background-color:{render_cfg.background_color()}")

    def keyPressEvent(self, event):
        modifier = ''
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            modifier += 'Ctrl+'
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            modifier += 'Shift+'
        if event.modifiers() & Qt.KeyboardModifier.AltModifier:
            modifier += 'Alt+'

        # key = event.text().upper()
        # if not key:
        key = Qt.Key(event.key()).name

        joined_key =  f"{modifier}{key}"

        if joined_key == "Ctrl+Key_O":
            self.open_new_image()

        super().keyPressEvent(event)

    def open_new_image(self):
        path = self.open_image_dialog()
        if path and os.path.exists(path):
            self.model.new_pixmap_path(path)

    def open_image_dialog(self):
        filter = "Obrázky (*.png *.jpg *.jpeg *.bmp *.gif)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Vyberte obrázek", "", filter)
        return file_path


class ControlPanel(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = core.container.model()
        self.init_ui()

    def init_ui(self):
        self.custom_layout = QHBoxLayout()

        self.width_label = QLabel("width")
        # self.width_slider = QSlider(Qt.Orientation.Horizontal, self)
        # self.width_slider.setMinimum(0)
        # self.width_slider.setMaximum(2000)
        # self.width_slider.setValue(400)
        # self.width_slider.valueChanged.connect(self.update_width_label)
        self.width_spin = QSpinBox(self)
        self.width_spin.setMinimum(0)
        self.width_spin.setMaximum(2500)
        self.width_spin.setMinimumWidth(250)
        self.width_spin.setValue(self.model.crop_rect_width())
        self.width_spin.valueChanged.connect(self.model.new_width)

        self.height_label = QLabel("height")
        # self.height_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.height_spin = QSpinBox(self)
        self.height_spin.setMinimum(0)
        self.height_spin.setMaximum(2500)
        self.height_spin.setMinimumWidth(250)
        self.height_spin.setValue(self.model.crop_rect_height())
        self.height_spin.valueChanged.connect(self.model.new_height)

        self.scale_coefficient_label = QLabel("scale coefficient")
        # self.scale_coefficient_slider = QSlider(Qt.Orientation.Horizontal, self)

        # self.scale_coefficient_spin = QSpinBox(self)
        # self.scale_coefficient_spin.setMinimum(1)
        # self.scale_coefficient_spin.setMaximum(100)
        # self.scale_coefficient_spin.setMinimumWidth(250)
        # self.scale_coefficient_spin.setValue(self.model.crop_scale())
        # self.scale_coefficient_spin.valueChanged.connect(self.model.new_scale)

        self.scale_coefficient_spin = QDoubleSpinBox(self)
        self.scale_coefficient_spin.setMinimum(1)
        self.scale_coefficient_spin.setMaximum(100.00)
        self.scale_coefficient_spin.setDecimals(2)
        self.scale_coefficient_spin.setSingleStep(0.1)
        self.scale_coefficient_spin.setValue(1)
        self.scale_coefficient_spin.valueChanged.connect(self.model.new_scale)
        self.scale_coefficient_spin.setMinimumWidth(250)

        self.custom_layout.addWidget(self.width_label)
        # self.custom_layout.addWidget(self.width_slider)
        self.custom_layout.addWidget(self.width_spin)
        self.custom_layout.addStretch()

        self.custom_layout.addWidget(self.height_label)
        # self.custom_layout.addWidget(self.height_slider)
        self.custom_layout.addWidget(self.height_spin)
        self.custom_layout.addStretch()

        self.custom_layout.addWidget(self.scale_coefficient_label)
        # self.custom_layout.addWidget(self.scale_coefficient_slider)
        self.custom_layout.addWidget(self.scale_coefficient_spin)

        self.setLayout(self.custom_layout)

    # def update_width_label(self, value):
    #     self.width_label.setText(f"width [{str(value)}]")


class ImageCropper(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = core.container.logger()
        self.model = core.container.model()
        self.model.crop_rect_changed.connect(self.new_crop_rect)
        self.model.pixmap_changed.connect(self.load_pixmap)
        self.crop_rect = QRect(0, 0, self.model.crop_rect_width(), self.model.crop_rect_height())
        self.init_ui()

    def init_ui(self):
        self.load_pixmap()
        self.setMouseTracking(True)

    def load_pixmap(self):
        try:
            if self.model.image_path() is None:
                self.setPixmap(QPixmap(800, 500))
            else:
                print(self.model.image_path())
                self.setPixmap(QPixmap(self.model.image_path()))
        except Exception as e:
            self.logger.error(f"Error during opening image {self.model.image_path()}")
            return QPixmap(800, 500)

    def mouseMoveEvent(self, event):
        self.crop_rect.moveCenter(event.pos())
        self.update()

    def mouseDoubleClickEvent(self, event):
        rect = self.crop_rect.translated(self.pos())
        pixmap = self.pixmap().copy(rect)

        self.save_pixmap(pixmap)
        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.drawPixmap(QPoint(), self.pixmap())
        pen = QPen(QColor(self.model.crop_frame_color()), self.model.crop_frame_width())

        if self.model.crop_scale() == 1:
            pen.setStyle(Qt.PenStyle.SolidLine)
        else:
            pen.setStyle(Qt.PenStyle.DashLine)

        # pen = QPen(QColor(255, 105, 180), 3)
        painter.setPen(pen)

        rect = self.crop_rect.translated(self.pos())
        painter.drawRect(rect)

    def save_pixmap(self, pixmap):
        resized_pixmap = pixmap.scaled(self.model.width, self.model.height, Qt.AspectRatioMode.KeepAspectRatio)

        resized_pixmap.save(self.model.new_cropped_file_path(QRect(self.crop_rect.x(), self.crop_rect.y(), self.model.width, self.model.height)), "PNG")

    def new_crop_rect(self):
        new_width = self.model.crop_rect_width()
        new_height = self.model.crop_rect_height()

        center = self.crop_rect.center()

        new_x = center.x() - new_width // 2
        new_y = center.y() - new_height // 2

        self.crop_rect.setRect(int(new_x), int(new_y), int(new_width), int(new_height))