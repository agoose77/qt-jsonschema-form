from collections import Sequence
from functools import partial
from typing import Tuple, Optional

from PyQt5 import QtWidgets, QtCore, QtGui


class Signal:
    def __init__(self):
        self.cache = {}

    def __get__(self, instance, owner):
        if instance is None:
            return self

        try:
            return self.cache[instance]
        except KeyError:
            self.cache[instance] = instance = BoundSignal()
            return instance


class BoundSignal:
    def __init__(self):
        self._subscribers = []

    def __call__(self, *args):
        for sub in self._subscribers:
            sub(*args)

    def connect(self, listener):
        self._subscribers.append(listener)


class WidgetMixin:
    on_changed = Signal()

    VALID_COLOUR = '#ffffff'
    INVALID_COLOUR = '#f6989d'

    def __init__(self, schema: dict, ui_schema: dict, widget_builder: 'WidgetBuilder', **kwargs):
        super().__init__(**kwargs)

        self.schema = schema
        self.ui_schema = ui_schema
        self.widget_builder = widget_builder

        self.on_changed.connect(lambda _: self.clear_error())
        self.configure()

    def configure(self):
        pass

    @property
    def state(self):
        raise NotImplementedError(f"{self.__class__.__name__}.state")

    @state.setter
    def state(self, state):
        raise NotImplementedError(f"{self.__class__.__name__}.state")

    def handle_error(self, path, err):
        if path:
            raise ValueError("Cannot handle nested error by default")
        self._set_valid_state(err)

    def clear_error(self):
        self._set_valid_state(None)

    def _set_valid_state(self, error=None):
        palette = self.palette()
        colour = QtGui.QColor()
        colour.setNamedColor(self.VALID_COLOUR if error is None else self.INVALID_COLOUR)
        palette.setColor(self.backgroundRole(), colour)

        self.setPalette(palette)
        self.setToolTip("" if error is None else error.message)  # TODO


class TextWidget(WidgetMixin, QtWidgets.QLineEdit):

    def configure(self):
        self.textChanged.connect(self.on_changed)

    @property
    def state(self):
        return str(self.text())

    @state.setter
    def state(self, state):
        self.setText(state)


class PasswordWidget(TextWidget):

    def configure(self):
        super().configure()

        self.setEchoMode(self.Password)


class TextAreaWidget(WidgetMixin, QtWidgets.QTextEdit):

    @property
    def state(self):
        return str(self.toPlainText())

    @state.setter
    def state(self, state):
        self.setPlainText(state)

    def configure(self):
        self.textChanged.connect(lambda: self.on_changed(self.state))


class CheckboxWidget(WidgetMixin, QtWidgets.QCheckBox):

    @property
    def state(self):
        return self.isChecked()

    @state.setter
    def state(self, checked):
        self.setChecked(checked)

    def configure(self):
        self.stateChanged.connect(lambda _: self.on_changed(self.state))


class SpinDoubleWidget(WidgetMixin, QtWidgets.QDoubleSpinBox):

    @property
    def state(self):
        return self.value()

    @state.setter
    def state(self, state):
        self.setValue(state)

    def configure(self):
        self.valueChanged.connect(self.on_changed)


class SpinWidget(WidgetMixin, QtWidgets.QSpinBox):

    @property
    def state(self):
        return self.value()

    @state.setter
    def state(self, state):
        self.setValue(state)

    def configure(self):
        self.valueChanged.connect(self.on_changed)


class IntegerRangeWidget(WidgetMixin, QtWidgets.QSlider):

    def __init__(self, schema: dict, ui_schema: dict, widget_builder: 'WidgetBuilder'):
        super().__init__(schema, ui_schema, widget_builder, orientation=QtCore.Qt.Horizontal)

    @property
    def state(self):
        return self.value()

    @state.setter
    def state(self, state):
        self.setValue(state)

    def configure(self):
        self.valueChanged.connect(self.on_changed)

        minimum = 0
        if "minimum" in self.schema:
            minimum = self.schema["minimum"]
            if self.schema.get("exclusiveMinimum"):
                minimum += 1

        maximum = 0
        if "maximum" in self.schema:
            maximum = self.schema["maximum"]
            if self.schema.get("exclusiveMaximum"):
                maximum -= 1

        if "multipleOf" in self.schema:
            self.setTickInterval(self.schema["multipleOf"])
            self.setSingleStep(self.schema["multipleOf"])
            self.setTickPosition(self.TicksBothSides)

        self.setRange(minimum, maximum)


class ObjectWidget(WidgetMixin, QtWidgets.QGroupBox):

    def __init__(self, schema: dict, ui_schema: dict, widget_builder: 'WidgetBuilder'):
        super().__init__(schema, ui_schema, widget_builder)

        self.widgets = self.populate_from_schema(schema, ui_schema, widget_builder)

    @property
    def state(self):
        return {k: w.state for k, w in self.widgets.items()}

    @state.setter
    def state(self, state):
        for name, value in state.items():
            self.widgets[name].state = value

    def handle_error(self, path: Tuple[str], err: Exception):
        name, *tail = path
        self.widgets[name].handle_error(tail, err)

    def widget_on_changed(self, name, value):
        self.state[name] = value
        self.on_changed(self.state)

    def populate_from_schema(self, schema, ui_schema, widget_builder):
        layout = QtWidgets.QFormLayout()
        self.setLayout(layout)
        layout.setAlignment(QtCore.Qt.AlignTop)
        self.setFlat(False)

        if 'title' in schema:
            self.setTitle(schema['title'])

        if 'description' in schema:
            self.setToolTip(schema['description'])

        # Populate rows
        widgets = {}

        for name, sub_schema in schema['properties'].items():
            sub_ui_schema = ui_schema.get(name, {})
            widget = widget_builder.create_widget(sub_schema, sub_ui_schema)  # TODO onchanged
            widget.on_changed.connect(partial(self.widget_on_changed, name))
            label = sub_schema.get("title", name)
            layout.addRow(label, widget)
            widgets[name] = widget

        return widgets


class QColorButton(QtWidgets.QPushButton):
    """Color picker widget QPushButton subclass.

    Implementation derived from https://martinfitzpatrick.name/article/qcolorbutton-a-color-selector-tool-for-pyqt/
    """

    colorChanged = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(QColorButton, self).__init__(*args, **kwargs)

        self._color = None
        self.pressed.connect(self.onColorPicker)

    def color(self):
        return self._color

    def setColor(self, color):
        if color != self._color:
            self._color = color
            self.colorChanged.emit()

        if self._color:
            self.setStyleSheet("background-color: %s;" % self._color)
        else:
            self.setStyleSheet("")

    def onColorPicker(self):
        dlg = QtWidgets.QColorDialog(self)
        if self._color:
            dlg.setCurrentColor(QtGui.QColor(self._color))

        if dlg.exec_():
            self.setColor(dlg.currentColor().name())

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.setColor(None)

        return super(QColorButton, self).mousePressEvent(event)


class ColorWidget(WidgetMixin, QColorButton):
    """Widget representation of a string with the 'color' format keyword."""

    def configure(self):
        self.colorChanged.connect(lambda: self.on_changed(self.state))

    @property
    def state(self) -> str:
        return self.color()

    @state.setter
    def state(self, data: str):
        self.setColor(data)


class FilepathWidget(WidgetMixin, QtWidgets.QWidget):

    def __init__(self, schema: dict, ui_schema: dict, widget_builder: 'WidgetBuilder'):
        super().__init__(schema, ui_schema, widget_builder)

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        self.path_widget = QtWidgets.QLineEdit()
        self.button_widget = QtWidgets.QPushButton("Browse")
        layout.addWidget(self.path_widget)
        layout.addWidget(self.button_widget)

        self.button_widget.clicked.connect(self._on_clicked)
        self.path_widget.textChanged.connect(self.on_changed)

    def _on_clicked(self, flag):
        path, filter = QtWidgets.QFileDialog.getOpenFileName()
        self.path_widget.setText(path)

    @property
    def state(self):
        return self.path_widget.text()

    @state.setter
    def state(self, state):
        self.path_widget.setText(state)


def is_concrete_schema(schema):
    return "type" in schema


class ArrayWidget(WidgetMixin, QtWidgets.QWidget):

    @property
    def state(self):
        return [w.state for (w, c) in self.rows]

    @state.setter
    def state(self, state):
        raise NotImplementedError

    def handle_error(self, path: Tuple[str], err: Exception):
        index, *tail = path
        widget, controls = self.rows[index]
        widget.handle_error(tail, err)

    def configure(self):
        layout = QtWidgets.QVBoxLayout()
        style = self.style()

        self.add_button = QtWidgets.QPushButton()
        self.add_button.setIcon(style.standardIcon(QtWidgets.QStyle.SP_FileIcon))
        self.add_button.clicked.connect(self.add_item)

        self.array_widget = QtWidgets.QWidget(self)
        array_layout = QtWidgets.QGridLayout()
        self.array_widget.setLayout(array_layout)
        self.on_changed.connect(self._update_add_state)

        layout.addWidget(self.add_button)
        layout.addWidget(self.array_widget)
        self.setLayout(layout)

        self.rows = []

    def _update_add_state(self, _):
        disabled = self.next_item_schema is None
        self.add_button.setEnabled(not disabled)

    @property
    def next_item_schema(self) -> Optional[dict]:
        item_schema = self.schema['items']

        if isinstance(item_schema, dict):
            return item_schema

        index = len(self.rows)

        try:
            item_schema = item_schema[index]
        except IndexError:
            item_schema = self.schema.get("additionalItems", {})
            if isinstance(item_schema, bool):
                return None

        if not is_concrete_schema(item_schema):
            return None

        return item_schema

    def add_item(self, _):
        item_schema = self.schema['items']
        index = len(self.rows)
        print(f"Add after {index} rows")

        if isinstance(item_schema, Sequence):
            try:
                item_schema = item_schema[index]
            except IndexError:
                item_schema = self.schema.get("additionalItems", {})
                if item_schema is False:
                    raise ValueError("No additional fields permitted")
                elif item_schema is True or not is_concrete_schema(item_schema):
                    raise ValueError("Require concrete schema")

        item_ui_schema = self.ui_schema.get("items", {})
        widget = self.widget_builder.create_widget(item_schema, item_ui_schema)
        widget.on_changed.connect(partial(self.widget_on_changed, index))
        controls = self.create_controls(lambda: self.remove_item(row))

        row = widget, controls
        self.rows.append(row)

        row_index = len(self.rows)
        layout = self.array_widget.layout()
        layout.addWidget(widget, row_index, 0)
        layout.addWidget(controls, row_index, 1)

        self.on_changed(self.state)

    @staticmethod
    def create_controls(delete_cb) -> QtWidgets.QWidget:
        item_controls_widget = QtWidgets.QWidget()
        style = item_controls_widget.style()

        up_button = QtWidgets.QPushButton()
        up_button.setIcon(style.standardIcon(QtWidgets.QStyle.SP_ArrowUp))

        delete_button = QtWidgets.QPushButton()
        delete_button.setIcon(style.standardIcon(QtWidgets.QStyle.SP_DialogCancelButton))
        delete_button.clicked.connect(lambda _: delete_cb())

        down_button = QtWidgets.QPushButton()
        down_button.setIcon(style.standardIcon(QtWidgets.QStyle.SP_ArrowDown))

        group_layout = QtWidgets.QHBoxLayout()
        item_controls_widget.setLayout(group_layout)
        group_layout.addWidget(up_button)
        group_layout.addWidget(down_button)
        group_layout.addWidget(delete_button)
        group_layout.setSpacing(0)
        group_layout.addStretch(0)
        return item_controls_widget

    def remove_item(self, row: tuple):
        widget, controls = row
        self.rows.remove(row)

        widget.deleteLater()
        controls.deleteLater()

        self.on_changed(self.state)

    def widget_on_changed(self, index: int, value):
        self.state[index] = value
        self.on_changed(self.state)
