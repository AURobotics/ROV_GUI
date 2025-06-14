from __future__ import annotations

from random import randint

from PySide6.QtCore import QTimer
from PySide6.QtGui import Qt, QPixmap, QPainter, QColor, QFont, QPen
from PySide6.QtWidgets import (QWidget,
                               QStackedWidget,
                               QTableWidget,
                               QTableWidgetItem,
                               QSizePolicy,
                               QVBoxLayout,
                               QPushButton, QHeaderView, QHBoxLayout, QCheckBox, QLabel, )

from ROV_CONSOLE.paths import CARP_MAP_PNG, CARP_MAP_REGIONS


class _CheckBoxWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(0)
        self.checkbox = QCheckBox()
        self.layout().addWidget(self.checkbox)
        self.layout().setAlignment(Qt.AlignmentFlag.AlignCenter)


class _InputTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Headers setup
        col_count = 5
        self.setColumnCount(col_count)
        for i in range(col_count):
            self.setHorizontalHeaderItem(i, QTableWidgetItem(f'Region {i + 1}'))

        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        row_count = 10
        self.setRowCount(row_count)
        for i in range(row_count):
            self.setVerticalHeaderItem(i, QTableWidgetItem(f'20{i + 16}'))

        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Cell setup
        for r in range(row_count):
            for c in range(col_count):
                w = _CheckBoxWidget()
                w.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                self.setCellWidget(r, c, w)

    def keyPressEvent(self, event, /):
        if event.key() == Qt.Key.Key_Space:
            for i in self.selectedIndexes():
                w = self.cellWidget(i.row(), i.column())
                if isinstance(w, _CheckBoxWidget):
                    w.checkbox.setChecked(not w.checkbox.isChecked())
        else:
            super().keyPressEvent(event)

    def get_info(self):
        info = []
        for r in range(self.rowCount()):
            year = []
            for c in range(self.columnCount()):
                w = self.cellWidget(r, c)
                if isinstance(w, _CheckBoxWidget):
                    if w.checkbox.isChecked():
                        year.append(c)
            info.append(year)
        return info


class _DisplayWidget(QWidget):
    def __init__(self, parent: InvasiveCarpMissionWindow):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self._image_display = QLabel()
        self._slides: list[QPixmap] = []
        self._return_button = QPushButton('Return and Edit')
        self._return_button.clicked.connect(lambda: [self._stop(), parent.display_page(0)])
        self.layout().addWidget(self._image_display)
        self.layout().addWidget(self._return_button)

        self._slide_show_timer = QTimer()
        self._slide_show_timer.timeout.connect(self._slideshow)
        self._current_slide = 0

    def show_map(self, region_info: list[list[int]]):
        # [ [1, 2], [1, 2, 3], ...]
        self._current_slide = 0
        self._slides = []
        for year, regions in enumerate(region_info):
            self._render_slide(year, regions)

        self._slide_show_timer.start(1000)

    def _slideshow(self):
        slide = self._slides[self._current_slide].scaled(self._image_display.size())
        self._image_display.setPixmap(slide)
        self._current_slide += 1
        self._current_slide = self._current_slide % 10

    def _stop(self):
        self._slide_show_timer.stop()

    def _render_slide(self, year: int, regions: list[int]):
        year += 2016
        overlay_color = QColor(255, randint(50, 100), 50)
        pix = QPixmap(str(CARP_MAP_PNG))
        overlays = [QPixmap(str(path)) for path in [CARP_MAP_REGIONS[r] for r in regions]]
        for overlay in overlays:
            mask = overlay.createMaskFromColor(QColor(0, 0, 0), Qt.MaskMode.MaskOutColor)
            overlay.fill(Qt.GlobalColor.transparent)
            painter = QPainter(overlay)
            painter.setClipRegion(mask)
            painter.setClipping(True)
            painter.fillRect(overlay.rect(), overlay_color)
            painter.end()

        painter = QPainter(pix)
        for overlay in overlays:
            painter.drawPixmap(0, 0, overlay)

        painter.setFont(QFont('Arial', 40))
        painter.setPen(QPen(overlay_color))
        painter.drawText(0, painter.fontMetrics().height(), f'{year}')
        painter.end()
        self._slides.append(pix)


class InvasiveCarpMissionWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowTitle('Invasative Carp Tracking')
        self.setLayout(QVBoxLayout())
        self._pages = QStackedWidget()
        self.layout().addWidget(self._pages)
        self._page1 = QWidget()
        self._page1.setLayout(QVBoxLayout())
        self._page2 = _DisplayWidget(self)
        self._page2.setLayout(QVBoxLayout())
        self._pages.addWidget(self._page1)
        self._pages.addWidget(self._page2)
        self._finish_button = QPushButton('Finish')
        self._finish_button.clicked.connect(lambda: self.display_page(1))
        self._table = _InputTableWidget()
        self._page1.layout().addWidget(self._table)
        self._page1.layout().addWidget(self._finish_button)
        self.resize(self._table.size())
        self.show()

    def display_page(self, index):
        self._pages.setCurrentIndex(index)
        if index == 1:
            self._page2.show_map(self._table.get_info())
