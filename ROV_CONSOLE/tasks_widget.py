from functools import partial
from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QFont, QKeyEvent
from PySide6.QtWidgets import (QWidget,
                               QListWidget,
                               QSizePolicy,
                               QListWidgetItem,
                               QAbstractItemView,
                               QHBoxLayout,
                               QPushButton, QLabel, QLineEdit, QStackedLayout, )

from ROV_CONSOLE.constants import TASKS_ICONS_PATH as ASSETS


class Task(QWidget):
    def __init__(self, text: str, trash_callback: Callable):
        super().__init__()
        self._content = text

        self._layout = QStackedLayout(self)

        self._normal = QWidget()
        normal = QHBoxLayout(self._normal)

        self._layout.addWidget(self._normal)

        self._label = QLabel(self._content)
        self._label.setFont(QFont('Arial', 16))
        self._label.setStyleSheet("QLabel { background-color : none; }")
        self._label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        normal.addWidget(self._label)

        self._done_button = QPushButton(QIcon(str(ASSETS / 'checkmark.svg')), '')
        self._done_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        self._done_button.clicked.connect(self._mark_done)
        normal.addWidget(self._done_button)

        self._edit_button = QPushButton(QIcon(str(ASSETS / 'edit.svg')), '')
        self._edit_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        self._edit_button.clicked.connect(self.edit)
        normal.addWidget(self._edit_button)

        self._trash_button = QPushButton(QIcon(str(ASSETS / 'trash.svg')), '')
        self._trash_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        self._trash_button.clicked.connect(trash_callback)
        normal.addWidget(self._trash_button)

        self._edit = QWidget()
        edit = QHBoxLayout(self._edit)

        self._layout.addWidget(self._edit)

        self._edit_field = QLineEdit()
        self._edit_field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self._edit_field.setFont(QFont('Arial', 16))
        self._edit_field.setClearButtonEnabled(True)
        self._edit_field.setReadOnly(True)
        self._edit_field.keyPressEvent = partial(self._esc_detector, self._edit_field)
        self._edit_field.editingFinished.connect(self._discard_edit)
        edit.addWidget(self._edit_field)

        self._edit_discard_button = QPushButton(QIcon(str(ASSETS / 'cancel.svg')), '')
        self._edit_discard_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        self._edit_discard_button.clicked.connect(self._discard_edit)
        edit.addWidget(self._edit_discard_button)

        self._done = QWidget()
        done = QHBoxLayout(self._done)
        self._layout.addWidget(self._done)

        self._done_label = QLabel(self._content)
        self._done_label.setFont(QFont('Arial', 16))
        self._done_label.setStyleSheet("QLabel { background-color : green; }")
        done.addWidget(self._done_label)

        self._restore_button = QPushButton(QIcon(str(ASSETS / 'revert.svg')), '')
        self._restore_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        self._restore_button.clicked.connect(self._restore)
        done.addWidget(self._restore_button)

        self._layout.setCurrentIndex(0)

    def edit(self):
        self._edit_field.setReadOnly(False)
        self._edit_field.setText(self._content)
        self._layout.setCurrentWidget(self._edit)
        self._edit_field.setFocus()

    def _mark_done(self):
        self._done_label.setText(self._content)
        self._layout.setCurrentWidget(self._done)

    def _restore(self):
        self._label.setText(self._content)
        self._layout.setCurrentWidget(self._normal)

    def _save_edit(self):
        self._content = self._edit_field.text()
        self._edit_field.setReadOnly(True)
        self._label.setText(self._content)
        self._layout.setCurrentWidget(self._normal)

    def _discard_edit(self):
        if self._edit_field.isReadOnly():
            return
        self._edit_field.setReadOnly(True)
        self._label.setText(self._content)
        self._label.setVisible(True)
        self._layout.setCurrentWidget(self._normal)

    def _esc_detector(self, _le: QLineEdit, event: QKeyEvent, /):
        if event.key() == Qt.Key.Key_Escape:
            _le.clearFocus()
            self._discard_edit()
        elif event.key() == Qt.Key.Key_Return:
            self._save_edit()
        else:
            QLineEdit.keyPressEvent(_le, event)


class TasksWidget(QListWidget):
    def __init__(self, parent: QWidget, tasks: Optional[list[str]]):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self.itemDoubleClicked.connect(self._edit_task)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setSelectionRectVisible(False)

        if tasks is not None:
            for t in tasks:
                item = QListWidgetItem()
                self.addItem(item)
                task = Task(t, partial(self._del_task, item))
                item.setSizeHint(task.sizeHint())
                self.setItemWidget(item, task)

        add_button = QPushButton('Add Task')
        add_button.setFont(QFont('Arial', 16))
        add_button.clicked.connect(self._new_task)
        self.add_task_item = QListWidgetItem()
        self.add_task_item.setSizeHint(add_button.sizeHint())
        self.addItem(self.add_task_item)
        self.add_task_item.setFlags(
            self.add_task_item.flags() & ~Qt.ItemFlag.ItemIsDragEnabled & ~Qt.ItemFlag.ItemIsSelectable)
        self.setItemWidget(self.add_task_item, add_button)

    def _new_task(self):
        item = QListWidgetItem()
        self.insertItem(self.row(self.add_task_item), item)
        task = Task('New Task', partial(self._del_task, item))
        item.setSizeHint(task.sizeHint())
        self.setItemWidget(item, task)

    def _edit_task(self, item: QListWidgetItem):
        task = self.itemWidget(item)
        if isinstance(task, Task):
            task.edit()

    def _del_task(self, item: QListWidgetItem):
        self.removeItemWidget(item)
        self.takeItem(self.row(item))
        del item
