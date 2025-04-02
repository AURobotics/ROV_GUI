from functools import partial
from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QFont, QKeyEvent, QDropEvent
from PySide6.QtWidgets import (QWidget,
                               QSizePolicy,
                               QAbstractItemView,
                               QHBoxLayout,
                               QPushButton,
                               QLabel,
                               QLineEdit,
                               QStackedLayout,
                               QTreeWidget,
                               QTreeWidgetItem, )

from ROV_CONSOLE.constants import TASKS_ICONS_PATH as ASSETS


class TaskWidget(QWidget):
    def __init__(self, content: str, status_callback, done=False):
        super().__init__()
        self._content = content
        self._status = done
        self._emit_status_change = status_callback

        self._layout = QStackedLayout(self)

        self._display = QWidget()
        normal = QHBoxLayout(self._display)

        self._layout.addWidget(self._display)

        self._label = QLabel(self._content)
        self._label.setFont(QFont('Arial', 14))
        self._label.setStyleSheet("QLabel { background-color : none; }")
        self._label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        normal.addWidget(self._label)

        self._done_button = QPushButton(QIcon(str(ASSETS / 'checkmark.svg')), '')
        self._done_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        self._done_button.clicked.connect(self._mark_done)
        normal.addWidget(self._done_button)

        self._restore_button = QPushButton(QIcon(str(ASSETS / 'revert.svg')), '')
        self._restore_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        self._restore_button.clicked.connect(self._mark_pending)
        normal.addWidget(self._restore_button)

        self._edit_button = QPushButton(QIcon(str(ASSETS / 'edit.svg')), '')
        self._edit_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        self._edit_button.clicked.connect(self.edit)
        normal.addWidget(self._edit_button)

        self._done_button.setVisible(False)
        self._edit_button.setVisible(False)
        self._restore_button.setVisible(False)

        self._edit = QWidget()
        edit = QHBoxLayout(self._edit)

        self._layout.addWidget(self._edit)

        self._edit_field = QLineEdit()
        self._edit_field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self._edit_field.setFont(QFont('Arial', 14))
        self._edit_field.setClearButtonEnabled(True)
        self._edit_field.setReadOnly(True)
        self._edit_field.keyPressEvent = partial(self._esc_detector, self._edit_field)
        self._edit_field.editingFinished.connect(self._close_edit)
        edit.addWidget(self._edit_field)

        self._edit_save_button = QPushButton(QIcon(str(ASSETS / 'checkmark.svg')), '')
        self._edit_save_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        self._edit_save_button.clicked.connect(self._save_edit)
        edit.addWidget(self._edit_save_button)

        self._edit_discard_button = QPushButton(QIcon(str(ASSETS / 'cancel.svg')), '')
        self._edit_discard_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        self._edit_discard_button.clicked.connect(self._close_edit)
        edit.addWidget(self._edit_discard_button)

        self._layout.setCurrentWidget(self._display)
        if done:
            self.mark_done()

    @property
    def metadata(self):
        return {'content': self._content, 'status': self._status}

    def enterEvent(self, event, /):
        if self._layout.currentWidget() == self._edit:
            return
        self._edit_button.setVisible(True)
        if self._status:
            self._done_button.setVisible(False)
            self._restore_button.setVisible(True)
        else:
            self._done_button.setVisible(True)
            self._restore_button.setVisible(False)

    def leaveEvent(self, event, /):
        self._edit_button.setVisible(False)
        self._done_button.setVisible(False)
        self._restore_button.setVisible(False)

    def edit(self):
        self._edit_field.setReadOnly(False)
        self._edit_field.setText(self._content)
        self._layout.setCurrentWidget(self._edit)
        self._edit_field.setFocus()

    def mark_done(self):
        self._label.setText(f'✅ {self._content}')
        self._label.setStyleSheet('QLabel { color : gray; }')
        self._layout.setCurrentWidget(self._display)
        self._status = True

    def mark_pending(self):
        self._label.setText(self._content)
        self._label.setStyleSheet('')
        self._layout.setCurrentWidget(self._display)
        self._status = False

    def _mark_done(self):
        self._restore_button.setVisible(True)
        self._done_button.setVisible(False)
        self.mark_done()
        self._emit_status_change(True)

    def _mark_pending(self):
        self._restore_button.setVisible(False)
        self._done_button.setVisible(True)
        self.mark_pending()
        self._emit_status_change(False)

    def _save_edit(self):
        self._content = self._edit_field.text()
        self._close_edit()

    def _close_edit(self):
        self._edit_field.setReadOnly(True)
        self._mark_pending()

    def _esc_detector(self, _le: QLineEdit, event: QKeyEvent, /):
        if event.key() == Qt.Key.Key_Escape:
            _le.clearFocus()
            self._close_edit()
        elif event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
            self._save_edit()
        else:
            QLineEdit.keyPressEvent(_le, event)


class TaskHeaderLayout(QHBoxLayout):
    def __init__(self, add_task_callback: Callable, trash_callback: Callable, deselect_callback: Callable):
        super().__init__()

        self._label = QLabel('Tasks')
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setFont(QFont('Arial', 16))
        self._label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.addWidget(self._label)

        self._deselect_button = QPushButton(QIcon(str(ASSETS / 'cancel.svg')), '')
        self._deselect_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        self._deselect_button.clicked.connect(deselect_callback)
        self._deselect_button.setVisible(False)
        self._deselect_button.setToolTip('Deselect Current Task')
        self.addWidget(self._deselect_button)

        self._trash_button = QPushButton(QIcon(str(ASSETS / 'trash.svg')), '')
        self._trash_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        self._trash_button.clicked.connect(trash_callback)
        self._trash_button.setVisible(False)
        self._trash_button.setToolTip('Delete Task (Deletes Children)')
        self.addWidget(self._trash_button)

        self._add_task_button = QPushButton(QIcon(str(ASSETS / 'add.svg')), '')
        self._add_task_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        self._add_task_button.clicked.connect(add_task_callback)
        self._add_task_button.setToolTip('Add New Task')
        self.addWidget(self._add_task_button)

    def show_selection_buttons(self, onoff):
        self._deselect_button.setVisible(onoff)
        self._trash_button.setVisible(onoff)
        if onoff is True:
            self._add_task_button.setToolTip('Add New Task Under Selection')
        else:
            if onoff is True:
                self._add_task_button.setToolTip('Add New Task')

    def set_label_text(self, text: str):
        self._label.setText(text)


class TaskViewWidget(QTreeWidget):

    def __init__(self, parent: QWidget, tasks: Optional[list[str | dict]]):
        super().__init__(parent)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)

        self.itemSelectionChanged.connect(self._on_selection_change)

        self.setHeaderLabel('')
        self._header = TaskHeaderLayout(self._new_task, self._del_task, self.clearSelection)
        self.header().setLayout(self._header)
        self.header().setFixedHeight(self._header.sizeHint().height())

        self._populate_from_list(tasks)
        self._num_tasks_total = 0
        self._num_tasks_done = 0
        self._update_header_counter()

        self.expandAll()

    def _populate_from_list(self, tasks: Optional[list[str | dict | tuple]] = None,
                            level: Optional[QTreeWidgetItem] = None):

        if level is None:
            level = self.invisibleRootItem()
        if tasks is not None:
            for t in tasks:
                mark_done = False
                if isinstance(t, tuple):
                    t, mark_done = t  # add more validation here
                if not (isinstance(t, str) or isinstance(t, dict)):
                    continue
                item = QTreeWidgetItem()
                level.addChild(item)
                if isinstance(t, dict):
                    task_name = t['name']
                else:
                    task_name = t
                widget = TaskWidget(task_name, partial(self._status_callback, item), mark_done)
                item.setSizeHint(0, widget.sizeHint())
                self.setItemWidget(item, 0, widget)
                if isinstance(t, dict):
                    if 'tasks' in t:
                        self._populate_from_list(t['tasks'], item)

    def _count_tasks(self, level: Optional[QTreeWidgetItem] = None):
        if level is None:
            level = self.invisibleRootItem()
            self._num_tasks_done = 0
            self._num_tasks_total = 0
        if level.childCount():
            self._num_tasks_total += level.childCount()
            for i in range(level.childCount()):
                item = level.child(i)
                widget = self.itemWidget(item, 0)
                if widget is not None:
                    if isinstance(widget, TaskWidget):
                        if widget.metadata['status']:
                            if item.childCount() == 0:
                                self._num_tasks_done += 1
                if item.childCount():
                    widget.setStyleSheet('QWidget { font-weight: bold; color: lightgrey; }')
                    self._num_tasks_total -= 1
                    self._count_tasks(item)
                else:
                    widget.setStyleSheet('')
        else:
            self._num_tasks_total += 1

    def _notify_parent(self, item: QTreeWidgetItem):
        parent = item.parent()
        if parent is None or parent == self.invisibleRootItem():
            return
        child_count = parent.childCount()
        done_child_count = 0
        for i in range(child_count):
            child = parent.child(i)
            widget = self.itemWidget(child, 0)
            if widget is not None:
                if isinstance(widget, TaskWidget):
                    if widget.metadata['status']:
                        done_child_count += 1
        widget = self.itemWidget(parent, 0)
        if widget is not None:
            if isinstance(widget, TaskWidget):
                if child_count == done_child_count:
                    widget.mark_done()
                else:
                    widget.mark_pending()
        if parent.parent() is not None and parent.parent() != self.invisibleRootItem():
            self._notify_parent(parent)

    def _set_children_status(self, item: QTreeWidgetItem, status):
        child_count = item.childCount()
        for i in range(child_count):
            child = item.child(i)
            widget = self.itemWidget(child, 0)
            if widget is not None:
                if isinstance(widget, TaskWidget):
                    if status:
                        widget.mark_done()
                    else:
                        widget.mark_pending()
            if child.childCount():
                self._set_children_status(child, status)

    def _status_callback(self, item, status):
        self._set_children_status(item, status)
        self._notify_parent(item)
        self._update_header_counter()

    def _find_the_widgetless_level(self, level: Optional[QTreeWidgetItem] = None):
        if level is None:
            level = self.invisibleRootItem()
        for i in range(level.childCount()):
            item = level.child(i)
            widget = self.itemWidget(item, 0)
            if widget is None:
                return item
            if item.childCount():
                item_at_child = self._find_the_widgetless_level(item)
                if item_at_child is not None:
                    return item_at_child

    def _get_embedded_tree(self, item: QTreeWidgetItem):
        tree = []
        if item.childCount():
            for i in range(item.childCount()):
                citem = item.child(i)
                widget = self.itemWidget(citem, 0)
                if isinstance(widget, TaskWidget):
                    meta = widget.metadata.copy()
                    subtree = self._get_embedded_tree(citem)
                    tree.append(({'name': meta['content'], 'tasks': subtree}, meta['status']))
        return tree

    def dropEvent(self, event: QDropEvent):
        item_expansion = self.selectedItems()[0].isExpanded()
        selected_widget = self.itemWidget(self.selectedItems()[0], 0)
        if isinstance(selected_widget, TaskWidget):
            metadata = selected_widget.metadata.copy()
            children = self._get_embedded_tree(self.selectedItems()[0])
            super().dropEvent(event)
            new_item = self._find_the_widgetless_level()
            new_widget = TaskWidget(metadata['content'], partial(self._status_callback, new_item), metadata['status'])
            self.setItemWidget(new_item, 0, new_widget)
            new_item.takeChildren()
            self._populate_from_list(children, new_item)
            self._notify_parent(new_item)
            if new_item.parent():
                new_item.parent().setExpanded(True)
            self.clearSelection()
            new_item.setSelected(True)
            new_item.setExpanded(item_expansion)
            self._update_header_counter()

    def _new_task(self):
        level = self.invisibleRootItem()
        if len(self.selectedItems()) > 0:
            level = self.selectedItems()[0]
        item = QTreeWidgetItem()
        widget = TaskWidget('New Task', partial(self._status_callback, item))
        item.setSizeHint(0, widget.sizeHint())
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemNeverHasChildren)
        level.insertChild(0, item)
        self.setItemWidget(item, 0, widget)
        level.setExpanded(True)
        self.clearSelection()
        item.setSelected(True)
        self._notify_parent(item)
        self._update_header_counter()

    def _on_selection_change(self):
        self._header.show_selection_buttons(len(self.selectedItems()) > 0)

    def _update_header_counter(self):
        self._count_tasks()
        self._header.set_label_text(f'Tasks {self._num_tasks_done}/{self._num_tasks_total}')

    def _del_task(self):
        item = (self.selectedItems()[0])
        parent = item.parent()
        if parent is None:
            parent = self.invisibleRootItem()
        parent.takeChild(parent.indexOfChild(item))
        self.clearSelection()
        self._update_header_counter()
