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
                "items": [{
                    "type": "string",
                    "pattern": "[a-zA-Z\-'\s]+"
                },
                    {
                        "type": "string",
                        "pattern": "[a-zA-Z\-'\s]+"
                    }]
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
    w.show()
    w.on_changed.connect(lambda d: print(dumps(d, indent=4)))

    print(w)
    app.exec_()
