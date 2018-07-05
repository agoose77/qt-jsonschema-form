from copy import deepcopy

from jsonschema.validators import validator_for
\
from . import widgets
from .defaults import compute_defaults


def get_widget_state(schema, state=None):
    if state is None:
        return compute_defaults(schema)
    return state


def get_schema_type(schema: dict) -> str:
    return schema['type']


class WidgetBuilder:
    default_widget_map = {
        "boolean": {"checkbox": widgets.CheckboxWidget, "enum": widgets.EnumWidget},
        "object": {"object": widgets.ObjectWidget, "enum": widgets.EnumWidget},
        "number": {"spin": widgets.SpinDoubleWidget, "text": widgets.TextWidget, "enum": widgets.EnumWidget},
        "string": {"textarea": widgets.TextAreaWidget, "text": widgets.TextWidget, "password": widgets.PasswordWidget,
                   "filepath": widgets.FilepathWidget, "colour": widgets.ColorWidget, "enum": widgets.EnumWidget},
        "integer": {"spin": widgets.SpinWidget, "text": widgets.TextWidget, "range": widgets.IntegerRangeWidget,
                    "enum": widgets.EnumWidget},
        "array": {"array": widgets.ArrayWidget, "enum": widgets.EnumWidget}
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

        if "enum" in schema:
            default_variant = "enum"

        widget_variant = ui_schema.get('ui:widget', default_variant)
        widget_cls = self.widget_map[schema_type][widget_variant]

        widget = widget_cls(schema, ui_schema, self)

        default_state = get_widget_state(schema, state)
        if default_state is not None:
            widget.state = default_state
        return widget
