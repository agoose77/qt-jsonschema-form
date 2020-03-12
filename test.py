import sys
from json import dumps

from PyQt5 import QtWidgets

from qt_jsonschema_form import WidgetBuilder

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    builder = WidgetBuilder()

    schema = {
        "type": "object",
        "title": "Number fields and widgets",
        "properties": {
            "schema_path": {
                "title": "Schema path",
                "type": "string"
            },
            "text": {
                "type": "string",
                "maxLength": 20
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
            "boolean": {
                "type": "boolean",

            },
            "enum": {
                "type": "boolean",
                "enum": [True, False]

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

    ui_schema = {
        "schema_path": {
            "ui:widget": "filepath"
        },
        "sky_colour": {
            "ui:widget": "colour"
        },
        "enum": {
            "ui:widget": "enum",
        }

    }
    form = builder.create_form(schema, ui_schema)
    form.widget.state = {
        "schema_path": "some_file.py",
        "integerRangeSteps": 60,
        "sky_colour": "#8f5902",
        "names": [
            "Jack",
            "Bob"
        ]
    }
    form.show()
    form.widget.on_changed.connect(lambda d: print(dumps(d, indent=4)))

    app.exec_()
