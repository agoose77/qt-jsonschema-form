from copy import deepcopy
from typing import Optional

from . import widgets
from jsonschema.validators import validator_for


# TODO
def compute_defaults(schema):
    if "default" in schema:
        return schema["default"]

    schema_type = schema["type"]

    if schema_type == "object":
        return {k: compute_defaults(s) for k, s in schema["properties"].items()}
    elif schema_type == "array":
        items_schema = schema['items']
        if isinstance(items_schema, dict):
            return []
        return [compute_defaults(s) for s in schema["items"]]

    return None


def get_widget_state(schema, state=None):
    if state is None:
        return compute_defaults(schema)
    return state


def get_schema_type(schema: dict) -> str:
    return schema['type']


class WidgetBuilder:
    default_widget_map = {
        "boolean": {"checkbox": widgets.CheckboxWidget},
        "object": {"object": widgets.ObjectWidget},
        "number": {"spin": widgets.SpinDoubleWidget, "text": widgets.TextWidget},
        "string": {"textarea": widgets.TextAreaWidget, "text": widgets.TextWidget, "password": widgets.PasswordWidget,
                   "filepath": widgets.FilepathWidget, "colour": widgets.ColorWidget},
        "integer": {"spin": widgets.SpinWidget, "text": widgets.TextWidget, "range": widgets.IntegerRangeWidget},
        "array": {"array": widgets.ArrayWidget}
    }

    default_widget_variants = {
        "boolean": "checkbox",
        "object": "object",
        "array": "array",
        "number": "spin",
        "integer": "spin",
        "string": "text",
    }

    widget_variant_modifiers = {
        "string": lambda schema: schema.get("format", "text")
    }

    def __init__(self, validator_cls=None):
        self.widget_map = deepcopy(self.default_widget_map)
        self.validator_cls = validator_cls

    def create_form(self, schema: dict, ui_schema: dict, state=None) -> widgets.WidgetMixin:
        validator_cls = self.validator_cls
        if validator_cls is None:
            validator_cls = validator_for(schema)

        validator_cls.check_schema(schema)
        validator = validator_cls(schema)
        widget = self.create_widget(schema, ui_schema, state)

        def validate(data):
            for err in validator.iter_errors(data):
                widget.handle_error(err.path, err)

        widget.on_changed.connect(validate)

        return widget

    def create_widget(self, schema: dict, ui_schema: dict, state=None) -> widgets.WidgetMixin:
        schema_type = get_schema_type(schema)

        try:
            default_variant = self.widget_variant_modifiers[schema_type](schema)
        except KeyError:
            default_variant = self.default_widget_variants[schema_type]

        widget_variant = ui_schema.get('ui:widget', default_variant)
        widget_cls = self.widget_map[schema_type][widget_variant]

        widget = widget_cls(schema, ui_schema, self)

        default_state = get_widget_state(schema, state)
        if default_state is not None:
            widget.state = default_state
        return widget
