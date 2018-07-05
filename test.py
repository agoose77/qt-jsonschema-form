import sys
from json import dumps

from PyQt5 import QtWidgets

from qt_jsonschema_form import WidgetBuilder

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    wb = WidgetBuilder()
    s = {
        "type": "object",
        "title": "Number fields and widgets",
        "properties": {
            "schema_path": {
                "title": "Schema path",
                "type": "string"
            },
            "integerRangeSteps": {
                "title": "Integer range (by 10)",
                "type": "integer",
                "minimum": 55,
                "maximum": 100,
                "multipleOf": 10
            },
            "sky_colour": {
                "type": "string"
            },
            "names": {
                "type": "array",
                "items": [
                    {
                        "type": "string",
                        "pattern": "[a-zA-Z\-'\s]+",
                        "enum": [
                            "Jack", "Jill"
                        ]
                    },
                    {
                        "type": "string",
                        "pattern": "[a-zA-Z\-'\s]+",
                        "enum": [
                            "Alice", "Bob"
                        ]
                    },
                ],
                "additionalItems": {
                    "type": "number"
                },
            }
        }
    }

    uis = {
        "schema_path": {
            "ui:widget": "filepath"
        },
        "sky_colour": {
            "ui:widget": "colour"
        }

    }
    w = wb.create_form(s, uis)
    w.state = {
        "schema_path": "/home/angus/PycharmProjects/qt-jsonschema-form/qt_jsonschema_form/__pycache__/__init__.cpython-37.pyc",
        "integerRangeSteps": 60,
        "sky_colour": "#8f5902",
        "names": [
            "Jack",
            "Bob"
        ]
    }
    w.show()
    w.on_changed.connect(lambda d: print(dumps(d, indent=4)))

    print(w)
    app.exec_()

