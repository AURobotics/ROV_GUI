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
    def __init__(self, content: str | dict, done_callback: Callable):
        super().__init__()
        if isinstance(content, dict):
            self._chosen_layout = content['layout']
            self._content = content['content']
        else:
            self._content = content
            self._chosen_layout = 'normal'

        self._layout = QStackedLayout(self)

        self._layouts = {'normal': QWidget()}
        normal = QHBoxLayout(self._layouts['normal'])

        self._layout.addWidget(self._layouts['normal'])

        self._label = QLabel(self._content)
        self._label.setFont(QFont('Arial', 14))
        self._label.setStyleSheet("QLabel { background-color : none; }")
        self._label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        normal.addWidget(self._label)

        self._done_button = QPushButton(QIcon(str(ASSETS / 'checkmark.svg')), '')
        self._done_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        self._done_callback = done_callback
        self._done_button.clicked.connect(self._done)
        normal.addWidget(self._done_button)

        self._edit_button = QPushButton(QIcon(str(ASSETS / 'edit.svg')), '')
        self._edit_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        self._edit_button.clicked.connect(self.edit)
        normal.addWidget(self._edit_button)

        self._layouts['edit'] = QWidget()
        edit = QHBoxLayout(self._layouts['edit'])

        self._layout.addWidget(self._layouts['edit'])

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

        self._layouts['done'] = QWidget()
        done = QHBoxLayout(self._layouts['done'])
        self._layout.addWidget(self._layouts['done'])

        self._done_label = QLabel(self._content)
        self._done_label.setFont(QFont('Arial', 14))
        self._done_label.setStyleSheet("QLabel { background-color : green; }")
        done.addWidget(self._done_label)

        self._restore_button = QPushButton(QIcon(str(ASSETS / 'revert.svg')), '')
        self._restore_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        self._restore_button.clicked.connect(self._restore)
        done.addWidget(self._restore_button)

        self._layout.setCurrentWidget(self._layouts[self._chosen_layout])

    @property
    def metadata(self):
        return {'content': self._content, 'layout': self._chosen_layout}

    def edit(self):
        self._edit_field.setReadOnly(False)
        self._edit_field.setText(self._content)
        self._layout.setCurrentWidget(self._layouts['edit'])
        self._chosen_layout = 'edit'
        self._edit_field.setFocus()

    def mark_done(self):
        self._done_label.setText(self._content)
        self._layout.setCurrentWidget(self._layouts['done'])
        self._chosen_layout = 'done'

    def _done(self):
        self.mark_done()
        self._done_callback()

    def _restore(self):
        self._label.setText(self._content)
        self._layout.setCurrentWidget(self._layouts['normal'])
        self._chosen_layout = 'normal'
        self._done_callback()

    def _save_edit(self):
        self._content = self._edit_field.text()
        self._close_edit()

    def _close_edit(self):
        if self._edit_field.isReadOnly():
            return
        self._edit_field.setReadOnly(True)
        self._label.setText(self._content)
        self._label.setVisible(True)
        self._layout.setCurrentWidget(self._layouts['normal'])
        self._chosen_layout = 'normal'

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


class TaskViewWidget(QTreeWidget):

    def __init__(self, parent: QWidget, tasks: Optional[list[str | dict]]):
        super().__init__(parent)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)

        self.itemSelectionChanged.connect(self._on_selection_change)

        # self.setRootIsDecorated(False)
        self.setHeaderLabel('')
        self._header = TaskHeaderLayout(self._new_task, self._del_task, self.clearSelection)
        self.header().setLayout(self._header)
        self.header().setFixedHeight(self._header.sizeHint().height())

        self._populate_from_list(tasks)
        self._num_tasks_total = 0
        self._num_tasks_done = 0
        self._update_num_tasks()

        self.expandAll()

    def _populate_from_list(self, tasks: Optional[list[str | dict | tuple]] = None, level: Optional[
        QTreeWidgetItem] = None):
        if level is None:
            level = self.invisibleRootItem()
        if tasks is not None:
            for t in tasks:
                status = 'normal'
                if isinstance(t, tuple):
                    t, status = t  # add more validation here
                if not (isinstance(t, str) or isinstance(t, dict)):
                    continue
                item = QTreeWidgetItem()
                level.addChild(item)
                if isinstance(t, dict):
                    task_name = t['name']
                else:
                    task_name = t
                widget = TaskWidget({'content': task_name, 'layout': status}, self._update_num_tasks)
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
            subtask_done_num = 0
            for i in range(level.childCount()):
                item = level.child(i)
                widget = self.itemWidget(item, 0)
                if widget is not None:
                    if isinstance(widget, TaskWidget):
                        if widget.metadata['layout'] == 'done':
                            self._num_tasks_done += 1
                            subtask_done_num += 1
                if item.childCount():
                    self._num_tasks_total -= 1
                    self._count_tasks(item)
            if subtask_done_num > 0 and subtask_done_num == level.childCount() and level != self.invisibleRootItem():
                self.itemWidget(level, 0).mark_done()
        else:
            self._num_tasks_total += 1

    def _find_the_widgetless(self, level: QTreeWidgetItem):
        for i in range(level.childCount()):
            item = level.child(i)
            widget = self.itemWidget(item, 0)
            if widget is None:
                return item
            if item.childCount():
                item_at_child = self._find_the_widgetless(item)
                if item_at_child is not None:
                    return item_at_child

    def _get_embedded_tree(self, item: QTreeWidgetItem):
        tree = []
        if item.childCount():
            for i in range(item.childCount()):
                citem = item.child(i)
                widget: TaskWidget = self.itemWidget(citem, 0)
                if isinstance(widget, TaskWidget):
                    meta = widget.metadata.copy()
                    subtree = self._get_embedded_tree(citem)
                    tree.append(({'name': meta['content'], 'tasks': subtree}, meta['layout']))
        return tree

    def dropEvent(self, event: QDropEvent):
        selected_widget = self.itemWidget(self.selectedItems()[0], 0)
        if isinstance(selected_widget, TaskWidget):
            metadata = selected_widget.metadata.copy()
            children = self._get_embedded_tree(self.selectedItems()[0])
            super().dropEvent(event)
            new_item = self._find_the_widgetless(self.invisibleRootItem())
            new_widget = TaskWidget(metadata, self._update_num_tasks)
            self.setItemWidget(new_item, 0, new_widget)
            new_item.takeChildren()
            self._populate_from_list(children, new_item)
            self._update_num_tasks()

    def _new_task(self):
        level = self.invisibleRootItem()
        if len(self.selectedItems()) > 0:
            level = self.selectedItems()[0]
        item = QTreeWidgetItem()
        widget = TaskWidget('New Task', self._count_tasks)
        item.setSizeHint(0, widget.sizeHint())
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemNeverHasChildren)
        level.insertChild(0, item)
        self.setItemWidget(item, 0, widget)
        level.setExpanded(True)
        self.clearSelection()
        item.setSelected(True)
        self._update_num_tasks()

    def _on_selection_change(self):
        self._header.show_selection_buttons(len(self.selectedItems()) > 0)

    def _update_num_tasks(self):
        self._count_tasks()
        self._header._label.setText(f'Tasks {self._num_tasks_done}/{self._num_tasks_total}')

    def _del_task(self):
        item = (self.selectedItems()[0])
        parent = item.parent()
        if parent is None:
            parent = self.invisibleRootItem()
        parent.takeChild(parent.indexOfChild(item))
        self.clearSelection()
        self._update_num_tasks()
